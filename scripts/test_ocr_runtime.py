"""Validate optional OCR/document extraction without starting the backend."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "apps" / "api"
os.environ["DEBUG"] = "false"
sys.path.insert(0, str(API_DIR))

from app.core.ocr_capabilities import detect_ocr_capabilities  # noqa: E402
from app.services.extraction_service import ExtractionService, ResumeParseError  # noqa: E402


PDF_TYPE = "application/pdf"
DOCX_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
PNG_TYPE = "image/png"


def build_pdf(text: str) -> bytes:
    import fitz

    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    payload = document.tobytes()
    document.close()
    return payload


def build_docx(text: str) -> bytes:
    from docx import Document

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as handle:
        path = Path(handle.name)
    try:
        document = Document()
        document.add_paragraph(text)
        document.save(path)
        return path.read_bytes()
    finally:
        path.unlink(missing_ok=True)


def build_image(text: str) -> bytes:
    from io import BytesIO

    from PIL import Image, ImageDraw

    image = Image.new("RGB", (900, 220), "white")
    draw = ImageDraw.Draw(image)
    draw.text((32, 80), text, fill="black")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def parse_case(name: str, payload: bytes, content_type: str) -> dict[str, Any]:
    service = ExtractionService()
    try:
        parsed = service.parse(payload, content_type)
        return {
            "name": name,
            "ok": True,
            "text_length": len(parsed.text),
            "metadata": parsed.metadata,
            "preview": parsed.text[:120],
        }
    except Exception as exc:
        return {"name": name, "ok": False, "error": str(exc), "error_type": type(exc).__name__}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate OCR/document extraction runtime.")
    parser.add_argument("--include-image-ocr", action="store_true", help="Run Tesseract image OCR.")
    args = parser.parse_args()

    capabilities = detect_ocr_capabilities()
    cases = [
        parse_case("pdf_direct", build_pdf("Jane Candidate Python PostgreSQL"), PDF_TYPE),
        parse_case("docx_direct", build_docx("Jane Candidate FastAPI Redis Qdrant"), DOCX_TYPE),
        parse_case("malformed_pdf", b"not a pdf", PDF_TYPE),
        parse_case("empty_upload", b"", PDF_TYPE),
        parse_case("unsupported_format", b"plain text", "text/plain"),
    ]
    if args.include_image_ocr:
        cases.append(parse_case("image_ocr", build_image("Jane Candidate OCR Python"), PNG_TYPE))
    else:
        cases.append(
            {
                "name": "image_ocr",
                "ok": None,
                "skipped": "pass --include-image-ocr to require local Tesseract OCR",
            }
        )

    hard_failures = [
        item
        for item in cases
        if item["name"] in {"pdf_direct", "docx_direct"} and not item["ok"]
    ]
    if args.include_image_ocr:
        hard_failures.extend(
            item for item in cases if item["name"] == "image_ocr" and not item["ok"]
        )
    malformed_ok = all(
        item["ok"] is False and item.get("error_type") in {"ResumeParseError", "RuntimeError"}
        for item in cases
        if item["name"] in {"malformed_pdf", "empty_upload", "unsupported_format"}
    )
    result = {
        "capabilities": capabilities,
        "cases": cases,
        "success": not hard_failures and malformed_ok,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
