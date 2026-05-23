from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.resilience.circuit_breakers import circuit_breakers

T = TypeVar("T")


class FallbackRouter:
    async def call_with_fallback(
        self,
        primary_name: str,
        primary: Callable[[], Awaitable[T]],
        fallback: Callable[[], Awaitable[T]],
    ) -> T:
        breaker = circuit_breakers.get(primary_name)
        try:
            return await breaker.call(primary)
        except Exception:
            return await fallback()
