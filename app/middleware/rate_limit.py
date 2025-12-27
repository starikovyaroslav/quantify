"""
Rate limiting middleware
"""
import time

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import Scope, Receive, Send

from app.core.config import settings
from app.core.metrics import REQUEST_COUNT, REQUEST_DURATION
from app.core.redis_client import redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Skip WebSocket connections entirely - they use different protocol
        if scope.get("type") == "websocket":
            # Pass WebSocket directly to the app without rate limiting
            # Don't process WebSocket through rate limiting middleware
            await self.app(scope, receive, send)
            return

        # For HTTP requests, use the standard BaseHTTPMiddleware behavior
        await super().__call__(scope, receive, send)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        endpoint = request.url.path

        # Skip rate limiting for health checks, metrics, and WebSocket connections
        # WebSocket connections are handled separately in __call__
        if endpoint in ["/", "/health", "/docs", "/openapi.json", "/metrics"] or endpoint.startswith("/api/v1/ws/"):
            response = await call_next(request)
            duration = time.time() - start_time
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
            status = response.status_code
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
            return response

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        minute_key = f"rate_limit:minute:{client_ip}"
        hour_key = f"rate_limit:hour:{client_ip}"

        # Check per-minute limit
        minute_count = await redis_client.incr(minute_key)
        if minute_count == 1:
            await redis_client.expire(minute_key, 60)

        if minute_count > settings.RATE_LIMIT_PER_MINUTE:
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=429).inc()
            return Response(
                content='{"detail": "Rate limit exceeded. Maximum 100 requests per minute."}',
                status_code=429,
                media_type="application/json"
            )

        # Check per-hour limit
        hour_count = await redis_client.incr(hour_key)
        if hour_count == 1:
            await redis_client.expire(hour_key, 3600)

        if hour_count > settings.RATE_LIMIT_PER_HOUR:
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=429).inc()
            return Response(
                content='{"detail": "Rate limit exceeded. Maximum 1000 requests per hour."}',
                status_code=429,
                media_type="application/json"
            )

        # Process request
        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()

        return response
