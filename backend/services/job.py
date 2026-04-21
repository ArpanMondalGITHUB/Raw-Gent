import asyncio
import json
import logging
import os
from typing import Any, Dict
from google.oauth2 import service_account
import uuid
from datetime import datetime
from google.cloud import run_v2
from models.agent_model import FileChange, JobStatus, JobStatusResponse, RoleType, RunAgentRequest , AgentMessage
from core.config import (
    BACKEND_URL,
    CLOUD_RUN_JOB,
    GCP_PROJECT_ID,
    GCP_REGION,
    JOB_QUEUE_NAME,
    JOB_RUNNER_MODE,
    REDIS_SSL_VERIFY,
    REDIS_URL,
)
from services.github_app_service import mint_installation_token
from services.redis import redisservices

# In-memory storage for results
job_results : Dict[str, JobStatusResponse] = {}
logger = logging.getLogger(__name__)


def _build_initial_job_status(job_id: str, payload: RunAgentRequest) -> JobStatusResponse:
    return JobStatusResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        messages=[
            AgentMessage(
                role=RoleType.AGENT,
                content=f"Task queued: {payload.prompt}",
                timestamp=datetime.now().isoformat()
            )
        ],
        file_changes=[],
        current_step="Waiting to start...",
        error=None,
        created_at=datetime.now().isoformat(),
        updated_at=None
    )


def _build_job_payload(
    payload: RunAgentRequest,
    job_id: str,
    installation_access_token: str,
) -> dict:
    return {
        "job_id": job_id,
        "prompt": payload.prompt,
        "repo": payload.repo_name,
        "branch": payload.branches,
        "token": installation_access_token,
        "conversation_history": [],
    }


def _build_cloud_run_client() -> run_v2.JobsClient:
    credentials = None
    if os.getenv("GOOGLE_CLOUD_KEY_JSON"):
        try:
            creds_dict = json.loads(os.getenv("GOOGLE_CLOUD_KEY_JSON"))
            credentials = service_account.Credentials.from_service_account_info(creds_dict)
            logger.info("Loaded Google Cloud credentials successfully.")
        except Exception as exc:
            logger.error(f"Failed to load Google Cloud credentials: {exc}")

    if credentials:
        return run_v2.JobsClient(credentials=credentials)

    logger.warning("No explicit GCP credentials found. Falling back to default credentials.")
    return run_v2.JobsClient()


def _run_cloud_run_job(client: run_v2.JobsClient, request: run_v2.RunJobRequest) -> None:
    operation = client.run_job(request=request)
    operation.result()


async def _schedule_cloud_run_job(job_payload: dict) -> None:
    client = _build_cloud_run_client()
    job_name = f"projects/{GCP_PROJECT_ID}/locations/{GCP_REGION}/jobs/{CLOUD_RUN_JOB}"

    request = run_v2.RunJobRequest(
        name=job_name,
        overrides=run_v2.RunJobRequest.Overrides(
            container_overrides=[
                run_v2.RunJobRequest.Overrides.ContainerOverride(
                    env=[
                        run_v2.EnvVar(name="PROMPT", value=job_payload["prompt"]),
                        run_v2.EnvVar(name="REPO", value=job_payload["repo"]),
                        run_v2.EnvVar(name="BRANCH", value=job_payload["branch"]),
                        run_v2.EnvVar(name="TOKEN", value=job_payload["token"]),
                        run_v2.EnvVar(name="JOB_ID", value=job_payload["job_id"]),
                        run_v2.EnvVar(name="BACKEND_URL", value=BACKEND_URL or ""),
                        run_v2.EnvVar(name="REDIS_URL", value=REDIS_URL),
                        run_v2.EnvVar(name="REDIS_SSL_VERIFY", value=str(REDIS_SSL_VERIFY).lower()),
                    ]
                )
            ]
        )
    )

    await asyncio.to_thread(_run_cloud_run_job, client, request)


async def _enqueue_local_job(job_payload: dict) -> None:
    await redisservices.push_json(JOB_QUEUE_NAME, job_payload)
    logger.info(f"Queued local worker job {job_payload['job_id']} on {JOB_QUEUE_NAME}")

async def schedule_agent_job(payload:RunAgentRequest):
    installation_access_token = await mint_installation_token(str(payload.installation_id))
    job_id = str(uuid.uuid4())
    job_results[job_id] = _build_initial_job_status(job_id, payload)
    await redisservices.set_job_status(job_id, job_results[job_id].model_dump(mode="json"))
    job_payload = _build_job_payload(payload, job_id, installation_access_token)

    try:
        if JOB_RUNNER_MODE in {"docker", "local"}:
            await _enqueue_local_job(job_payload)
        elif JOB_RUNNER_MODE == "cloud_run":
            await _schedule_cloud_run_job(job_payload)
        else:
            raise ValueError(f"Unsupported JOB_RUNNER_MODE: {JOB_RUNNER_MODE}")
    except Exception as exc:
        update_job_status(job_id, {
            "status": JobStatus.FAILED.value,
            "current_step": "Failed to start job",
            "error": str(exc),
        })
        current_status = get_job_status(job_id)
        if current_status:
            await redisservices.set_job_status(job_id, current_status.model_dump(mode="json"))
        raise

    return job_id

def update_job_status(job_id: str, update: Dict[Any, Any]) -> bool:
    if job_id not in job_results:
        if "created_at" in update:
            job_results[job_id] = JobStatusResponse(**update)
            return True
        return False  # Job doesn't exist
    
    # ✅ Get the stored JobStatusResponse
    current: JobStatusResponse = job_results[job_id]
    
    # ✅ Update it with new data from Cloud Run
    if "status" in update:
        current.status = JobStatus(update["status"])
    
    if "messages" in update:
        current.messages = [AgentMessage(**msg) for msg in update["messages"]]
    
    if "file_changes" in update:
        current.file_changes = [FileChange(**fc) for fc in update["file_changes"]]
    
    if "current_step" in update:
        current.current_step = update["current_step"]
    
    if "error" in update:
        current.error = update["error"]
    
    current.updated_at = datetime.now().isoformat()
    
    # ✅ Store updated status back
    job_results[job_id] = current
    
    return True


def get_job_status(job_id: str) -> JobStatusResponse | None:
    """Get current job status"""
    return job_results.get(job_id)
