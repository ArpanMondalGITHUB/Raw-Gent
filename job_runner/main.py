from datetime import datetime
import json
import os
import re
import subprocess
import tempfile
from typing import List
from Raw_Gent.main_agent import root_agent
import logging
import sys
import asyncio
import shutil
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from job_runner_models import AgentMessage, FileChange, JobStatus, JobUpdate, RoleType
import redis.asyncio as redis
import ssl
from google.auth.exceptions import DefaultCredentialsError

try:
    import google.cloud.logging
except Exception:  # pragma: no cover - optional in local runs
    google = None


def _get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _build_cloud_logger():
    if google is None:
        return None

    try:
        client = google.cloud.logging.Client()
        client.setup_logging()
        return client.logger("agent-job")
    except (DefaultCredentialsError, Exception):
        return None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

cloud_logger = _build_cloud_logger()


def log_cloud_text(message: str, severity: str = "INFO"):
    if cloud_logger is not None:
        cloud_logger.log_text(message, severity=severity)


def _looks_like_edit_request(prompt: str) -> bool:
    normalized = prompt.lower()
    edit_target_pattern = (
        r"(?:file|files|class|classes|function|functions|module|modules|method|methods|"
        r"component|components|route|routes|endpoint|endpoints|handler|handlers|"
        r"test|tests|test case|test cases|suite|line|lines|snippet|snippets|config|dockerfile|workflow)"
    )
    explicit_command_patterns = (
        rf"\b(?:create|add|update|modify|edit|delete|remove|rename|refactor|write|implement|fix)\s+"
        rf"(?:a\s+|an\s+|the\s+)?(?:new\s+)?{edit_target_pattern}\b",
        r"\b(?:create|add|write|update|modify|edit)\s+(?:a\s+|an\s+|the\s+)?test(?: case| suite| file)?\b",
        r"\b(?:create file|add file|update file|modify file|write file|edit function|modify function|add test)\b",
        r"\b(?:create|add|update|modify|edit|delete|remove|rename|refactor|write|fix)\s+[`'\"]?[\w./-]+\.(?:py|ts|tsx|js|jsx|json|md|yml|yaml|css|html|sh)[`'\"]?\b",
    )
    return any(re.search(pattern, normalized) for pattern in explicit_command_patterns)


def _claims_file_changes(response_text: str) -> bool:
    normalized = response_text.lower()
    patterns = (
        r"\b(?:created|added|updated|modified|edited|deleted|removed|saved|wrote)\s+"
        r"(?:the\s+)?(?:file|files|function|functions|module|modules|class|classes|test|tests|component|components)\b",
        r"\b(?:created|added|updated|modified|edited|deleted|removed|saved|wrote)\s+"
        r"[`'\"]?[\w./-]+\.(?:py|ts|tsx|js|jsx|json|md|yml|yaml|css|html|sh)[`'\"]?\b",
        r"\b(?:created file|added file|updated file|modified file|saved file|created test|added test)\b",
    )
    return any(re.search(pattern, normalized) for pattern in patterns)


def _append_unverified_change_warning(
    messages: List[AgentMessage],
    prompt: str,
    response_text: str,
    file_changes: List[FileChange],
) -> List[AgentMessage]:
    if file_changes:
        return messages

    if not (_looks_like_edit_request(prompt) or _claims_file_changes(response_text)):
        return messages

    warning = AgentMessage(
        role=RoleType.AGENT,
        content=(
            "No repository file changes were actually detected for this run. "
            "Treat any claim about creating or updating files as unverified."
        ),
        timestamp=datetime.now().isoformat(),
    )

    return [*messages, warning]


def _should_fail_for_missing_changes(
    prompt: str,
    response_text: str,
    file_changes: List[FileChange],
) -> bool:
    if file_changes:
        return False

    return _looks_like_edit_request(prompt) or _claims_file_changes(response_text)

# Redis client for cloud run
redis_client:redis.Redis = None

async def init_redis():
    """Initialize Redis connection with SSL support"""
    global redis_client
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_ssl_verify = _get_bool_env("REDIS_SSL_VERIFY", redis_url.startswith("rediss://"))
    try:
        # ✅ Handle SSL (rediss://) URLs properly
        if redis_url.startswith("rediss://"):
            redis_client = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                ssl_cert_reqs=ssl.CERT_REQUIRED if redis_ssl_verify else ssl.CERT_NONE,
                ssl_check_hostname=redis_ssl_verify
            )
        else:
            redis_client = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        
        # Test connection
        await redis_client.ping()
        logging.info("✅ Connected to Redis")
    except Exception as e:
        logging.error(f"❌ Failed to connect to Redis: {e}")
        raise

