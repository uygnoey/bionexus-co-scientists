"""Structured logging configuration using structlog."""
import logging
import sys
from typing import Any

import structlog
from structlog.stdlib import BoundLogger

from app.core.config import settings


def configure_logging() -> None:
    """Configure structured logging with structlog."""
    # Determine log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Add appropriate renderer based on environment
    if settings.debug:
        # Pretty console output for development
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Set log level for common noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("neo4j").setLevel(logging.WARNING)


def get_logger(name: str) -> BoundLogger:
    """Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def log_function_call(func_name: str, **kwargs: Any) -> None:
    """Log a function call with parameters.
    
    Args:
        func_name: Function name
        **kwargs: Function parameters to log
    """
    logger = get_logger("function_call")
    logger.info(f"Calling {func_name}", **kwargs)


def log_function_result(func_name: str, result: Any, **kwargs: Any) -> None:
    """Log a function result.
    
    Args:
        func_name: Function name
        result: Function result
        **kwargs: Additional context to log
    """
    logger = get_logger("function_result")
    logger.info(
        f"Function {func_name} completed",
        result_type=type(result).__name__,
        **kwargs,
    )


def log_error(error: Exception, context: dict[str, Any] | None = None) -> None:
    """Log an error with context.
    
    Args:
        error: Exception that occurred
        context: Additional context dict
    """
    logger = get_logger("error")
    logger.error(
        f"Error: {error.__class__.__name__}",
        error_message=str(error),
        **(context or {}),
        exc_info=True,
    )
