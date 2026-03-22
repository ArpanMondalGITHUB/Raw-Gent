import json
import logging
from typing import Optional
import google.cloud.logging
import redis.asyncio as redis
from core.config import REDIS_URL
client = google.cloud.logging.Client()

client.setup_logging()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

class RedisServices:
    """"""
    def __init__(self):
        self.redis:Optional[redis.Redis] = None

    async def connect(self):
        """ connect with redis service """
        self.redis = await redis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("✅ Connected to Redis")
        logging.info("✅ Connected to Redis")

    async def disconnect(self):
        """ disconnect the redis service """
        if self.redis:
            await self.redis.close()
            logger.info("❌ Disconnected from Redis")
            logging.info("❌ Disconnected from Redis")

    async def publish_message(self,job_id:str,msg:dict):
        """ publish message to the job's channel for websocket broadcasting """
        channel = f"job:{job_id}:updates"
        await self.redis.publish(channel=channel,message=json.dumps(msg))
        logger.debug(f"📤 Published to {channel}")
        logging.debug(f"📤 Published to {channel}")

    async def subscribe_to_job(self,job_id:str):
        """subscribe to job's updates channel"""
        channel = f"job:{job_id}:updates"
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        logger.info(f"pubsub:{pubsub}")
        logging.info(f"pubsub:{pubsub}")
        return pubsub
        
    
    async def add_message_to_queue(self,job_id:str,msg:dict):
        """ add messages to the queue for cloud """
        key = f"job:{job_id}:queue"
        await self.redis.rpush(name=key,values=json.dumps(msg))
        logger.debug(f"📥 Added to queue {key}")
        logging.debug(f"📥 Added to queue {key}")

    async def get_message_from_queue(self,job_id,timeout:int=5):
        """ get the messages from cloud queue """
        key = f"job:{job_id}:queue"
        result = await self.redis.blpop(keys=key,timeout=timeout)
        if result:
            _, message_json = result
            return json.loads(message_json)
        return None
    
    async def set_job_status(self, job_id: str, status: dict):
        """Store job status in Redis"""
        key = f"job:{job_id}:status"
        await self.redis.set(key, json.dumps(status), ex=86400)  # 24h expiry
    
    async def get_job_status(self, job_id: str):
        """Get job status from Redis"""
        key = f"job:{job_id}:status"
        result = await self.redis.get(key)
        return json.loads(result) if result else None
    
redisservices = RedisServices()