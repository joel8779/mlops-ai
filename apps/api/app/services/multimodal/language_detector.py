"""Language Detector - Detect language of resume text."""

from dataclasses import dataclass
from enum import Enum

try:
    from langdetect import detect, DetectorFactory
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


class Language(str, Enum):
    """Supported languages."""

    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    PORTUGUESE = "pt"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"
    UNKNOWN = "unknown"


@dataclass
class DetectionResult:
    """Result of language detection."""

    language: Language
    confidence: float
    alternatives: list[tuple[Language, float]]


class LanguageDetector:
    """Detect language of resume text."""

    def __init__(self) -> None:
        """Initialize language detector."""
        if LANGDETECT_AVAILABLE:
            # Set seed for reproducibility
            DetectorFactory.seed = 0

    async def detect(self, text: str) -> DetectionResult:
        """Detect language of text.

        Args:
            text: Text to analyze

        Returns:
            DetectionResult with detected language
        """
        if not text or len(text.strip()) < 10:
            return DetectionResult(
                language=Language.UNKNOWN,
                confidence=0.0,
                alternatives=[],
            )

        if LANGDETECT_AVAILABLE:
            return await self._detect_with_langdetect(text)
        else:
            return await self._detect_heuristic(text)

    async def _detect_with_langdetect(self, text: str) -> DetectionResult:
        """Detect language using langdetect library.

        Args:
            text: Text to analyze

        Returns:
            DetectionResult
        """
        try:
            detected = detect(text)
            language = self._map_langdetect_code(detected)

            # Get confidence by testing multiple samples
            confidence = await self._calculate_confidence(text, language)

            return DetectionResult(
                language=language,
                confidence=confidence,
                alternatives=[],
            )
        except Exception:
            return DetectionResult(
                language=Language.UNKNOWN,
                confidence=0.0,
                alternatives=[],
            )

    async def _detect_heuristic(self, text: str) -> DetectionResult:
        """Detect language using heuristic methods.

        Args:
            text: Text to analyze

        Returns:
            DetectionResult
        """
        text_sample = text[:1000].lower()

        # Language-specific patterns
        patterns = {
            Language.SPANISH: ["el", "la", "los", "las", "un", "una", "es", "son", "está"],
            Language.FRENCH: ["le", "la", "les", "un", "une", "est", "sont", "dans"],
            Language.GERMAN: ["der", "die", "das", "ein", "eine", "ist", "sind", "im"],
            Language.PORTUGUESE: ["o", "a", "os", "as", "um", "uma", "é", "são"],
            Language.CHINESE: ["的", "是", "在", "了", "和", "有", "我", "他"],
            Language.JAPANESE: ["の", "は", "を", "に", "が", "で", "と", "も"],
            Language.KOREAN: ["의", "이", "가", "은", "는", "를", "을", "에"],
            Language.ARABIC: ["في", "من", "على", "إلى", "هذا", "هذه", "التي", "الذي"],
            Language.HINDI: ["के", "की", "का", "है", "में", "से", "पर", "को"],
        }

        # Score each language
        scores = {}
        for language, words in patterns.items():
            score = sum(1 for word in words if word in text_sample)
            scores[language] = score

        # Return highest scoring language
        if scores:
            best_language = max(scores, key=scores.get)
            confidence = min(scores[best_language] / 3.0, 1.0)  # Normalize

            return DetectionResult(
                language=best_language,
                confidence=confidence,
                alternatives=[],
            )

        # Default to English if no patterns match
        return DetectionResult(
            language=Language.ENGLISH,
            confidence=0.5,
            alternatives=[],
        )

    def _map_langdetect_code(self, code: str) -> Language:
        """Map langdetect code to Language enum.

        Args:
            code: Language code from langdetect

        Returns:
            Language enum
        """
        mapping = {
            "en": Language.ENGLISH,
            "es": Language.SPANISH,
            "fr": Language.FRENCH,
            "de": Language.GERMAN,
            "pt": Language.PORTUGUESE,
            "zh-cn": Language.CHINESE,
            "zh-tw": Language.CHINESE,
            "ja": Language.JAPANESE,
            "ko": Language.KOREAN,
            "ar": Language.ARABIC,
            "hi": Language.HINDI,
        }
        return mapping.get(code.lower(), Language.UNKNOWN)

    async def _calculate_confidence(self, text: str, language: Language) -> float:
        """Calculate confidence in language detection.

        Args:
            text: Text to analyze
            language: Detected language

        Returns:
            Confidence score between 0 and 1
        """
        # Simple confidence based on text length
        text_length = len(text.strip())

        if text_length > 500:
            return 0.9
        elif text_length > 100:
            return 0.7
        else:
            return 0.5
