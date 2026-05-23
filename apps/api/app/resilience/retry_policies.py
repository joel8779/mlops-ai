from __future__ import annotations

from dataclasses import dataclass
from random import random

from tenacity import retry_if_exception_type, stop_after_attempt, wait_exponential_jitter


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3
    min_wait_seconds: float = 0.2
    max_wait_seconds: float = 5.0

    def tenacity_kwargs(self) -> dict:
        return {
            "retry": retry_if_exception_type(Exception),
            "stop": stop_after_attempt(self.attempts),
            "wait": wait_exponential_jitter(
                initial=self.min_wait_seconds,
                max=self.max_wait_seconds,
                jitter=random(),
            ),
            "reraise": True,
        }


DEFAULT_RETRY_POLICY = RetryPolicy()