async def poll_for_user_messages(job_id: str) -> dict:
    """
    Poll Redis queue for user messages (blocking)
    Returns message or None after timeout
    """
    queue_key = f"job:{job_id}:queue"
    
    try:
        # Block for 5 seconds waiting for message
        result = await redis_client.blpop(queue_key, timeout=5)
        
        if result:
            _, message_json = result
            message = json.loads(message_json)
            logging.info(f"📨 Got user message: {message.get('content')}")
            return message
            
    except Exception as e:
        logging.error(f"Error polling queue: {e}")
        await asyncio.sleep(2)
    
    return None

async def send_agent_response_to_redis(job_id: str, message: dict):
    """Send agent response via Redis pub/sub"""
    channel = f"job:{job_id}:updates"
    await redis_client.publish(channel, json.dumps(message))
    logging.info(f"📤 Published agent response to Redis")

    
async def send_job_update(job_id: str, update: JobUpdate) -> None:
    """Send update via Redis pub/sub only (no HTTP)"""
    try:
        channel = f"job:{job_id}:updates"
        update_payload = update.model_dump(mode="json", exclude_none=False)
        existing_status_raw = await redis_client.get(f"job:{job_id}:status")
        existing_status = json.loads(existing_status_raw) if existing_status_raw else {}
        merged_status = {
            **existing_status,
            **update_payload,
            "job_id": existing_status.get("job_id", job_id),
        }
        merged_status = {key: value for key, value in merged_status.items() if value is not None}
        merged_status["updated_at"] = datetime.now().isoformat()
        
        # Convert update to dict
        message = {
            "type": "status_update",
            "content": json.dumps(merged_status),
            "job_id": job_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Publish to Redis
        await redis_client.publish(channel, json.dumps(message))
        await redis_client.set(f"job:{job_id}:status", json.dumps(merged_status), ex=86400)
        logging.info(f"✅ Published status update to Redis: {update.status}")
        
    except Exception as e:
        logging.error(f"❌ Failed to publish update: {e}")


async def run_agent_async(prompt: str, repo: str, branch: str, token: str, temp_dir: str , conversation_history: list):
    """
    Run the agent with proper session state management.
    Sets repo_path in session state so all tools and sub-agents can access it.
    """
    APP_NAME = "raw_gent_agent"
    USER_ID = "job_runner"
    SESSION_ID = f"{repo}_{branch}_{os.getpid()}"
    job_id = os.environ.get("JOB_ID")
    os.environ["REPO_PATH"] = temp_dir

    # ✅ Load conversation history
    messages: List[AgentMessage] = []
    for msg in conversation_history:
        messages.append(AgentMessage(
            role=RoleType(msg["role"]),
            content=msg["content"],
            timestamp=msg["timestamp"]
        ))
    
    # ✅ Add current user message
    messages.append(AgentMessage(
        role=RoleType.USER,
        content=prompt,
        timestamp=datetime.now().isoformat()
    ))

    logging.info("Initializing agent session")
    # Create session service and runner
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    logging.info("Initializing agent session successfull updating through job_update")

    # ✅ Initial update with full history
    await send_job_update(job_id=job_id, update=JobUpdate(
        status=JobStatus.RUNNING,
        current_step="Initializing agent session",
        messages=messages
    ))

    
    # Set repo_path in session state before running agent
    session.state['repo_path'] = temp_dir
    session.state['repo'] = repo
    session.state['branch'] = branch
    session.state['github_token'] = token
    
    logging.info("Creating Runner")
    # Create runner
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    logging.info("Created Runner Successfully")
    # ✅ Build context with conversation history
    context_prompt = prompt
    if conversation_history:
        context_prompt = "Previous conversation:\n"
        for msg in conversation_history:
            context_prompt += f"{msg['role']}: {msg['content']}\n"
        context_prompt += f"\nCurrent request: {prompt}"
    
    # Create user message content
    content = types.Content(
        role='user',
        parts=[types.Part(text=context_prompt)]
    )
    
    # Run the agent
    msg = f"🎯 Starting agent execution for session: {SESSION_ID} with {len(conversation_history)} previous messages"
    logging.info(msg)
    log_cloud_text(msg, severity='INFO')
    print(msg)
    

    # ✅ START polling for user messages in background
    async def poll_and_respond():
        """Background task to poll for user messages and respond"""
        while True:
            user_msg = await poll_for_user_messages(job_id)
            if not user_msg:
                continue
                
            if user_msg.get("type") == "user_message":
                logging.info(f"💬 Processing user message: {user_msg.get('content')[:100]}")
                messages.append(AgentMessage(
                    role=RoleType.USER,
                    content=user_msg["content"],
                    timestamp=user_msg.get("timestamp", datetime.now().isoformat())
                ))

                await send_job_update(job_id=job_id, update=JobUpdate(
                    status=JobStatus.RUNNING,
                    messages=messages,
                    current_step="Processing follow-up request..."
                ))
                
                # Process user message
                user_content = types.Content(
                    role='user',
                    parts=[types.Part(text=user_msg["content"])]
                )
                
                # Run agent with user message
                agent_events = runner.run_async(
                    user_id=USER_ID,
                    session_id=SESSION_ID,
                    new_message=user_content
                )
                
                async for event in agent_events:
                    if event.is_final_response():
                        response_text = event.content.parts[0].text if event.content.parts else ""
                        messages.append(AgentMessage(
                            role=RoleType.AGENT,
                            content=response_text,
                            timestamp=datetime.now().isoformat()
                        ))
                        
                        logging.info(f"🤖 Agent response: {response_text[:100]}")

                        file_changes: List[FileChange] = await collect_file_changes(temp_dir)
                        messages_with_verification = _append_unverified_change_warning(
                            messages,
                            user_msg["content"],
                            response_text,
                            file_changes,
                        )
                        should_fail = _should_fail_for_missing_changes(
                            user_msg["content"],
                            response_text,
                            file_changes,
                        )
                        await send_job_update(job_id=job_id, update=JobUpdate(
                            status=JobStatus.FAILED if should_fail else JobStatus.COMPLETED,
                            messages=messages_with_verification,
                            file_changes=file_changes,
                            current_step="No verified file changes were produced." if should_fail else "Done!",
                            error=(
                                "The run was expected to create or update repository files, "
                                "but no verified file changes were detected."
                                if should_fail
                                else None
                            ),
                        ))
    
    polling_task: asyncio.Task | None = None

    try:
        # ✅ Process initial agent response
        events = runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content
        )
        
        # Process events
        async for event in events:
            if event.is_final_response():
                response_text = event.content.parts[0].text if event.content.parts else ""
                messages.append(AgentMessage(
                    role=RoleType.AGENT,
                    content=response_text,
                    timestamp=datetime.now().isoformat()
                ))

                await send_job_update(job_id=job_id, update=JobUpdate(
                    status=JobStatus.RUNNING,
                    messages=messages,
                    current_step="Processing..."
                ))
                
                msg = f"📝 Agent initial response: {response_text}"
                logging.info(msg)
                log_cloud_text(msg, severity='INFO')
        
        # ✅ Collect file changes
        file_changes: List[FileChange] = await collect_file_changes(temp_dir)
        final_response_text = messages[-1].content if messages and messages[-1].role == RoleType.AGENT else ""
        messages_with_verification = _append_unverified_change_warning(
            messages,
            prompt,
            final_response_text,
            file_changes,
        )
        should_fail = _should_fail_for_missing_changes(
            prompt,
            final_response_text,
            file_changes,
        )

        # ✅ Send completion update
        await send_job_update(job_id=job_id, update=JobUpdate(
            status=JobStatus.FAILED if should_fail else JobStatus.COMPLETED,
            messages=messages_with_verification,
            file_changes=file_changes,
            current_step="No verified file changes were produced." if should_fail else "Done!",
            error=(
                "The run was expected to create or update repository files, "
                "but no verified file changes were detected."
                if should_fail
                else None
            ),
        ))
        
        msg = "✅ Agent initial workflow finished, now listening for follow-ups..."
        logging.info(msg)
        log_cloud_text(msg, severity='INFO')

        # Start polling only after the initial runner invocation completes.
        polling_task = asyncio.create_task(poll_and_respond())
        
        # ✅ Wait for polling task or timeout
        try:
            await asyncio.wait_for(polling_task, timeout=600)  # 10 minutes
        except asyncio.TimeoutError:
            logging.info("⏱️ Polling timeout reached ")
    finally:
        if polling_task is not None:
            polling_task.cancel()
            try:
                await polling_task
            except asyncio.CancelledError:
                pass


