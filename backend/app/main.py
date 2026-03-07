"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.cache import cache
from app.core.rate_limit import rate_limit_middleware
from app.core.exceptions import (
    BioNexusException,
    bionexus_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configure logging on startup
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None during application lifetime
    """
    # Startup
    logger.info(
        "Starting BioNexus Co-scientists Backend",
        version=settings.app_version,
        debug=settings.debug,
    )
    
    # Initialize Redis cache
    await cache.connect()
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    
    # Disconnect Redis cache
    await cache.disconnect()
    
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered scientific hypothesis generation using multi-agent debate",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
if settings.allow_all_origins:
    # For Tailscale/development: allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Can't use credentials with allow_origins=*
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Production: specific origins only + Tailscale pattern
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=r"https?://100\.[0-9]+\.[0-9]+\.[0-9]+(:[0-9]+)?",  # Tailscale IPs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Add exception handlers
app.add_exception_handler(BioNexusException, bionexus_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug,
        }
    )


@app.get("/", tags=["Root"])
async def root() -> JSONResponse:
    """Root endpoint with API info.
    
    Returns:
        JSON response with API information
    """
    return JSONResponse(
        content={
            "message": "BioNexus Co-scientists API",
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
        }
    )


# Add routers
from app.api import papers, hypotheses, websocket

app.include_router(papers.router, prefix="/api/papers", tags=["Papers"])
app.include_router(hypotheses.router, prefix="/api/hypotheses", tags=["Hypotheses"])
app.include_router(websocket.router, tags=["WebSocket"])


if __name__ == "__main__":
    import uvicorn

    # 0.0.0.0으로 바인딩하여 Tailscale 접속 허용
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # 모든 인터페이스에서 접근 가능
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
