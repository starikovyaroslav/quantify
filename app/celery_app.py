"""
Celery application configuration
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "quanttxt",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.celery_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.TASK_TIMEOUT_SECONDS,  # Hard timeout
    task_soft_time_limit=settings.TASK_SOFT_TIMEOUT_SECONDS,  # Soft timeout
    task_acks_late=True,  # Acknowledge tasks after completion (allows cancellation)
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_routes={
        'app.tasks.quantize_task.process_quantize_task': {'queue': 'quantize'},
    },
)

