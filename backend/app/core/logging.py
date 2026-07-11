"""Structured logging via structlog.

Emits JSON logs in production and colored console logs in development.
Provides a `log_timing` context manager used across agents/sources to
record execution latency uniformly.
"""
import logging
import sys
import time
from contextlib import contextmanager

import structlog

from app.core.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(stream=sys.stdout, level=level, format="%(message)s")

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    renderer = (
        structlog.processors.JSONRenderer()
        if settings.app_env == "production"
        else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


@contextmanager
def log_timing(logger: structlog.stdlib.BoundLogger, operation: str, **context):
    """Log start/end/latency (and failures) of an operation."""
    start = time.perf_counter()
    logger.debug("operation.start", operation=operation, **context)
    try:
        yield
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        logger.error(
            "operation.failed",
            operation=operation,
            latency_ms=elapsed_ms,
            error=str(exc),
            **context,
        )
        raise
    else:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        logger.info(
            "operation.completed", operation=operation, latency_ms=elapsed_ms, **context
        )
