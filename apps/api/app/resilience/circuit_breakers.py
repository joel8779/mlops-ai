from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Awaitable, Callable, TypeVar


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


T = TypeVar("T")


@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 30
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    opened_at: datetime | None = None

    async def call(self, operation: Callable[[], Awaitable[T]]) -> T:
        if self.state == CircuitState.OPEN:
            if not self._can_probe():
                raise RuntimeError(f"Circuit breaker '{self.name}' is open")
            self.state = CircuitState.HALF_OPEN
        try:
            result = await operation()
        except Exception:
            self._record_failure()
            raise
        self._record_success()
        return result

    def _record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.opened_at = datetime.now(timezone.utc)

    def _record_success(self) -> None:
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.opened_at = None

    def _can_probe(self) -> bool:
        if self.opened_at is None:
            return True
        return datetime.now(timezone.utc) - self.opened_at >= timedelta(seconds=self.recovery_timeout_seconds)


@dataclass
class CircuitBreakerRegistry:
    _breakers: dict[str, CircuitBreaker] = field(default_factory=dict)

    def get(self, name: str) -> CircuitBreaker:
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name=name)
        return self._breakers[name]


circuit_breakers = CircuitBreakerRegistry()
