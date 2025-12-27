"""
Celery task definitions
"""
from app.celery_app import celery_app
from app.core.config import settings
from app.tasks.quantize_task import process_quantize_task


@celery_app.task(name='app.tasks.quantize_task.process_quantize_task', bind=True)
def quantize_task(self, task_id: str, file_path: str, width: int, height: int, quality: int):
    """
    Celery task wrapper for quantization with cancellation support

    Args:
        self: Celery task instance (bind=True)
        task_id: Task identifier
        file_path: Path to input image
        width: Target width
        height: Target height
        quality: Quality level
    """
    # Check if task was revoked/cancelled
    if self.is_aborted():
        import redis as redis_sync
        import json
        redis_sync_client = redis_sync.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )
        try:
            task_info = {
                "status": "cancelled",
                "progress": 0,
                "message": "Задача отменена"
            }
            redis_sync_client.set(
                f"task:{task_id}",
                json.dumps(task_info),
                ex=3600
            )
            redis_sync_client.publish(
                f"task:{task_id}:updates",
                json.dumps(task_info)
            )
        except Exception:
            pass
        raise Exception("Task was cancelled")

    return process_quantize_task(self, task_id, file_path, width, height, quality)




