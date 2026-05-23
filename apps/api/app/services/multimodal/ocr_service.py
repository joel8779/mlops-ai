"""OCR Service - Extract text from scanned documents and images."""

import io
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import pytesseract
from PIL import Image


class OCRLanguage(str, Enum):
    """Supported OCR languages."""

    ENGLISH = "eng"
    SPANISH = "spa"
    FRENCH = "fra"
    GERMAN = "deu"
    PORTUGUESE = "por"
    CHINESE_SIMPLIFIED = "chi_sim"
    CHINESE_TRADITIONAL = "chi_tra"
    JAPANESE = "jpn"
    KOREAN = "kor"
    ARABIC = "ara"
    HINDI = "hin"


@dataclass
class OCRResult:
    """Result of OCR processing."""

    text: str
    confidence: float
    language: str
    pages: int
    metadata: dict


class OCRService:
    """Service for OCR text extraction from documents."""

    def __init__(self, default_language: OCRLanguage = OCRLanguage.ENGLISH) -> None:
        """Initialize OCR service.

        Args:
            default_language: Default language for OCR
        """
        self.default_language = default_language

    async def extract_text_from_image(
        self,
        image_data: bytes,
        language: Optional[OCRLanguage] = None,
    ) -> OCRResult:
        """Extract text from an image.

        Args:
            image_data: Image bytes
            language: Optional language override

        Returns:
            OCRResult with extracted text and metadata
        """
        language = language or self.default_language

        # Open image
        image = Image.open(io.BytesIO(image_data))

        # Perform OCR
        text = pytesseract.image_to_string(image, lang=language.value)

        # Get confidence data
        data = pytesseract.image_to_data(image, lang=language.value, output_type=pytesseract.Output.DICT)
        confidences = [float(conf) for conf in data["conf"] if conf != "-1"]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return OCRResult(
            text=text.strip(),
            confidence=avg_confidence / 100.0,  # Convert to 0-1 range
            language=language.value,
            pages=1,
            metadata={
                "width": image.width,
                "height": image.height,
                "format": image.format,
            },
        )

    async def extract_text_from_pdf(
        self,
        pdf_path: Path,
        language: Optional[OCRLanguage] = None,
    ) -> OCRResult:
        """Extract text from a PDF using OCR.

        Args:
            pdf_path: Path to PDF file
            language: Optional language override

        Returns:
            OCRResult with extracted text and metadata
        """
        import fitz  # PyMuPDF

        language = language or self.default_language
        doc = fitz.open(pdf_path)

        all_text = []
        total_confidence = 0.0
        page_count = 0

        for page in doc:
            # Try to extract text directly first
            text = page.get_text()
            if text.strip():
                all_text.append(text)
                total_confidence += 1.0  # Direct extraction is high confidence
            else:
                # Fall back to OCR on page image
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                page_text = pytesseract.image_to_string(image, lang=language.value)
                all_text.append(page_text)

                # Get confidence
                data = pytesseract.image_to_data(image, lang=language.value, output_type=pytesseract.Output.DICT)
                confidences = [float(conf) for conf in data["conf"] if conf != "-1"]
                avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
                total_confidence += avg_conf / 100.0

            page_count += 1

        doc.close()

        combined_text = "\n\n".join(all_text)
        avg_confidence = total_confidence / page_count if page_count > 0 else 0.0

        return OCRResult(
            text=combined_text.strip(),
            confidence=avg_confidence,
            language=language.value,
            pages=page_count,
            metadata={"source": "pdf", "path": str(pdf_path)},
        )

    async def extract_structured_data(
        self,
        image_data: bytes,
        language: Optional[OCRLanguage] = None,
    ) -> dict:
        """Extract structured data from an image (e.g., forms, tables).

        Args:
            image_data: Image bytes
            language: Optional language override

        Returns:
            Dictionary with structured data
        """
        language = language or self.default_language
        image = Image.open(io.BytesIO(image_data))

        # Get OCR data with bounding boxes
        data = pytesseract.image_to_data(image, lang=language.value, output_type=pytesseract.Output.DICT)

        # Group by lines
        lines = {}
        for i, text in enumerate(data["text"]):
            if text.strip():
                line_num = data["line_num"][i]
                if line_num not in lines:
                    lines[line_num] = []
                lines[line_num].append({
                    "text": text,
                    "left": data["left"][i],
                    "top": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i],
                    "confidence": float(data["conf"][i]) / 100.0,
                })

        return {
            "lines": lines,
            "total_lines": len(lines),
            "language": language.value,
        }

    def detect_language_from_text(self, text: str) -> OCRLanguage:
        """Detect likely language from text sample.

        Args:
            text: Text sample

        Returns:
            Detected OCRLanguage
        """
        # Simple heuristic-based detection
        # In production, use a proper language detection library like langdetect
        text_sample = text[:500]

        # Check for character patterns
        if any(ord(c) > 127 for c in text_sample):
            # Non-ASCII characters
            if any("\u4e00" <= c <= "\u9fff" for c in text_sample):
                return OCRLanguage.CHINESE_SIMPLIFIED
            if any("\u3040" <= c <= "\u309f" or "\u30a0" <= c <= "\u30ff" for c in text_sample):
                return OCRLanguage.JAPANESE
            if any("\uac00" <= c <= "\ud7af" for c in text_sample):
                return OCRLanguage.KOREAN
            if any("\u0600" <= c <= "\u06ff" for c in text_sample):
                return OCRLanguage.ARABIC
            if any("\u0900" <= c <= "\u097f" for c in text_sample):
                return OCRLanguage.HINDI

        # Check for common words
        text_lower = text_sample.lower()
        if any(word in text_lower for word in ["el", "la", "los", "las", "un", "una", "es"]):
            return OCRLanguage.SPANISH
        if any(word in text_lower for word in ["le", "la", "les", "un", "une", "est"]):
            return OCRLanguage.FRENCH
        if any(word in text_lower for word in ["der", "die", "das", "ein", "eine", "ist"]):
            return OCRLanguage.GERMAN
        if any(word in text_lower for word in ["o", "a", "os", "as", "um", "uma", "é"]):
            return OCRLanguage.PORTUGUESE

        return self.default_language
