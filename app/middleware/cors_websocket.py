"""
Custom CORS middleware that supports WebSocket
WebSocket connections bypass CORS completely
"""
import logging
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send

logger = logging.getLogger(__name__)


class CORSWebSocketMiddleware:
    """
    CORS middleware that properly handles WebSocket connections
    WebSocket paths bypass CORS completely
    """
    def __init__(self, app: ASGIApp, **kwargs):
        # Store original app for WebSocket passthrough
        self.original_app = app
        # Store CORS kwargs
        self.cors_kwargs = kwargs

        # Create CORS middleware for HTTP requests only
        self.cors_middleware = CORSMiddleware(app, **kwargs)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Check if this is a WebSocket connection - bypass CORS completely
        scope_type = scope.get("type")
        path = scope.get("path", "")

        # WebSocket connections bypass CORS completely
        if scope_type == "websocket":
            logger.info(f"WebSocket connection detected: {path}, bypassing CORS")
            await self.original_app(scope, receive, send)
            return

        # Check for WebSocket upgrade requests (HTTP with Upgrade header)
        if scope_type == "http":
            headers_list = scope.get("headers", [])
            headers_dict = {k.decode("utf-8").lower(): v.decode("utf-8") for k, v in headers_list}
            upgrade_header = headers_dict.get("upgrade", "").lower()
            connection_header = headers_dict.get("connection", "").lower()

            # Check if it's a WebSocket path or upgrade request
            if path.startswith("/api/v1/ws/") or upgrade_header == "websocket" or "upgrade" in connection_header:
                logger.info(f"WebSocket upgrade request detected: {path}, bypassing CORS")
                await self.original_app(scope, receive, send)
                return

        # For regular HTTP requests, use standard CORS middleware
        await self.cors_middleware(scope, receive, send)

