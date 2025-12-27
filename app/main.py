"""
FastAPI application entry point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from prometheus_client import generate_latest, REGISTRY
from starlette.responses import Response

from app.api.v1 import router as api_router
from app.core.config import settings
from app.core.metrics import REQUEST_COUNT, REQUEST_DURATION
from app.core.redis_client import redis_client
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.cors_websocket import CORSWebSocketMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await redis_client.connect()
    yield
    # Shutdown
    await redis_client.disconnect()


app = FastAPI(
    title="QuantTxt API",
    description="Оптическое квантование изображений в текст",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS with WebSocket support (added last, so it executes first)
# Must be before rate limiting to handle WebSocket properly
app.add_middleware(
    CORSWebSocketMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (must be added after CORS, so it executes after CORS)
app.add_middleware(RateLimitMiddleware)

# Routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "QuantTxt",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    redis_status = await redis_client.ping()
    return {
        "status": "healthy" if redis_status else "degraded",
        "redis": "connected" if redis_status else "disconnected"
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(REGISTRY), media_type="text/plain")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

