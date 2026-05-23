"""Log validation - Validate structured logging."""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from app.logging import get_logger


@dataclass
class LogValidationResult:
    """Result of log validation."""

    log_emitted: bool
    is_structured: bool
    has_timestamp: bool
    has_level: bool
    has_message: bool
    is_json_parsable: bool
    error: Optional[str]
    timestamp: datetime


class LogValidator:
    """Validate structured logging."""

    def __init__(self) -> None:
        """Initialize log validator."""
        self.logger = get_logger(__name__)
        self._captured_logs: list[str] = []

    async def validate_logging(self) -> LogValidationResult:
        """Validate that logs are structured correctly.

        Returns:
            LogValidationResult
        """
        try:
            # Capture log output
            import io
            import sys
            from contextlib import redirect_stderr

            stderr_capture = io.StringIO()

            with redirect_stderr(stderr_capture):
                self.logger.info("test_log", test_key="test_value", nested={"key": "value"})

            log_output = stderr_capture.getvalue()

            if not log_output:
                return LogValidationResult(
                    log_emitted=False,
                    is_structured=False,
                    has_timestamp=False,
                    has_level=False,
                    has_message=False,
                    is_json_parsable=False,
                    error="No log output captured",
                    timestamp=datetime.now(timezone.utc),
                )

            # Try to parse as JSON
            try:
                log_data = json.loads(log_output)
                is_json = True
                is_structured = True
                has_timestamp = "timestamp" in log_data or "time" in log_data
                has_level = "level" in log_data or "severity" in log_data
                has_message = "message" in log_data or "msg" in log_data
            except json.JSONDecodeError:
                is_json = False
                is_structured = False
                has_timestamp = False
                has_level = False
                has_message = False

            return LogValidationResult(
                log_emitted=True,
                is_structured=is_structured,
                has_timestamp=has_timestamp,
                has_level=has_level,
                has_message=has_message,
                is_json_parsable=is_json,
                error=None,
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as exc:
            return LogValidationResult(
                log_emitted=False,
                is_structured=False,
                has_timestamp=False,
                has_level=False,
                has_message=False,
                is_json_parsable=False,
                error=str(exc),
                timestamp=datetime.now(timezone.utc),
            )
