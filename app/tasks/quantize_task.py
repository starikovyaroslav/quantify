"""
Quantization background task
"""
import json
import os
from pathlib import Path

import redis
from PIL import Image

from app.core.config import settings
from app.quantizer.quantizer import OpticalQuantizer


def _update_progress(redis_client, task_id: str, progress: int, message: str, status: str = "processing"):
    """Update task progress in Redis and publish to WebSocket subscribers"""
    task_info = {
        "status": status,
        "progress": progress,
        "message": message
    }
    redis_client.set(
        f"task:{task_id}",
        json.dumps(task_info),
        ex=3600
    )
    # Publish update to WebSocket subscribers
    try:
        redis_client.publish(
            f"task:{task_id}:updates",
            json.dumps(task_info)
        )
    except Exception:
        # Ignore publish errors (WebSocket might not be connected)
        pass


def process_quantize_task(
    celery_task,
    task_id: str,
    file_path: str,
    width: int,
    height: int,
    quality: int
):
    """
    Process quantization task (synchronous for Celery)

    Args:
        task_id: Task identifier
        file_path: Path to input image
        width: Target width
        height: Target height
        quality: Quality level
    """
    redis_sync_client = None
    try:
        # Update status (using sync Redis client)
        redis_sync_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )

        _update_progress(redis_sync_client, task_id, 5, "Загрузка изображения...")

        # Check for cancellation
        if celery_task and celery_task.is_aborted():
            raise Exception("Task was cancelled")

        # Load image
        image = Image.open(file_path)
        original_size = image.size

        _update_progress(redis_sync_client, task_id, 15, "Предобработка изображения...")

        # Check for cancellation
        if celery_task and celery_task.is_aborted():
            raise Exception("Task was cancelled")

        # Create quantizer
        quantizer = OpticalQuantizer(width=width, height=height, quality=quality)

        _update_progress(redis_sync_client, task_id, 30, "Квантование цветов...")

        # Check for cancellation
        if celery_task and celery_task.is_aborted():
            raise Exception("Task was cancelled")

        # Quantize with progress updates and error handling
        try:
            text_result = quantizer.quantize(image)
        except Exception as quantize_error:
            error_msg = f"Ошибка квантования: {str(quantize_error)}"
            _update_progress(redis_sync_client, task_id, 0, error_msg, "error")
            raise Exception(error_msg) from quantize_error

        # Check for cancellation
        if celery_task and celery_task.is_aborted():
            raise Exception("Task was cancelled")

        _update_progress(redis_sync_client, task_id, 80, "Сохранение результата...")

        # Create result directory
        result_dir = Path(settings.RESULT_DIR)
        result_dir.mkdir(parents=True, exist_ok=True)

        # Save result
        result_path = result_dir / f"{task_id}.txt"
        quantizer.save_as_utf16(text_result, str(result_path))

        _update_progress(redis_sync_client, task_id, 100, "Готово!", "completed")

        # Final update with result path
        task_info = {
            "status": "completed",
            "progress": 100,
            "message": "Готово!",
            "result_path": str(result_path),
            "original_size": original_size,
            "output_size": (width, height)
        }
        redis_sync_client.set(
            f"task:{task_id}",
            json.dumps(task_info),
            ex=3600
        )
        try:
            redis_sync_client.publish(
                f"task:{task_id}:updates",
                json.dumps(task_info)
            )
        except Exception:
            pass

        # Cleanup uploaded file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except (OSError, PermissionError):
            # Log but don't fail on cleanup errors
            pass

    except Exception as e:
        # Check if it's a cancellation
        error_msg = str(e)
        if "cancelled" in error_msg.lower() or "Task was cancelled" in error_msg:
            # Task was cancelled, status should already be updated
            # Just cleanup files
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except (OSError, PermissionError):
                pass
            return

        # Check if it's a timeout
        is_timeout = "time limit" in error_msg.lower() or "soft time limit" in error_msg.lower() or "timeout" in error_msg.lower()

        # Update status to error
        if redis_sync_client:
            try:
                error_info = {
                    "status": "error",
                    "progress": 0,
                    "message": "Превышено время выполнения" if is_timeout else f"Ошибка: {error_msg}",
                    "error": error_msg
                }
                redis_sync_client.set(
                    f"task:{task_id}",
                    json.dumps(error_info),
                    ex=3600
                )
                try:
                    redis_sync_client.publish(
                        f"task:{task_id}:updates",
                        json.dumps(error_info)
                    )
                except Exception:
                    pass
            except (redis.ConnectionError, redis.TimeoutError):
                # Can't update status, but continue with cleanup
                pass

        # Cleanup on error
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except (OSError, PermissionError):
            # Ignore cleanup errors
            pass
        if redis_sync_client:
            try:
                error_info = {
                    "status": "error",
                    "progress": 0,
                    "message": f"Неожиданная ошибка: {str(e)}",
                    "error": f"Unexpected error: {str(e)}"
                }
                redis_sync_client.set(
                    f"task:{task_id}",
                    json.dumps(error_info),
                    ex=3600
                )
                try:
                    redis_sync_client.publish(
                        f"task:{task_id}:updates",
                        json.dumps(error_info)
                    )
                except Exception:
                    pass
            except Exception:
                pass

