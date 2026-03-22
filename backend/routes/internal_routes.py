from datetime import datetime
import json
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from services.redis import redisservices
from services.job import  get_job_status, update_job_status

router = APIRouter()

@router.post("/internal/job-update/{job_id}")
async def receive_job_update(job_id: str, job_update: Dict[Any, Any]):
    # getting update from cloud run
    updated = update_job_status(job_id, job_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # ✅ Get full status
    status = get_job_status(job_id)

    
    # Publish to Redis pubsub so WebSocket picks it up
    await redisservices.publish_message(job_id, {
        "type": "status_update",
        "content": json.dumps(status.model_dump() if status else {}),
        "job_id": job_id,
        "timestamp": datetime.now().isoformat()
    })
        # ✅ Also store in Redis
    if status:
        await redisservices.set_job_status(job_id, status.model_dump())
    
    return {"status": "ok"}