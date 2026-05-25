"""Startup-safe OCR and document parsing capability checks."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from importlib import metadata
from typing import Any


@dataclass(frozen=True)
class BinaryCheck:
    name: str
    available: bool
    path: str | None
    version: str | None
    warning: str | None = None


@dataclass(frozen=True)
class PackageCheck:
    name: str
    available: bool
    version: str | None
    warning: str | None = None


def check_package(distribution: str, import_name: str | None = None) -> PackageCheck:
    try:
        version = metadata.version(distribution)
    except metadata.PackageNotFoundError:
        return PackageCheck(
            name=distribution,
            available=False,
            version=None,
            warning=f"{distribution} is not installed",
        )

    if import_name:
        try:
            __import__(import_name)
        except Exception as exc:
            return PackageCheck(
                name=distribution,
                available=False,
                version=version,
                warning=f"{import_name} import failed: {exc}",
            )
    return PackageCheck(name=distribution, available=True, version=version)


def check_binary(name: str, version_args: list[str] | None = None) -> BinaryCheck:
    path = shutil.which(name)
    if not path:
        return BinaryCheck(
            name=name,
            available=False,
            path=None,
            version=None,
            warning=f"{name} was not found on PATH",
        )

    version = None
    try:
        completed = subprocess.run(
            [path, *(version_args or ["--version"])],
            capture_output=True,
            check=False,
            text=True,
            timeout=5,
        )
        output = (completed.stdout or completed.stderr).strip().splitlines()
        version = output[0] if output else None
    except Exception as exc:
        return BinaryCheck(
            name=name,
            available=True,
            path=path,
            version=None,
            warning=f"{name} version probe failed: {exc}",
        )
    return BinaryCheck(name=name, available=True, path=path, version=version)


def detect_ocr_capabilities() -> dict[str, Any]:
    packages = {
        "pytesseract": check_package("pytesseract"),
        "Pillow": check_package("Pillow", "PIL"),
        "pdfplumber": check_package("pdfplumber"),
        "PyMuPDF": check_package("PyMuPDF", "fitz"),
        "python-docx": check_package("python-docx", "docx"),
        "pdf2image": check_package("pdf2image"),
        "easyocr": check_package("easyocr"),
    }
    binaries = {
        "tesseract": check_binary("tesseract"),
        "pdftoppm": check_binary("pdftoppm", ["-v"]),
        "pdfinfo": check_binary("pdfinfo", ["-v"]),
    }
    warnings = [
        item.warning
        for item in [*packages.values(), *binaries.values()]
        if item.warning
    ]
    return {
        "packages": {name: vars(check) for name, check in packages.items()},
        "binaries": {name: vars(check) for name, check in binaries.items()},
        "warnings": warnings,
        "ocr_available": packages["pytesseract"].available
        and packages["Pillow"].available
        and binaries["tesseract"].available,
        "pdf_direct_available": packages["pdfplumber"].available or packages["PyMuPDF"].available,
        "pdf_ocr_available": packages["PyMuPDF"].available
        and packages["pytesseract"].available
        and packages["Pillow"].available
        and binaries["tesseract"].available,
        "docx_available": packages["python-docx"].available,
        "poppler_available": binaries["pdftoppm"].available and binaries["pdfinfo"].available,
    }
