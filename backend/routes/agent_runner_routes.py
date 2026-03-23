import asyncio
from datetime import datetime
import json
import logging
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from services.job import get_job_status, schedule_agent_job, update_job_status
from models.agent_model import JobStatusResponse, RunAgentRequest , RunAgentResponse
from services.ws import manager
from services.redis import redisservices

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/agent/run" , response_model=RunAgentResponse)
async def run_agent(payload: RunAgentRequest)->RunAgentResponse:
    job_id = await  schedule_agent_job(payload)
    return RunAgentResponse(job_id=job_id,status="queued")

@router.get("/agent/status/{job_id}",response_model = JobStatusResponse)
def get_agent_status(job_id:str)->JobStatusResponse:
    status = get_job_status(job_id=job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status

@router.websocket("/ws/status/{job_id}")
async def websocket_handler(websocket:WebSocket,job_id:str):
    # connect the 
    await manager.connect(websocket=websocket,job_id=job_id)

    # subscribe to redis
    pubsub = await redisservices.subscribe_to_job(job_id=job_id)

    try:
        # send initial status 
        status = get_job_status(job_id=job_id)
        if status:
            await websocket.send_json({
                "type":"status_update",
                "data":status.dict(),
                "timestamp":datetime.now().isoformat()
            })
        
        #  run two jobs parallel
        
        # 1.listen to websocket
        async def listen_to_websocket():
            try:
                while True:
                    # recieve text
                    data = await websocket.receive_text()
                    # make it json
                    message = json.loads(data)

                    # evaluate message type

                    # Handle pong
                    if message.get("type") == "pong":
                        await manager.update_heartbeat(websocket=websocket,job_id=job_id)
                    # Handle usermessage
                    elif message.get("type") == "user_message":
                         # send user message to cloud via redis queue
                        await redisservices.add_message_to_queue(job_id=job_id,msg=message)

            except WebSocketDisconnect:
              logger.info(f"WebSocket disconnected for job {job_id}")
              logging.info(f"WebSocket disconnected for job {job_id}")

            except Exception as e:
              logger.info(f"Error in websocket listener: {e}")
              logging.info(f"Error in websocket listener: {e}")

        # 2.listen to redis for the messages from cloud
        async def listen_to_redis():
            try:
                async for redis_message in pubsub.listen():
                    if redis_message.get("type") == "message":
                        data = json.loads(redis_message["data"])
                        
                        # ✅ Update job status if it's a status update
                        if data.get("type") == "status_update":
                            try:
                                status_data = json.loads(data["content"])
                                update_job_status(job_id, status_data)
                                logger.debug(f"📊 Updated job status: {status_data.get('status')}")
                            except Exception as e:
                                logger.error(f"❌ Failed to update status: {e}")
                        
                        # ✅ Forward ALL messages to WebSocket client
                        await websocket.send_json(data)
                        logger.debug(f"📤 Sent to WebSocket: {data.get('type')}")

            except Exception as e:
                logger.error(f"❌ Error in Redis listener: {e}")
              
        # run both task in parallel
        await asyncio.gather(
           listen_to_websocket(),
           listen_to_redis()
        )

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from job {job_id}")
        
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {e}")
        
    finally:
        # Cleanup
        await manager.disconnect(websocket, job_id)
        await pubsub.unsubscribe()
        await pubsub.close()
