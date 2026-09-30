"""
EnviroMap-KG Celery Application Configuration for Distributed Task Queueing.
Integrates Redis message broker to run the LangGraph Multi-Agent pipeline asynchronously.
"""

import os
import logging
from celery import Celery

logger = logging.getLogger("enviromap.celery")

# Read broker and backend URLs from environment, falling back to local Redis defaults
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
BROKER_URL = os.getenv("CELERY_BROKER_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0")
BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", f"redis://{REDIS_HOST}:{REDIS_PORT}/1")

celery_app = Celery(
    "enviromap_orchestrator",
    broker=BROKER_URL,
    backend=BACKEND_URL,
    include=["orchestrator.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_time_limit=300,        # 5-minute hard limit per task
    task_soft_time_limit=240,   # 4-minute soft warning limit
    broker_connection_retry_on_startup=True
)

def is_redis_available() -> bool:
    """Check if the Redis broker is reachable without throwing unhandled exceptions."""
    try:
        import redis
        r = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), socket_connect_timeout=1)
        return r.ping()
    except Exception:
        return False
