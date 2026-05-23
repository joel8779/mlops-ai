from __future__ import annotations

from typing import Any

import structlog


def bind_log_context(**values: Any) -> None:
    clean = {key: str(value) for key, value in values.items() if value is not None}
    if clean:
        structlog.contextvars.bind_contextvars(**clean)


def clear_log_context() -> None:
    structlog.contextvars.clear_contextvars()
