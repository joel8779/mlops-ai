"""Validate optional OCR binaries and packages without starting the API."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "apps" / "api"
sys.path.insert(0, str(API_DIR))

from app.core.ocr_capabilities import detect_ocr_capabilities  # noqa: E402


def main() -> int:
    result = detect_ocr_capabilities()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
