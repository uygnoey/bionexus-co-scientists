"""Rate limiting middleware."""
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import time

from app.core.cache import cache, cache_key
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Rate limiter using Redis."""

    def __init__(
        self,
        requests_per_minute: int = settings.rate_limit_per_minute,
    ) -> None:
        """Initialize rate limiter.
        
        Args:
            requests_per_minute: Max requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.window = 60  # 1 minute in seconds

    async def check_rate_limit(self, client_id: str) -> tuple[bool, int]:
        """Check if client has exceeded rate limit.
        
        Args:
            client_id: Client identifier (IP address)
            
        Returns:
            (is_allowed, remaining_requests)
        """
        key = cache_key("rate_limit", client_id)
        
        # Get current count
        current = await cache.get(key)
        
        if current is None:
            # First request in window
            await cache.set(key, 1, ttl=self.window)
            return True, self.requests_per_minute - 1
        
        count = int(current)
        
        if count >= self.requests_per_minute:
            # Rate limit exceeded
            logger.warning(f"Rate limit exceeded for {client_id}")
            return False, 0
        
        # Increment count
        await cache.redis.incr(key)
        return True, self.requests_per_minute - count - 1


# Global rate limiter
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """Rate limiting middleware.
    
    Args:
        request: FastAPI request
        call_next: Next middleware/route
        
    Returns:
        Response
    """
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    # Check rate limit
    is_allowed, remaining = await rate_limiter.check_rate_limit(client_ip)
    
    if not is_allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {settings.rate_limit_per_minute}/min",
                "retry_after": 60,
            },
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": str(settings.rate_limit_per_minute),
                "X-RateLimit-Remaining": "0",
            },
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response
