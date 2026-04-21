import asyncio
from datetime import datetime
import json
import logging
import os
import sys
from typing import Any

import redis.asyncio as redis
import ssl


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def _get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_queue_name() -> str:
    value = os.getenv("JOB_QUEUE_NAME")
    if value and value.strip():
        return value.strip()

    return "agent_jobs:queue"


async def create_redis_client() -> redis.Redis:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_ssl_verify = _get_bool_env("REDIS_SSL_VERIFY", False)

    options: dict[str, Any] = {
        "encoding": "utf-8",
        "decode_responses": True,
    }

    if redis_url.startswith("rediss://"):
        options["ssl_cert_reqs"] = ssl.CERT_REQUIRED if redis_ssl_verify else ssl.CERT_NONE
        options["ssl_check_hostname"] = redis_ssl_verify

    client = redis.from_url(redis_url, **options)
    await client.ping()
    return client


async def publish_failed_status(redis_client: redis.Redis, job_id: str, error: str):
    update_payload = {
        "status": "failed",
        "current_step": "Worker failed",
        "error": error,
        "messages": [
            {
                "role": "agent",
                "content": "Agent job failed before completion. Check worker logs.",
                "timestamp": datetime.now().isoformat(),
            }
        ],
    }

    existing_status_raw = await redis_client.get(f"job:{job_id}:status")
    existing_status = json.loads(existing_status_raw) if existing_status_raw else {}
    merged_status = {
        **existing_status,
        **update_payload,
        "job_id": existing_status.get("job_id", job_id),
        "updated_at": datetime.now().isoformat(),
    }

    message = {
        "type": "status_update",
        "content": json.dumps(merged_status),
        "job_id": job_id,
        "timestamp": datetime.now().isoformat(),
    }

    await redis_client.publish(f"job:{job_id}:updates", json.dumps(message))
    await redis_client.set(f"job:{job_id}:status", json.dumps(merged_status), ex=86400)


async def run_job(redis_client: redis.Redis, job: dict):
    job_id = job["job_id"]
    timeout_seconds = int(os.getenv("JOB_RUNNER_TIMEOUT", "3600"))
    env = os.environ.copy()
    env.update(
        {
            "PROMPT": job["prompt"],
            "REPO": job["repo"],
            "BRANCH": job["branch"],
            "TOKEN": job["token"],
            "JOB_ID": job_id,
            "CONVERSATION_HISTORY": json.dumps(job.get("conversation_history", [])),
        }
    )

    logger.info(f"Starting local worker job {job_id}")
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "main.py",
        cwd=os.path.dirname(__file__),
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        process.kill()
        stdout_bytes, stderr_bytes = await process.communicate()
        stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
        stderr = stderr_bytes.decode("utf-8", errors="replace").strip()
        error = stderr or stdout or f"job_runner main.py timed out after {timeout_seconds} seconds"
        logger.error(f"Job {job_id} failed: {error}")
        await publish_failed_status(redis_client, job_id, error)
        return
    except asyncio.CancelledError:
        process.kill()
        await process.communicate()
        raise

    stdout = stdout_bytes.decode("utf-8", errors="replace")
    stderr = stderr_bytes.decode("utf-8", errors="replace")

    if process.returncode != 0:
        error = stderr.strip() or stdout.strip() or "job_runner main.py exited with a non-zero code"
        logger.error(f"Job {job_id} failed: {error}")
        await publish_failed_status(redis_client, job_id, error)
        return

    logger.info(f"Completed local worker job {job_id}")


async def main():
    queue_name = _get_queue_name()
    redis_client = await create_redis_client()
    logger.info(f"Local worker is listening on {queue_name}")

    try:
        while True:
            result = await redis_client.blpop(queue_name, timeout=5)
            if not result:
                continue

            _, raw_job = result
            job = json.loads(raw_job)
            try:
                await run_job(redis_client, job)
            except Exception as exc:
                job_id = job.get("job_id", "unknown")
                logger.exception(f"Unexpected worker failure for {job_id}: {exc}")
                if job_id != "unknown":
                    await publish_failed_status(redis_client, job_id, str(exc))
    finally:
        await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())
