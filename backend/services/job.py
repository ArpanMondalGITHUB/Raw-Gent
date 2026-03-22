import json
import os
from typing import Any, Dict
from google.oauth2 import service_account
import uuid
from datetime import datetime
from google.cloud import run_v2
from models.agent_model import FileChange, JobStatus, JobStatusResponse, RoleType, RunAgentRequest , AgentMessage
from core.config import BACKEND_URL,GCP_PROJECT_ID,GCP_REGION,CLOUD_RUN_JOB, REDIS_URL
from services.github_app_service import mint_installation_token

# In-memory storage for results
job_results : Dict[str, JobStatusResponse] = {}

async def schedule_agent_job(payload:RunAgentRequest):
    installation_access_token = await mint_installation_token(str(payload.installation_id))
    credentials = None
    if os.getenv("GOOGLE_CLOUD_KEY_JSON"):
        try:
          creds_dict = json.loads(os.getenv("GOOGLE_CLOUD_KEY_JSON"))
          credentials = service_account.Credentials.from_service_account_info(creds_dict)
          print("🔐 Loaded Google Cloud credentials successfully.")
        except Exception as e:
          print("❌ ERROR loading GCP credentials:", e)

    if credentials:
       client = run_v2.JobsClient(credentials=credentials)
    else:
        print("⚠ No GCP credentials found. Using default creds (will fail on Render).")
        client = run_v2.JobsClient()

    job_name = f"projects/{GCP_PROJECT_ID}/locations/{GCP_REGION}/jobs/{CLOUD_RUN_JOB}"
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # ✅ Initialize job result storage with proper schema
    job_results[job_id] = JobStatusResponse(
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


    request = run_v2.RunJobRequest(
        name = job_name,
        overrides = run_v2.RunJobRequest.Overrides(
            container_overrides = [
                run_v2.RunJobRequest.Overrides.ContainerOverride(
                    env = [
                        run_v2.EnvVar(name="PROMPT", value=payload.prompt),
                        run_v2.EnvVar(name="REPO", value=payload.repo_name),
                        run_v2.EnvVar(name="BRANCH", value=payload.branches),
                        run_v2.EnvVar(name="TOKEN", value=installation_access_token),
                        run_v2.EnvVar(name="JOB_ID", value=job_id),  # ← NEW
                        run_v2.EnvVar(name="BACKEND_URL", value=BACKEND_URL),  # ← NEW
                        run_v2.EnvVar(name="REDIS_URL", value=REDIS_URL),
                    ]
                )
            ]
        )
    )

    operation = client.run_job(request=request)
    response = operation.result()
    return job_id

def update_job_status(job_id: str, update: Dict[Any, Any]) -> bool:
    if job_id not in job_results:
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