# OCR Stack Analysis - PHASE 24.4

Date: 2026-05-25

## Current Findings

- `ExtractionService` is the active resume/job document parser used by Celery workers.
- Resume uploads already accept PDF, DOCX, PNG, and JPEG, then queue `resume.parse`.
- The stable API startup path does not need OCR, so OCR/document dependencies must stay lazy.
- The previous parser imported OCR/PDF/DOCX packages at module import time. That was unsafe for optional OCR.

## Minimal Stable Stack

- `pdfplumber`: first-pass direct text extraction for digital PDFs.
- `PyMuPDF` (`fitz`): direct PDF fallback and scanned-page rendering when OCR is required.
- `python-docx`: DOCX paragraph extraction.
- `Pillow`: image decoding for OCR fallback.
- `pytesseract`: Python wrapper for Tesseract.
- External `tesseract` binary: required only for image OCR and scanned PDF OCR.

## Avoided Stack

- `pdf2image`: avoided because it requires Poppler and duplicates PyMuPDF rendering.
- Poppler: optional only; detected for forensics but not required by the chosen path.
- `easyocr`: avoided because it pulls heavy vision/deep-learning dependencies.
- GPU/CUDA packages: not required and intentionally excluded.
- Training frameworks: not part of this restoration phase.

## Windows-Safe Strategy

1. Extract PDF text directly with `pdfplumber`.
2. Fall back to PyMuPDF direct extraction if `pdfplumber` cannot decode the PDF.
3. Parse DOCX with `python-docx`.
4. Use Tesseract OCR only for image uploads or PDFs with insufficient direct text.
5. Render PDF pages with PyMuPDF instead of Poppler.
6. Detect `tesseract`, `pdftoppm`, and `pdfinfo` safely with `shutil.which` and short version probes.

## External Binary Requirements

- Tesseract must be installed separately and available on `PATH` for OCR.
- Poppler is not required by runtime ingestion because `pdf2image` is not used.
- Missing binaries produce structured warnings and do not break API startup.

## Guardrails Added

- Lazy imports for PDF, DOCX, Pillow, and Tesseract wrappers.
- `OCR_ENABLED` can disable OCR without disabling direct PDF/DOCX parsing.
- `OCR_TIMEOUT_SECONDS` bounds individual Tesseract calls.
- `OCR_MAX_PAGES` bounds PDF parsing/OCR page count.
- `MAX_UPLOAD_BYTES` is enforced again inside extraction for worker-side protection.
- Malformed, empty, unsupported, and OCR-unavailable documents fail as controlled parse errors.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe scripts\validate_ocr_binaries.py
.\.venv\Scripts\python.exe scripts\test_ocr_runtime.py
.\.venv\Scripts\python.exe scripts\test_ocr_runtime.py --include-image-ocr
```

The final command requires a local Tesseract installation. The first two commands do not start FastAPI.
