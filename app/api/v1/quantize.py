"""
Quantization API endpoints
"""
import json
import os
import uuid
from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.celery_app import celery_app
from app.core.redis_client import redis_client

router = APIRouter()


class QuantizeRequest(BaseModel):
    """Quantization request parameters"""
    width: Optional[int] = Field(default=settings.DEFAULT_WIDTH, ge=50, le=settings.MAX_WIDTH)
    height: Optional[int] = Field(default=settings.DEFAULT_HEIGHT, ge=50, le=settings.MAX_HEIGHT)
    quality: Optional[int] = Field(default=settings.DEFAULT_QUALITY, ge=1, le=10)


class QuantizeResponse(BaseModel):
    """Quantization response"""
    task_id: str
    status: str
    estimated_time: int


@router.post("/", response_model=QuantizeResponse)
async def quantize_image(
    file: UploadFile = File(...),
    width: int = Form(default=settings.DEFAULT_WIDTH, ge=50, le=settings.MAX_WIDTH),
    height: int = Form(default=settings.DEFAULT_HEIGHT, ge=50, le=settings.MAX_HEIGHT),
    quality: int = Form(default=settings.DEFAULT_QUALITY, ge=1, le=10)
):
    """
    Convert image to text using optical quantization

    - **file**: Image file (JPEG, PNG, etc.)
    - **width**: Output width in characters (50-1000)
    - **height**: Output height in characters (50-1000)
    - **quality**: Quality level 1-10 (higher = more colors)
    """
    # Validate parameters
    if width < 50 or width > settings.MAX_WIDTH:
        raise HTTPException(status_code=400, detail=f"Width must be between 50 and {settings.MAX_WIDTH}")
    if height < 50 or height > settings.MAX_HEIGHT:
        raise HTTPException(status_code=400, detail=f"Height must be between 50 and {settings.MAX_HEIGHT}")
    if quality < 1 or quality > 10:
        raise HTTPException(status_code=400, detail="Quality must be between 1 and 10")
    # Validate file
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Generate task ID
    task_id = str(uuid.uuid4())

    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded file
    file_path = upload_dir / f"{task_id}_{file.filename}"

    # Check file size
    file_size = 0
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):
                file_size += len(chunk)
                if file_size > settings.MAX_FILE_SIZE:
                    # Cleanup partial file
                    try:
                        if file_path.exists():
                            file_path.unlink()
                    except (OSError, PermissionError):
                        pass
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
                    )
                await f.write(chunk)
    except (IOError, OSError) as e:
        # Cleanup on write error
        try:
            if file_path.exists():
                file_path.unlink()
        except (OSError, PermissionError):
            pass
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    # Store task info in Redis
    import time
    task_info = {
        "status": "processing",
        "file_path": str(file_path),
        "width": width,
        "height": height,
        "quality": quality,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
    }
    await redis_client.set(f"task:{task_id}", json.dumps(task_info), ex=3600)  # 1 hour expiry

    # Process task asynchronously via Celery
    from app.tasks.celery_tasks import quantize_task
    celery_result = quantize_task.delay(task_id, str(file_path), width, height, quality)

    # Store Celery task ID for cancellation
    task_info["celery_task_id"] = celery_result.id
    await redis_client.set(f"task:{task_id}", json.dumps(task_info), ex=3600)

    # Estimate processing time (rough calculation)
    estimated_time = max(1, int((width * height) / 10000))

    return QuantizeResponse(
        task_id=task_id,
        status="processing",
        estimated_time=estimated_time
    )


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get status of quantization task"""
    task_info_str = await redis_client.get(f"task:{task_id}")

    if not task_info_str:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        task_info = json.loads(task_info_str)
        return {
            "status": task_info.get("status", "processing"),
            "task_id": task_id,
            **({k: v for k, v in task_info.items() if k != "status"})
        }
    except json.JSONDecodeError:
        return {"status": "processing", "task_id": task_id}


@router.post("/cancel/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a quantization task"""
    task_info_str = await redis_client.get(f"task:{task_id}")

    if not task_info_str:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        task_info = json.loads(task_info_str)
        status = task_info.get("status", "processing")

        # Check if task can be cancelled
        if status in ["completed", "error", "cancelled"]:
            raise HTTPException(status_code=400, detail=f"Task is already {status}")

        # Get Celery task ID
        celery_task_id = task_info.get("celery_task_id")
        if celery_task_id:
            # Revoke Celery task
            from app.celery_app import celery_app
            celery_app.control.revoke(celery_task_id, terminate=True)

        # Update task status to cancelled
        task_info["status"] = "cancelled"
        task_info["message"] = "Задача отменена пользователем"
        await redis_client.set(f"task:{task_id}", json.dumps(task_info), ex=3600)

        # Publish cancellation to WebSocket subscribers
        try:
            await redis_client.client.publish(
                f"task:{task_id}:updates",
                json.dumps({
                    "status": "cancelled",
                    "progress": 0,
                    "message": "Задача отменена пользователем"
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

        return {"message": "Task cancelled successfully", "task_id": task_id}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing task info")


@router.get("/result/{task_id}")
async def get_result(task_id: str):
    """Download quantization result"""
    result_dir = Path(settings.RESULT_DIR)
    result_file = result_dir / f"{task_id}.txt"

    if not result_file.exists():
        # Check if task exists
        task_info_str = await redis_client.get(f"task:{task_id}")
        if not task_info_str:
            raise HTTPException(status_code=404, detail="Task not found")

        try:
            task_info = json.loads(task_info_str)
            if task_info.get("status") == "error":
                raise HTTPException(status_code=500, detail=f"Task failed: {task_info.get('error', 'Unknown error')}")
            else:
                raise HTTPException(status_code=202, detail="Task still processing")
        except json.JSONDecodeError:
            raise HTTPException(status_code=202, detail="Task still processing")

    return FileResponse(
        result_file,
        media_type="text/plain; charset=utf-16",
        filename=f"{task_id}.txt",
        headers={
            "Content-Disposition": f'attachment; filename="{task_id}.txt"'
        }
    )

