"""
Structured logging with structlog.

- JSON output in production, colored console in development.
- Adds contextual metadata (device_id, user_id, request_id) via bind().
"""

from __future__ import annotations

import logging
import sys

import structlog
from structlog.types import Processor

from app.core.config import settings


def _build_processors(is_dev: bool) -> list[Processor]:
    shared: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]
    if is_dev:
        shared.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        shared.append(structlog.processors.format_exc_info)
        shared.append(structlog.processors.JSONRenderer())
    return shared


def configure_logging(level: str = "INFO") -> None:
    """Configure structlog + stdlib logging (call once at startup)."""
    level_value = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level_value,
    )

    structlog.configure(
        processors=_build_processors(settings.is_development),
        wrapper_class=structlog.make_filtering_bound_logger(level_value),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Silence very noisy libraries in production
    if settings.is_production:
        for noisy in ("uvicorn.access", "sqlalchemy.engine", "asyncio"):
            logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger; pass module `__name__` for best results."""
    return structlog.get_logger(name)
