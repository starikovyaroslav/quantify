"""
WebSocket endpoints for real-time task updates
"""
import json
import logging
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from app.core.config import settings

router = APIRouter()

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

logger = logging.getLogger(__name__)


async def get_redis_client() -> Redis:
    """Get async Redis client"""
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
        decode_responses=True
    )


@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time task status updates

    Args:
        websocket: WebSocket connection
        task_id: Task identifier to monitor
    """
    logger.info(f"WebSocket connection attempt for task_id: {task_id}")
    try:
        # Accept WebSocket connection first
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for task_id: {task_id}")
        active_connections[task_id] = websocket
    except Exception as e:
        logger.error(f"Failed to accept WebSocket connection for task_id {task_id}: {e}")
        raise

    try:
        redis_client = await get_redis_client()

        # Subscribe to task updates
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(f"task:{task_id}:updates")

        # Send initial status
        task_info_str = await redis_client.get(f"task:{task_id}")
        if task_info_str:
            try:
                task_info = json.loads(task_info_str)
                await websocket.send_json({
                    "type": "status",
                    "data": {
                        "status": task_info.get("status", "processing"),
                        "progress": task_info.get("progress", 0),
                        "message": task_info.get("message", "Обработка...")
                    }
                })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "status",
                    "data": {"status": "processing", "progress": 0, "message": "Обработка..."}
                })

        # Listen for updates
        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    try:
                        data = json.loads(message["data"])
                        await websocket.send_json({
                            "type": "update",
                            "data": data
                        })

                        # Close connection if task is completed or failed
                        if data.get("status") in ["completed", "error"]:
                            break
                    except (json.JSONDecodeError, KeyError):
                        continue

                # Also check Redis for status updates (fallback)
                task_info_str = await redis_client.get(f"task:{task_id}")
                if task_info_str:
                    try:
                        task_info = json.loads(task_info_str)
                        status = task_info.get("status", "processing")
                        if status in ["completed", "error"]:
                            await websocket.send_json({
                                "type": "status",
                                "data": {
                                    "status": status,
                                    "progress": 100 if status == "completed" else task_info.get("progress", 0),
                                    "message": task_info.get("message", "Завершено" if status == "completed" else "Ошибка"),
                                    "error": task_info.get("error") if status == "error" else None
                                }
                            })
                            break
                    except json.JSONDecodeError:
                        pass

            except Exception as e:
                # Log error but continue
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"Ошибка соединения: {str(e)}"}
                })
                break

        await pubsub.unsubscribe(f"task:{task_id}:updates")
        await pubsub.close()
        await redis_client.close()

    except WebSocketDisconnect:
        pass
    except Exception as e:
        # Send error and close
        try:
            await websocket.send_json({
                "type": "error",
                "data": {"message": f"Ошибка: {str(e)}"}
            })
        except:
            pass
    finally:
        # Cleanup
        if task_id in active_connections:
            del active_connections[task_id]
        try:
            await websocket.close()
        except:
            pass

