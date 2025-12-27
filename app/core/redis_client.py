"""
Redis client singleton
"""
import redis.asyncio as redis

from app.core.config import settings


class RedisClient:
    """Async Redis client"""

    def __init__(self):
        self.client: redis.Redis = None

    async def connect(self):
        """Connect to Redis"""
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
        )

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.aclose()

    async def ping(self) -> bool:
        """Check Redis connection"""
        try:
            if self.client:
                await self.client.ping()
                return True
        except (redis.ConnectionError, redis.TimeoutError, AttributeError):
            pass
        return False

    async def get(self, key: str):
        """Get value from Redis"""
        if self.client:
            return await self.client.get(key)
        return None

    async def set(self, key: str, value: str, ex: int = None):
        """Set value in Redis"""
        if self.client:
            await self.client.set(key, value, ex=ex)

    async def incr(self, key: str):
        """Increment key"""
        if self.client:
            return await self.client.incr(key)
        return 0

    async def expire(self, key: str, seconds: int):
        """Set expiration on key"""
        if self.client:
            await self.client.expire(key, seconds)

    async def scan(self, cursor: int = 0, match: str = None, count: int = None):
        """Scan Redis keys"""
        if self.client:
            return await self.client.scan(cursor, match=match, count=count)
        return (0, [])

    async def delete(self, key: str):
        """Delete key from Redis"""
        if self.client:
            await self.client.delete(key)

    async def publish(self, channel: str, message: str):
        """Publish message to channel"""
        if self.client:
            await self.client.publish(channel, message)


redis_client = RedisClient()

