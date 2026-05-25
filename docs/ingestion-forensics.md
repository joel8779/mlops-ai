# Ingestion Forensics

Resume ingestion current path:

- API stores upload bytes through `ObjectStorage`.
- `Resume` is created with status `queued`.
- Celery task `resume.parse` downloads the object, extracts text, resolves candidate identity, extracts skills, embeds chunks, writes Qdrant points, and records processing events.

Known failure points:

- Object storage misconfiguration can prevent worker download.
- OCR dependencies can fail for scanned PDFs/images.
- Embedding model load can fail if sentence-transformers or local model cache is unavailable.
- Qdrant availability can fail vector upsert.
- Celery/Redis outage can leave resumes failed at enqueue time.

Repairs applied:

- Worker identity resolution now uses `CandidateIdentityExtractor`.
- `"Candidate Profile"` is blocked as a detected name.
- Existing real candidate names are not overwritten by fallback identity.
- Resume processing events continue to record success and failure event types.

Diagnostics to inspect:

- `resumes.status`
- `resumes.parse_error`
- `resumes.metadata_json.parse`
- `resume_processing_events.event_type`
- `resume_processing_events.payload`
- worker logs for `resume_parse_failed` and `resume_enqueue_failed`

Next recommended repair:

Expose a recruiter-safe diagnostics endpoint that returns the latest processing event, normalized failure category, and next action for each failed resume instead of a generic document processing failure.
