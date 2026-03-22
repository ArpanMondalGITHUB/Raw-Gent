import asyncio
from datetime import datetime
import logging
from typing import Dict, List
from fastapi import WebSocket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


class JobConnectionManager:
    """
    Docstring for JobConnectionManger
    1.Accept all connection in one place
    2.track the lifesycle
    3.handle background task

    """
    def __init__(self, heartbeat_timeout:int=60, heartbeat_interval:int=10):
        """
        Args:
            heartbeat_interval: sets interval between every ping messages (10 seconds)
            heartbeat_timeout: seconds between dead connections (60 seconds)
        """

        # storing every connctions
        self.active_connections:Dict[str,List[WebSocket]] = {}
        
        # store the last heartbeat for connection
        self.last_heartbeat:Dict[str,float] = {}

        # run background task for for check connection
        self.heartbeat_task:Dict[str,asyncio.Task] = {}

        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout

        self._lock = asyncio.Lock()

        # start background task to monitor connections
        self.monitor_task = asyncio.create_task(self._monitor_connection())

    async def connect(self,websocket:WebSocket,job_id:str):
        """
        accept all the connections

        """
        try:
            # accept connections
            await websocket.accept()

            # store all the connections in connections list
            async with self._lock:
                if job_id not in self.active_connections:
                    self.active_connections[job_id] = []
                self.active_connections[job_id].append(websocket)

            # start the heartbeat
            connection_key = (job_id,websocket)
            self.last_heartbeat[connection_key] = asyncio.get_event_loop().time()

            # start the hearbeat background task
            heartbeat_background_task = asyncio.create_task(
                self._heartbeat_send(websocket,job_id)
            )
            self.heartbeat_task[connection_key] = heartbeat_background_task
            
        except Exception as e:
            logging.error(f"❌ Error connecting to job {job_id}: {e}")
            logger.error(f"❌ Error connecting to job {job_id}: {e}")
            raise

    async def disconnect(self,websocket:WebSocket,job_id:str):
        """remove connections and cleanup resourses"""
        try:
           async with self._lock:
              # Remove from active connections
              if job_id in self.active_connections:
                 if websocket in self.active_connections:
                    self.active_connections[job_id].remove(websocket)
            # Remove job entry if no more connections
                 if not self.active_connections[job_id]:
                    del self.active_connections[job_id]

            # Clean up heartbeat tracking
              connection_key = (job_id,websocket)
              if connection_key in self.last_heartbeat:
                 del self.last_heartbeat[connection_key]
              if connection_key in self.heartbeat_task:
                 self.heartbeat_task[connection_key].cancel()
                 del self.heartbeat_task[connection_key]
           logging.info(f"🔌 WebSocket disconnected from job {job_id}")
           logger.info(f"🔌 WebSocket disconnected from job {job_id}")
        except Exception as e:
          logging.error(f"🔌 WebSocket not disconnected from job {job_id}")
          logger.error(f"🔌 WebSocket not disconnected from job {job_id}")

    async def _heartbeat_send(self,websocket:WebSocket,job_id:str):
        try:
          while True:
              await asyncio.sleep(self.heartbeat_interval)
              try:
                await websocket.send_json({
                   "type":"ping",
                   "timestamp":datetime.now().isoformat()
                })
                logging.debug(f"💓 Sent ping to job {job_id}")
                logger.debug(f"💓 Sent ping to job {job_id}")
              except Exception as e:
                logging.warning(f"💔 Heartbeat failed for job {job_id}: {e}")
                logger.warning(f"💔 Heartbeat failed for job {job_id}: {e}")
                break
        except asyncio.CancelledError:
          logging.debug(f"Heartbeat cancelled for job {job_id}")
          logger.debug(f"Heartbeat cancelled for job {job_id}")

    async def _monitor_connection(self):
       """ monitor all the dead connections """
       try:
         while True:
            await asyncio.sleep(10)
            current_time = asyncio.get_event_loop().time()
            dead_connections = []

            # find connections that are not responding
            async with self._lock:
               for (job_id,websocket) , last_beat in list(self.last_heartbeat.items()):
                  if current_time - last_beat > self.heartbeat_timeout:
                     dead_connections.append((job_id,websocket))

            # cleanup dead connections
            for job_id , websocket in dead_connections:
               logging.warning({
                  f"⚠️ Connection for job {job_id} timed out "
                  f"(no response for {self.heartbeat_timeout}s)"
               })
               logger.warning({
                  f"⚠️ Connection for job {job_id} timed out "
                  f"(no response for {self.heartbeat_timeout}s)"
               })
               await self.disconnect(websocket=websocket,job_id=job_id)

       except asyncio.CancelledError:
         logging.info("Connection monitor stopped")
         logger.info("Connection monitor stopped")

    async def update_heartbeat(self, websocket: WebSocket, job_id: str):
        """Update heartbeat timestamp when client sends pong"""
        connection_key = (job_id, websocket)
        if connection_key in self.last_heartbeat:
            self.last_heartbeat[connection_key] = asyncio.get_event_loop().time()
            logging.debug(f"💚 Received pong from job {job_id}")
            logger.debug(f"💚 Received pong from job {job_id}")

    def get_job_connections(self, job_id: str) -> int:
        """Get number of active connections for a job"""
        return len(self.active_connections.get(job_id, []))
    
    def get_all_jobs(self) -> List[str]:
        """Get list of all jobs with active connections"""
        return list(self.active_connections.keys())
    
    def get_total_connections(self) -> int:
        """Get total number of active connections across all jobs"""
        return sum(len(conns) for conns in self.active_connections.values())
    
    async def shutdown(self):
       """ shutdown all connections """
       logging.info("🛑 Shutting down WebSocket manager...")
       logger.info("🛑 Shutting down WebSocket manager...")

     # cancel monitor
       self.monitor_task.cancel()

     # cancel all heartbeat task
       for task in self.heartbeat_task.values():
          task.cancel()

     # Close all connections

       for job_id, connections in list(self.active_connections.items()):
          for websocket in connections:
             try:
                await websocket.close()
             except:
               pass
             await self.disconnect(websocket, job_id)

       logging.info("✅ WebSocket manager shutdown complete")
       logger.info("✅ WebSocket manager shutdown complete")

# Global manager instance
manager = JobConnectionManager(
    heartbeat_interval=30,  # Ping every 30 seconds
    heartbeat_timeout=60    # Consider dead after 60 seconds
)       