async def collect_file_changes(temp_dir: str) -> List[FileChange]:
    """
    Detect what files were changed by the agent
    
    Args:
        temp_dir: Path to cloned repository
        
    Returns:
        List of FileChange objects with modified files
    """
    file_changes: List[FileChange] = []
    
    try:
        # Use porcelain status so untracked new files also appear in the UI.
        result = await asyncio.to_thread(
            subprocess.run,
            ["git", "status", "--porcelain"],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )
        
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            if len(line) < 4:
                continue

            status = line[:2]
            file_path = line[3:].strip()
            if " -> " in file_path:
                file_path = file_path.split(" -> ", 1)[1].strip()

            if status == "??" or "A" in status:
                change_type = "created"
            elif "D" in status:
                change_type = "deleted"
            else:
                change_type = "modified"
            
            full_path = os.path.join(temp_dir, file_path)
            
            # Read file content
            modified_content = ""
            original_content = None
            
            if change_type == 'deleted':
                # For deleted files, get content from git
                try:
                    git_result = await asyncio.to_thread(
                        subprocess.run,
                        ["git", "show", f"HEAD:{file_path}"],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        check=False,
                    )
                    original_content = git_result.stdout
                except Exception:
                    original_content = ""
            else:
                # For created/modified files
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        modified_content = f.read()
                
                # Get original content for modified files
                if change_type == 'modified':
                    try:
                        git_result = await asyncio.to_thread(
                            subprocess.run,
                            ["git", "show", f"HEAD:{file_path}"],
                            cwd=temp_dir,
                            capture_output=True,
                            text=True,
                            timeout=10,
                            check=False,
                        )
                        original_content = git_result.stdout
                    except Exception:
                        original_content = None
            
            # Detect language
            language = detect_language(file_path)
            
            # ✅ Create typed FileChange object
            file_changes.append(FileChange(
                file_path=file_path,
                original_content=original_content,
                modified_content=modified_content,
                change_type=change_type,
                language=language
            ))
    
    except Exception as e:
        logging.error(f"❌ Failed to collect file changes: {e}")
    
    return file_changes


