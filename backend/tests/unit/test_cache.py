"""Unit tests for Redis cache."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.core.cache import RedisCache, cache_key


@pytest.mark.asyncio
async def test_cache_key_generation():
    """Test cache key generation."""
    key = cache_key("papers", "search", "quantum", "10")
    assert key == "papers:search:quantum:10"


@pytest.mark.asyncio
async def test_cache_get_miss():
    """Test cache miss."""
    cache = RedisCache()
    cache.redis = AsyncMock()
    cache.redis.get = AsyncMock(return_value=None)
    
    result = await cache.get("test_key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_get_hit():
    """Test cache hit."""
    import json
    
    cache = RedisCache()
    cache.redis = AsyncMock()
    cache.redis.get = AsyncMock(return_value=json.dumps({"data": "test"}))
    
    result = await cache.get("test_key")
    assert result == {"data": "test"}


@pytest.mark.asyncio
async def test_cache_set():
    """Test cache set."""
    cache = RedisCache()
    cache.redis = AsyncMock()
    cache.redis.setex = AsyncMock()
    
    result = await cache.set("test_key", {"data": "test"}, ttl=60)
    assert result is True
    cache.redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_cache_delete():
    """Test cache delete."""
    cache = RedisCache()
    cache.redis = AsyncMock()
    cache.redis.delete = AsyncMock(return_value=1)
    
    result = await cache.delete("test_key")
    assert result is True


@pytest.mark.asyncio
async def test_cache_clear_pattern():
    """Test cache clear with pattern."""
    cache = RedisCache()
    cache.redis = AsyncMock()
    cache.redis.keys = AsyncMock(return_value=["key1", "key2"])
    cache.redis.delete = AsyncMock(return_value=2)
    
    result = await cache.clear_pattern("test:*")
    assert result == 2


@pytest.mark.asyncio
async def test_cache_no_redis():
    """Test cache operations when Redis is not connected."""
    cache = RedisCache()
    cache.redis = None
    
    result_get = await cache.get("test")
    result_set = await cache.set("test", "data")
    result_del = await cache.delete("test")
    result_clear = await cache.clear_pattern("test:*")
    
    assert result_get is None
    assert result_set is False
    assert result_del is False
    assert result_clear == 0
