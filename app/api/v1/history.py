"""
History API endpoints
"""
import json
import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.redis_client import redis_client

router = APIRouter()


class HistoryItem(BaseModel):
    """History item model"""
    task_id: str
    status: str
    width: Optional[int] = None
    height: Optional[int] = None
    quality: Optional[int] = None
    created_at: Optional[str] = None
    error: Optional[str] = None


class CancelAllResponse(BaseModel):
    """Response for cancel all operation"""
    cancelled_count: int
    cancelled_tasks: List[str]


@router.get("/", response_model=List[HistoryItem])
async def get_history(limit: int = 50):
    """
    Get quantization history

    - **limit**: Maximum number of items to return (default: 50)
    """
    # Get all task keys from Redis
    # Note: In production, you might want to use a database for this
    # For now, we'll scan Redis keys (this is not efficient for large datasets)

    history = []
    cursor = 0

    # Scan Redis for task keys using the underlying client
    while True:
        cursor, keys = await redis_client.client.scan(cursor, match="task:*", count=100)

        for key in keys:
            try:
                task_info_str = await redis_client.get(key)
                if task_info_str:
                    task_info = json.loads(task_info_str)
                    task_id = key.replace("task:", "")

                    history.append(HistoryItem(
                        task_id=task_id,
                        status=task_info.get("status", "unknown"),
                        width=task_info.get("width"),
                        height=task_info.get("height"),
                        quality=task_info.get("quality"),
                        created_at=task_info.get("created_at"),
                        error=task_info.get("error")
                    ))
            except (json.JSONDecodeError, KeyError):
                continue

        if cursor == 0:
            break

    # Sort by creation time (newest first) and limit
    history.sort(key=lambda x: x.created_at or "", reverse=True)
    return history[:limit]


@router.get("/active", response_model=List[HistoryItem])
async def get_active_tasks():
    """
    Get all active (processing) tasks

    Returns list of tasks with status 'processing'
    """
    active_tasks = []
    cursor = 0

    # Scan Redis for task keys
    while True:
        cursor, keys = await redis_client.client.scan(cursor, match="task:*", count=100)

        for key in keys:
            try:
                task_info_str = await redis_client.get(key)
                if task_info_str:
                    task_info = json.loads(task_info_str)
                    status = task_info.get("status", "unknown")

                    # Only include processing tasks
                    if status == "processing":
                        task_id = key.replace("task:", "")
                        active_tasks.append(HistoryItem(
                            task_id=task_id,
                            status=status,
                            width=task_info.get("width"),
                            height=task_info.get("height"),
                            quality=task_info.get("quality"),
                            created_at=task_info.get("created_at"),
                            error=task_info.get("error")
                        ))
            except (json.JSONDecodeError, KeyError):
                continue

        if cursor == 0:
            break

    # Sort by creation time (newest first)
    active_tasks.sort(key=lambda x: x.created_at or "", reverse=True)
    return active_tasks


@router.post("/cancel-all", response_model=CancelAllResponse)
async def cancel_all_active_tasks():
    """
    Cancel all active (processing) tasks

    Returns count of cancelled tasks and their IDs
    """
    from app.celery_app import celery_app

    cancelled_tasks = []
    cursor = 0

    # Scan Redis for task keys
    while True:
        cursor, keys = await redis_client.client.scan(cursor, match="task:*", count=100)

        for key in keys:
            try:
                task_info_str = await redis_client.get(key)
                if task_info_str:
                    task_info = json.loads(task_info_str)
                    status = task_info.get("status", "unknown")

                    # Only cancel processing tasks
                    if status == "processing":
                        task_id = key.replace("task:", "")

                        # Get Celery task ID
                        celery_task_id = task_info.get("celery_task_id")
                        if celery_task_id:
                            # Revoke Celery task
                            try:
                                celery_app.control.revoke(celery_task_id, terminate=True)
                            except Exception:
                                pass  # Task might already be completed

                        # Update task status to cancelled
                        task_info["status"] = "cancelled"
                        task_info["message"] = "Задача отменена (массовая отмена)"
                        await redis_client.set(key, json.dumps(task_info), ex=3600)

                        # Publish cancellation to WebSocket subscribers
                        try:
                            await redis_client.client.publish(
                                f"task:{task_id}:updates",
                                json.dumps({
                                    "status": "cancelled",
                                    "progress": 0,
                                    "message": "Задача отменена (массовая отмена)"
                                })
                            )
                        except Exception:
                            pass

                        # Cleanup uploaded file if exists
                        file_path = task_info.get("file_path")
                        if file_path:
                            try:
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                            except (OSError, PermissionError):
                                pass

                        cancelled_tasks.append(task_id)
            except (json.JSONDecodeError, KeyError):
                continue

        if cursor == 0:
            break

    return CancelAllResponse(
        cancelled_count=len(cancelled_tasks),
        cancelled_tasks=cancelled_tasks
    )