def detect_language(file_path: str) -> str:
    """
    Detect programming language from file extension
    
    Args:
        file_path: Path to the file
        
    Returns:
        Language identifier for syntax highlighting
    """
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.md': 'markdown',
        '.json': 'json',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.html': 'html',
        '.css': 'css',
        '.sh': 'bash',
    }
    ext = os.path.splitext(file_path)[1]
    return ext_map.get(ext, 'plaintext')

def main():
    prompt = os.environ["PROMPT"]
    repo = os.environ["REPO"]
    branch = os.environ["BRANCH"]
    token = os.environ["TOKEN"]

    # ✅ Load conversation history from environment
    conversation_history_json = os.environ.get("CONVERSATION_HISTORY", "[]")
    try:
        conversation_history = json.loads(conversation_history_json)
    except json.JSONDecodeError:
        conversation_history = []

    temp_dir = None
    temp_dir = tempfile.mkdtemp()
    clone_url = f"https://x-access-token:{token}@github.com/{repo}.git"

    logging.info(f"Starting agent job for repo: {repo}, branch: {branch}")

        # ✅ Log with both methods
    msg = f"🚀 Starting agent job for repo: {repo}, branch: {branch}"
    logging.info(msg)
    log_cloud_text(msg, severity='INFO')
    print(msg)  # Also print to stdout

    try:
        subprocess.run([
           "git", "clone", "--depth", "1", "-b", branch,
            clone_url, temp_dir
        ], check=True,capture_output=True,text=True,timeout=300)
        msg = "✅ Repository cloned successfully"
        logging.info(msg)
        log_cloud_text(msg, severity='INFO')
        print(msg)
        logging.info("Repository clone successfully") 
    except FileNotFoundError:
        logging.critical("❌ Git not found in container. Install it in Dockerfile.")
        msg = "❌ Git not found in container"
        logging.critical(msg)
        log_cloud_text(msg, severity='ERROR')
        print(msg)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logging.error(f"Git clone failed with code {e.returncode}\n"
            f"STDOUT: {e.stdout}\nSTDERR: {e.stderr}")
        sys.exit(1)
    except subprocess.TimeoutExpired as e:
        logging.info(f"❌ Git clone timed out after {e.timeout} seconds.")
        sys.exit(1)
    except Exception as e:
        logging.info("Unexpected error occured")
        sys.exit(1)

    try:
        msg = "🤖 Running root agent workflow..."
        logging.info(msg)
        log_cloud_text(msg, severity='INFO')
        
        # ✅ Initialize Redis and run agent
        async def run_with_redis():
            await init_redis()
            try:
                await run_agent_async(prompt, repo, branch, token, temp_dir, conversation_history)
            finally:
                if redis_client:
                    await redis_client.close()
                    logging.info("✅ Redis connection closed")
        
        asyncio.run(run_with_redis())
        
        logging.info("✅ Agent workflow finished successfully")
    except Exception as e:
        logging.exception("Agent run failed")
        msg = f"❌ Agent run failed: {str(e)}"
        logging.exception(msg)
        log_cloud_text(msg, severity='ERROR')
        print(msg)
        sys.exit(1)
    finally:
        # Cleanup temp dir after agent completes
        if temp_dir and os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            logging.info("🧹 Cleaned up temporary directory.")

if __name__ == "__main__":
    main()
