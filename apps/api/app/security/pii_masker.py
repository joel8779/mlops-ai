"""PII Masker - Mask personally identifiable information for privacy."""

import re
from dataclasses import dataclass
from enum import Enum


class PIIMaskLevel(str, Enum):
    """Levels of PII masking."""

    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"


@dataclass
class MaskedResult:
    """Result of PII masking."""

    masked_text: str
    pii_detected: list[str]
    mask_count: int


class PIIMasker:
    """Mask PII from text for privacy compliance."""

    # PII patterns
    PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
        "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    }

    def __init__(self, mask_level: PIIMaskLevel = PIIMaskLevel.PARTIAL) -> None:
        """Initialize PII masker.

        Args:
            mask_level: Level of masking to apply
        """
        self.mask_level = mask_level

    def mask(self, text: str) -> MaskedResult:
        """Mask PII from text.

        Args:
            text: Text to mask

        Returns:
            MaskedResult with masked text and detection info
        """
        masked_text = text
        pii_detected = []
        mask_count = 0

        for pii_type, pattern in self.PATTERNS.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                pii_detected.append(pii_type)
                mask_count += 1
                masked_text = self._mask_match(match, masked_text, pii_type)

        return MaskedResult(
            masked_text=masked_text,
            pii_detected=pii_detected,
            mask_count=mask_count,
        )

    def _mask_match(self, match: re.Match, text: str, pii_type: str) -> str:
        """Mask a single match.

        Args:
            match: Regex match object
            text: Original text
            pii_type: Type of PII

        Returns:
            Text with match masked
        """
        start, end = match.span()
        original = match.group()

        if self.mask_level == PIIMaskLevel.NONE:
            return text

        if self.mask_level == PIIMaskLevel.FULL:
            return text[:start] + "*" * len(original) + text[end:]

        # Partial masking
        if pii_type == "email":
            # Show first character and domain
            parts = original.split("@")
            if len(parts) == 2:
                masked = parts[0][0] + "***@" + parts[1]
                return text[:start] + masked + text[end:]

        elif pii_type == "phone":
            # Show area code only
            masked = original[:3] + "-***-****"
            return text[:start] + masked + text[end:]

        elif pii_type == "ssn":
            # Show first 3 digits only
            masked = "***-**-****"
            return text[:start] + masked + text[end:]

        elif pii_type == "credit_card":
            # Show last 4 digits only
            masked = "****-****-****-" + original[-4:]
            return text[:start] + masked + text[end:]

        # Default partial masking
        return text[:start] + original[:2] + "*" * (len(original) - 2) + text[end:]

    def detect_pii(self, text: str) -> list[str]:
        """Detect PII in text without masking.

        Args:
            text: Text to analyze

        Returns:
            List of detected PII types
        """
        detected = []
        for pii_type, pattern in self.PATTERNS.items():
            if re.search(pattern, text):
                detected.append(pii_type)
        return detected

    def is_pii_free(self, text: str) -> bool:
        """Check if text is free of PII.

        Args:
            text: Text to check

        Returns:
            True if no PII detected
        """
        return len(self.detect_pii(text)) == 0
