import asyncio
from datetime import datetime
import json
import logging
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, logger
from services.job import get_job_status, schedule_agent_job
from models.agent_model import JobStatusResponse, RunAgentRequest , RunAgentResponse
from services.ws import manager
from services.redis import redisservices
import google.cloud.logging

# init cloud loging client
client = google.cloud.logging.Client()

# route python logs to  cloud loging
client.setup_logging()

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
                        user_message = ({
                            "type":"user_message",
                            "data":message["content"],
                            "timestamp":datetime.now().isoformat()
                        })
                    
                    # send user message to cloud via redis queue
                    await redisservices.add_message_to_queue(job_id=job_id,msg=message)

                    # publish to redis pubsub 
                    await redisservices.publish_message(job_id=job_id,msg=message)

            except WebSocketDisconnect:
              logger.info(f"WebSocket disconnected for job {job_id}")
              logging.info(f"WebSocket disconnected for job {job_id}")

            except Exception as e:
              logger.info(f"Error in websocket listener: {e}")
              logging.info(f"Error in websocket listener: {e}")

        # 2.listen to redis for the messages from cloud
        async def listen_to_redis():
            try:
              # recieve from redis pubsub
              async for redismessage in pubsub.listen():
                 if redismessage.get("type") == "message":
                    data = json.loads(redismessage["data"])

                    # send to websocket
                    await websocket.send_json(data)

                    logger.debug(f"📤 Sent Redis message to WebSocket: {data.get('type')}")
                    logging.debug(f"📤 Sent Redis message to WebSocket: {data.get('type')}")

            except Exception as e:
              logger.error(f"Error in Redis listener: {e}")
              
        # run both task 
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
