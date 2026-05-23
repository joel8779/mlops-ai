from __future__ import annotations

from typing import Any

from app.observability.tracing.correlation import current_trace_context


def add_trace_context(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    event_dict.update(current_trace_context())
    return event_dict
