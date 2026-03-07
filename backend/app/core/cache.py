"""Redis caching utilities."""
import json
from typing import Any, Optional
import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedisCache:
    """Redis cache manager."""

    def __init__(self) -> None:
        """Initialize Redis cache."""
        self.redis: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis.ping()
            logger.info("Redis cache connected")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.redis = None

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis cache disconnected")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.redis:
            return None

        try:
            value = await self.redis.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
    ) -> bool:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        if not self.redis:
            return False

        try:
            await self.redis.setex(
                key,
                ttl,
                json.dumps(value),
            )
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted
        """
        if not self.redis:
            return False

        try:
            result = await self.redis.delete(key)
            logger.debug(f"Cache delete: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "papers:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.redis:
            return 0

        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Cleared {deleted} keys matching {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0


# Global cache instance
cache = RedisCache()


def cache_key(*args: str) -> str:
    """Generate cache key from arguments.
    
    Args:
        *args: Key components
        
    Returns:
        Cache key string
    """
    return ":".join(args)
