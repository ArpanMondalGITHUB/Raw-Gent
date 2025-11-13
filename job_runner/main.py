import os
import subprocess
import tempfile
from backend.Raw_Gent.main_agent import root_agent
import logging
import google.cloud.logging
import sys
import asyncio
import shutil
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# init cloud loging client
client = google.cloud.logging.Client()

# route python logs to  cloud loging
client.setup_logging()

async def run_agent_async(prompt: str, repo: str, branch: str, token: str, temp_dir: str):
    """
    Run the agent with proper session state management.
    Sets repo_path in session state so all tools and sub-agents can access it.
    """
    APP_NAME = "raw_gent_agent"
    USER_ID = "job_runner"
    SESSION_ID = f"{repo}_{branch}_{os.getpid()}"
    
    # Create session service and runner
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    # Set repo_path in session state before running agent
    session.state['repo_path'] = temp_dir
    session.state['repo'] = repo
    session.state['branch'] = branch
    session.state['github_token'] = token
    
    # Save the session with updated state
    await session_service.update_session(session)
    
    # Create runner
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    # Create user message content
    content = types.Content(
        role='user',
        parts=[types.Part(text=prompt)]
    )
    
    # Run the agent
    logging.info(f"Starting agent execution for session: {SESSION_ID}")
    events = runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    )
    
    # Process events
    async for event in events:
        if event.is_final_response():
            response_text = event.content.parts[0].text if event.content.parts else ""
            logging.info(f"Agent final response: {response_text[:200]}...")  # Log first 200 chars
    
    logging.info("✅ Agent workflow finished successfully.")

def main():
    prompt = os.environ["PROMPT"]
    repo = os.environ["REPO"]
    branch = os.environ["BRANCH"]
    token = os.environ["TOKEN"]

    temp_dir = None
    temp_dir = tempfile.mkdtemp()
    clone_url = f"https://x-access-token:{token}@github.com/{repo}.git"

    logging.info(f"Starting agent job for repo: {repo}, branch: {branch}")

    try:
        subprocess.run([
           "git", "clone", "--depth", "1", "-b", branch,
            clone_url, temp_dir
        ], check=True,capture_output=True,text=True,timeout=300)
        logging.info("Repository clone successfully") 
    except FileNotFoundError:
        logging.critical("❌ Git not found in container. Install it in Dockerfile.")
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
        logging.info("Running root agent workflow...")
        # Run the async agent function
        asyncio.run(run_agent_async(prompt, repo, branch, token, temp_dir))
        logging.info("✅ Agent workflow finished successfully.")
    except Exception as e:
        logging.exception("Agent run failed")
        sys.exit(1)
    finally:
        # Cleanup temp dir after agent completes
        if temp_dir and os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            logging.info("🧹 Cleaned up temporary directory.")
