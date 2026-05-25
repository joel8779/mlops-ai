# Worker Pipeline Trace

Resume worker stages now emit structured events into `resume_processing_events`.

Stages:

- `storage_download`
- `document_extraction`
- `candidate_extraction`
- `skill_persistence`
- `embedding_indexing`

Each stage event includes:

- `stage`
- `status`
- `duration_ms`
- payload summary
- recruiter-safe error code and message on failure
- exception type and message for backend operators

Failure codes:

- `ocr_extraction_failed`
- `gemini_extraction_failed`
- `embedding_generation_failed`
- `qdrant_indexing_failed`
- `candidate_persistence_failed`
- `document_parsing_failed`

Diagnostic endpoints:

- `/api/v1/resumes/{resume_id}/diagnostics`
- `/api/v1/diagnostics/runtime`

Operational note:

The worker still depends on Redis/Celery, object storage, OCR binaries, Python parser packages, sentence-transformers, and Qdrant. The new trace events are meant to identify the exact failing segment instead of returning only `Document processing failed`.
