from dataclasses import dataclass
from io import BytesIO

import fitz
import pdfplumber
import pytesseract
from docx import Document
from PIL import Image


class ResumeParseError(RuntimeError):
    pass


@dataclass(frozen=True)
class ParsedResume:
    text: str
    parser_version: str
    metadata: dict[str, str | int]


class ExtractionService:
    parser_version = "resume-extraction-0.2.0"

    def parse(self, payload: bytes, content_type: str) -> ParsedResume:
        if content_type == "application/pdf":
            return self._parse_pdf(payload)
        if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return self._parse_docx(payload)
        if content_type in {"image/png", "image/jpeg"}:
            return self._parse_image(payload)
        raise ResumeParseError(f"Unsupported content type: {content_type}")

    def _parse_pdf(self, payload: bytes) -> ParsedResume:
        with pdfplumber.open(BytesIO(payload)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
            text = normalize_text("\n".join(pages))
            page_count = len(pdf.pages)
        if not text:
            # PyMuPDF is a useful fallback for PDFs that pdfplumber cannot decode cleanly.
            document = fitz.open(stream=payload, filetype="pdf")
            text = normalize_text("\n".join(page.get_text() for page in document))
            page_count = document.page_count
        return ParsedResume(text=text, parser_version=self.parser_version, metadata={"page_count": page_count})

    def _parse_docx(self, payload: bytes) -> ParsedResume:
        document = Document(BytesIO(payload))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        text = normalize_text("\n".join(paragraphs))
        return ParsedResume(
            text=text,
            parser_version=self.parser_version,
            metadata={"paragraph_count": len(document.paragraphs)},
        )

    def _parse_image(self, payload: bytes) -> ParsedResume:
        image = Image.open(BytesIO(payload))
        text = normalize_text(pytesseract.image_to_string(image))
        return ParsedResume(
            text=text,
            parser_version=self.parser_version,
            metadata={"width": image.width, "height": image.height},
        )


def normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)
