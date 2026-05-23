from __future__ import annotations

import logging


class HealthcheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return "/health" not in message and "/ready" not in message and "/metrics" not in message
