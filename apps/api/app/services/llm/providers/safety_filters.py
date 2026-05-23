"""Content safety filters for LLM outputs."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SafetyLevel(str, Enum):
    """Safety filtering levels."""

    BLOCK_NONE = "block_none"
    BLOCK_LOW = "block_low"
    BLOCK_MEDIUM = "block_medium"
    BLOCK_HIGH = "block_high"


@dataclass
class SafetyResult:
    """Result of safety check."""

    is_safe: bool
    blocked_categories: list[str]
    confidence: float
    reason: str = ""


class SafetyFilter:
    """Content safety filter for LLM inputs and outputs."""

    # Patterns for potentially harmful content
    PATTERNS = {
        "personal_info": [
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone numbers
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
        ],
        "financial_info": [
            r"\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b",  # Credit card
            r"\b\d{16}\b",  # Credit card without spaces
        ],
        "api_keys": [
            r"[A-Za-z0-9]{32,}",  # Long alphanumeric strings (potential API keys)
        ],
    }

    # Blocked words/phrases
    BLOCKED_PHRASES = [
        "password",
        "secret",
        "api key",
        "access token",
        "private key",
    ]

    def __init__(self, level: SafetyLevel = SafetyLevel.BLOCK_MEDIUM) -> None:
        """Initialize safety filter.

        Args:
            level: Safety filtering level
        """
        self.level = level

    def check_input(self, text: str) -> SafetyResult:
        """Check input text for safety issues.

        Args:
            text: Input text to check

        Returns:
            SafetyResult with check outcome
        """
        blocked_categories = []
        confidence = 0.0

        # Check for PII patterns
        for category, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    blocked_categories.append(category)
                    confidence = max(confidence, 0.8)

        # Check for blocked phrases
        for phrase in self.BLOCKED_PHRASES:
            if phrase.lower() in text.lower():
                blocked_categories.append("sensitive_phrase")
                confidence = max(confidence, 0.9)

        is_safe = len(blocked_categories) == 0 or self.level == SafetyLevel.BLOCK_NONE

        return SafetyResult(
            is_safe=is_safe,
            blocked_categories=blocked_categories,
            confidence=confidence,
            reason=f"Blocked categories: {', '.join(blocked_categories)}" if blocked_categories else "",
        )

    def check_output(self, text: str) -> SafetyResult:
        """Check output text for safety issues.

        Args:
            text: Output text to check

        Returns:
            SafetyResult with check outcome
        """
        # Output checks are similar to input checks
        return self.check_input(text)

    def sanitize(self, text: str) -> str:
        """Sanitize text by removing sensitive information.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        sanitized = text

        # Mask phone numbers
        sanitized = re.sub(
            r"\b(\d{3})[-.]?(\d{3})[-.]?(\d{4})\b",
            r"\1-***-\3",
            sanitized,
        )

        # Mask emails
        sanitized = re.sub(
            r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+)\.([A-Z|a-z]{2,})\b",
            r"***@\2.***",
            sanitized,
        )

        # Mask SSN-like patterns
        sanitized = re.sub(
            r"\b\d{3}-\d{2}-\d{4}\b",
            "***-**-****",
            sanitized,
        )

        # Mask credit cards
        sanitized = re.sub(
            r"\b(\d{4})[\s-]?(\d{4})[\s-]?(\d{4})[\s-]?(\d{4})\b",
            r"\1-****-****-\4",
            sanitized,
        )

        return sanitized

    def should_block(self, result: SafetyResult) -> bool:
        """Determine if content should be blocked based on safety level.

        Args:
            result: SafetyResult from check

        Returns:
            True if content should be blocked
        """
        if self.level == SafetyLevel.BLOCK_NONE:
            return False

        if not result.is_safe:
            if self.level == SafetyLevel.BLOCK_HIGH:
                # Only block high confidence
                return result.confidence >= 0.9
            elif self.level == SafetyLevel.BLOCK_MEDIUM:
                # Block medium and high confidence
                return result.confidence >= 0.7
            elif self.level == SafetyLevel.BLOCK_LOW:
                # Block any detected issue
                return True

        return False
