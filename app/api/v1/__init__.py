"""
API v1 routes
"""
from fastapi import APIRouter

from app.api.v1 import gallery, history, quantize, websocket

router = APIRouter()

router.include_router(quantize.router, prefix="/quantize", tags=["quantize"])
router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
router.include_router(gallery.router, prefix="/gallery", tags=["gallery"])
router.include_router(history.router, prefix="/history", tags=["history"])

