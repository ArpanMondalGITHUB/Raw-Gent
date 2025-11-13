from fastapi import APIRouter
from services.job import schedule_agent_job
from models.agent_model import AgentRunRequest

router = APIRouter()

@router.post("/agent/run")
async def run_agent(payload: AgentRunRequest):
    job_id = await  schedule_agent_job(payload)
    return {"job_id": job_id, "status": "queued"}