"""
Gallery API endpoints
"""
import json
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from app.core.config import settings
from app.core.redis_client import redis_client

router = APIRouter()


class GalleryItem(BaseModel):
    """Gallery item model"""
    task_id: str
    filename: str
    created_at: str
    width: Optional[int] = None
    height: Optional[int] = None
    quality: Optional[int] = None
    status: str


@router.get("/", response_model=List[GalleryItem])
async def list_gallery_items(limit: int = 50, offset: int = 0):
    """
    List all quantization results (gallery items) including active tasks

    - **limit**: Maximum number of items to return (default: 50)
    - **offset**: Number of items to skip (default: 0)
    """
    result_dir = Path(settings.RESULT_DIR)
    result_dir.mkdir(parents=True, exist_ok=True)

    items = []
    task_ids_seen = set()

    # First, get all result files
    result_files = sorted(result_dir.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)

    for result_file in result_files:
        task_id = result_file.stem
        task_ids_seen.add(task_id)

        # Try to get task info from Redis
        task_info_str = await redis_client.get(f"task:{task_id}")
        task_info = {}
        if task_info_str:
            try:
                task_info = json.loads(task_info_str)
            except json.JSONDecodeError:
                pass

        # Get file stats
        stat = result_file.stat()

        items.append(GalleryItem(
            task_id=task_id,
            filename=result_file.name,
            created_at=str(int(stat.st_mtime)),  # Unix timestamp as string
            width=task_info.get("width"),
            height=task_info.get("height"),
            quality=task_info.get("quality"),
            status=task_info.get("status", "completed")
        ))

    # Also get active tasks from Redis (tasks that don't have result files yet)
    try:
        # Scan Redis for all task keys
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor, match="task:*", count=100)
            for key in keys:
                # Extract task_id from key (format: "task:{task_id}")
                if key.startswith("task:"):
                    task_id = key[5:]  # Remove "task:" prefix

                    # Skip if we already have this task (it has a result file)
                    if task_id in task_ids_seen:
                        continue

                    # Get task info
                    task_info_str = await redis_client.get(key)
                    if task_info_str:
                        try:
                            task_info = json.loads(task_info_str)
                            status = task_info.get("status", "processing")

                            # Only include active/processing tasks
                            if status in ["processing", "pending", "started"]:
                                items.append(GalleryItem(
                                    task_id=task_id,
                                    filename=f"{task_id}.txt (обработка...)",
                                    created_at=str(int(task_info.get("created_at", 0))),
                                    width=task_info.get("width"),
                                    height=task_info.get("height"),
                                    quality=task_info.get("quality"),
                                    status=status
                                ))
                        except json.JSONDecodeError:
                            pass

            if cursor == 0:
                break
    except Exception as e:
        # Log error but continue
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error scanning Redis for active tasks: {e}")

    # Sort by created_at (most recent first)
    items.sort(key=lambda x: int(x.created_at) if x.created_at.isdigit() else 0, reverse=True)

    # Apply limit and offset
    return items[offset:offset + limit]


@router.get("/{task_id}/preview")
async def preview_result(task_id: str, max_lines: int = 50):
    """
    Preview quantization result (first N lines)

    - **task_id**: Task identifier
    - **max_lines**: Maximum number of lines to return (default: 50)
    """
    result_dir = Path(settings.RESULT_DIR)
    result_file = result_dir / f"{task_id}.txt"

    if not result_file.exists():
        raise HTTPException(status_code=404, detail="Result not found")

    try:
        # Read first N lines
        with open(result_file, 'r', encoding='utf-16-le') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                lines.append(line.rstrip('\n\r'))

            preview_text = '\n'.join(lines)

            return Response(
                content=preview_text,
                media_type="text/plain; charset=utf-8"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@router.get("/{task_id}/download")
async def download_result(task_id: str):
    """
    Download quantization result

    - **task_id**: Task identifier
    """
    result_dir = Path(settings.RESULT_DIR)
    result_file = result_dir / f"{task_id}.txt"

    if not result_file.exists():
        raise HTTPException(status_code=404, detail="Result not found")

    return FileResponse(
        result_file,
        media_type="text/plain; charset=utf-16",
        filename=f"{task_id}.txt",
        headers={
            "Content-Disposition": f'attachment; filename="{task_id}.txt"'
        }
    )


@router.delete("/{task_id}")
async def delete_result(task_id: str):
    """
    Delete quantization result or cancel active task

    - **task_id**: Task identifier
    """
    result_dir = Path(settings.RESULT_DIR)
    result_file = result_dir / f"{task_id}.txt"

    # Check if task is active in Redis
    task_info_str = await redis_client.get(f"task:{task_id}")
    task_info = {}
    if task_info_str:
        try:
            task_info = json.loads(task_info_str)
        except json.JSONDecodeError:
            pass

    # If task is active, try to cancel it
    status = task_info.get("status", "unknown")
    if status in ["processing", "pending", "started"]:
        # Try to cancel the Celery task
        try:
            from celery.result import AsyncResult
            from app.celery_app import celery_app

            task = AsyncResult(task_id, app=celery_app)
            if task.state in ['PENDING', 'STARTED', 'RETRY']:
                task.revoke(terminate=True, signal='SIGKILL')

                # Update Redis status to cancelled
                cancelled_info = {
                    "status": "cancelled",
                    "progress": 0,
                    "message": "Задача отменена"
                }
                await redis_client.set(f"task:{task_id}", json.dumps(cancelled_info), ex=3600)
                await redis_client.publish(f"task:{task_id}:updates", json.dumps(cancelled_info))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error cancelling task {task_id}: {e}")

    # Delete result file if exists
    if result_file.exists():
        try:
            result_file.unlink()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

    # Delete from Redis
    await redis_client.delete(f"task:{task_id}")

    return {"message": "Result deleted successfully" if result_file.exists() else "Task cancelled successfully"}

