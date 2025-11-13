import uuid
from datetime import datetime
from google.cloud import run_v2
from models.agent_model import AgentRunRequest
from core.config import BACKEND_URL,GCP_PROJECT_ID,GCP_REGION,CLOUD_RUN_JOB
from services.github_app_service import mint_installation_token

# In-memory storage for results
job_results = {}

async def schedule_agent_job(payload:AgentRunRequest):
    installation_access_token = await mint_installation_token(str(payload.installation_id))
    client = run_v2.JobsClient()

    job_name = f"projects/{GCP_PROJECT_ID}/locations/{GCP_REGION}/jobs/{CLOUD_RUN_JOB}"
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job result storage
    job_results[job_id] = {
        "status": "queued",
        "final_response": None,
        "prompt": payload.prompt,
        "repo": payload.repo_name,
        "branch": payload.branches,
        "code_changes": {...},
        "created_at": datetime.now().isoformat(),
        "updated_at": None
    }

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
                    ]
                )
            ]
        )
    )

    operation = client.run_job(request=request)
    response = operation.result()
    return job_id 
