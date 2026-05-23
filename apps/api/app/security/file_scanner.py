MALWARE_SIGNATURES = [b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE", b"<script", b"<?php"]


def scan_upload(payload: bytes) -> None:
    lowered = payload[:4096].lower()
    if any(signature.lower() in lowered for signature in MALWARE_SIGNATURES):
        raise ValueError("Upload failed malware signature scan")
