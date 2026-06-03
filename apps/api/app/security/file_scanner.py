MALWARE_SIGNATURES = [b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE", b"<script", b"<?php"]


def scan_upload(payload: bytes) -> None:
    if not payload:
        raise ValueError("Empty file payload")

    # Inspect magic numbers/headers
    is_pdf = payload.startswith(b"%PDF")
    is_docx = payload.startswith(b"PK\x03\x04")
    is_png = payload.startswith(b"\x89PNG")
    is_jpeg = payload.startswith(b"\xff\xd8\xff")

    if not (is_pdf or is_docx or is_png or is_jpeg):
        raise ValueError("Invalid file format. Only PDF, DOCX, PNG, and JPEG are allowed.")

    lowered = payload[:4096].lower()
    if any(signature.lower() in lowered for signature in MALWARE_SIGNATURES):
        raise ValueError("Upload failed malware signature scan")

