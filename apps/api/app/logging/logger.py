from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from app.core.config import settings
from app.logging.filters import HealthcheckFilter
from app.logging.serializers import add_trace_context


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(HealthcheckFilter())
    logging.basicConfig(
        handlers=[handler],
        format="%(message)s",
        level=settings.log_level.upper(),
        force=True,
    )
    renderer = structlog.processors.JSONRenderer() if settings.log_json else structlog.dev.ConsoleRenderer()
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_trace_context,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level.upper())
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str, **context: Any) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name).bind(**context)
