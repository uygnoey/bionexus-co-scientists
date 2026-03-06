"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging, get_logger

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
    
    # TODO: Initialize database connections
    # - Neo4j
    # - Qdrant
    # - Redis
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    
    # TODO: Close database connections
    
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
