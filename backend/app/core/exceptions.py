"""Custom exceptions and error handlers."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger(__name__)


class BioNexusException(Exception):
    """Base exception for BioNexus application."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class PaperNotFoundException(BioNexusException):
    """Raised when paper is not found."""

    def __init__(self, arxiv_id: str):
        super().__init__(
            message=f"Paper {arxiv_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class HypothesisGenerationError(BioNexusException):
    """Raised when hypothesis generation fails."""

    def __init__(self, message: str = "Hypothesis generation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class RateLimitExceeded(BioNexusException):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message=f"Rate limit exceeded. Retry after {retry_after} seconds",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )
        self.retry_after = retry_after


async def bionexus_exception_handler(
    request: Request, exc: BioNexusException
) -> JSONResponse:
    """Handle custom BioNexus exceptions."""
    logger.error(
        f"BioNexus exception: {exc.message}",
        status_code=exc.status_code,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "path": request.url.path,
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(
        f"Validation error: {exc.errors()}",
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": exc.errors(),
            "path": request.url.path,
        },
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.error(
        f"HTTP exception: {exc.detail}",
        status_code=exc.status_code,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP{exc.status_code}",
            "message": exc.detail,
            "path": request.url.path,
        },
    )


async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle uncaught exceptions."""
    logger.error(
        f"Uncaught exception: {str(exc)}",
        exc_info=True,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "path": request.url.path,
        },
    )
