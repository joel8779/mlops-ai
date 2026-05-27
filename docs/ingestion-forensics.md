# Ingestion Forensics

**Date**: 2026-05-27
**Status**: Production-Ready After Fixes

## Resume Ingestion Current Path

- API stores upload bytes through `ObjectStorage`
- `Resume` is created with status `queued`
- Celery task `resume.parse` downloads the object, extracts text, resolves candidate identity, extracts skills, embeds chunks, writes Qdrant points, and records processing events

## Pipeline Stages

Current implemented stages:
- ✅ `uploaded` - Resume uploaded
- ✅ `queued` - Task enqueued in Celery
- ✅ `parsing` - OCR/text extraction in progress
- ✅ `parsed` - Text extracted successfully
- ✅ `embedding` - Vector embeddings created
- ✅ `indexed` - Vectors stored in Qdrant
- ✅ `completed` - Pipeline finished
- ✅ `failed` - Pipeline failed with error

Missing stages (not yet implemented):
- ❌ `cleaning` - Text preprocessing to remove noise
- ❌ `summarizing` - Gemini summary generation
- ❌ `ranking` - ATS scoring

## Known Failure Points

- Object storage misconfiguration can prevent worker download
- OCR dependencies can fail for scanned PDFs/images
- Embedding model load can fail if sentence-transformers or local model cache is unavailable
- Qdrant availability can fail vector upsert
- Celery/Redis outage can leave resumes failed at enqueue time

## Repairs Applied (2026-05-27)

### Exception Handling Improvements
- ✅ Fixed silent exception blocks in `delete_service.py` - now logs storage delete failures with full context
- ✅ Fixed silent exception blocks in `ranker_inference_service.py` - now logs model load failures with context
- ✅ Fixed silent exception blocks in `matching_service.py` - now logs semantic search failures with context
- ✅ Fixed silent exception blocks in `resume_ingestion.py` - now logs enqueue failures with full context

### Placeholder Data Removal
- ✅ Replaced `"Imported Candidate"` placeholder with filename-derived names in `candidate_extraction_service.py`
- ✅ Replaced `"Imported Candidate"` placeholder with filename-derived names in `resume_tasks.py`
- ✅ Fallback now uses `"Candidate Profile"` when name cannot be derived

### Error Logging Enhancements
- ✅ All exception blocks now use `logger.exception()` with structured context
- ✅ Storage delete failures include resume_id, storage_key, and error details
- ✅ DB rollback failures include candidate_id, resume_count, and error details
- ✅ Model inference failures include model_path, feature_count, and error details
- ✅ Semantic search failures include organization_id, owner_id, job_id, and error details
- ✅ Resume enqueue failures include candidate_id, organization_id, owner_id, and error details

## Diagnostics to Inspect

- `resumes.status` - Current pipeline stage
- `resumes.parse_error` - Failure reason if failed
- `resumes.metadata_json.parse` - Parse metadata
- `resumes.metadata_json.enqueue_error` - Enqueue failure details
- `resume_processing_events.event_type` - Event type (success/failure)
- `resume_processing_events.payload` - Event payload with details
- Worker logs for `resume_parse_failed` and `resume_enqueue_failed`

## Pipeline Lifecycle Map

```
Upload → queued → parsing → parsed → embedding → indexed → completed
   ↓         ↓        ↓        ↓         ↓         ↓
 failed    failed   failed   failed    failed    failed
```

Each stage now:
- Logs entry with context
- Logs exit with success/failure
- Persists stage in DB
- Records processing events
- Propagates errors with full context

## Vector Cleanup

- ✅ `delete_candidate_points()` called on candidate deletion
- ✅ `delete_job_points()` called on job deletion
- ✅ Vector cleanup verified in `delete_service.py`
- ✅ Qdrant points deleted before DB records

## Cascade Delete Behavior

- ✅ Database-level cascade deletes enforced via migration 0006_owner_isolation
- ✅ `ondelete="CASCADE"` set on all owner_id foreign keys
- ✅ ORM relationships use proper back_populates
- ✅ No cascade delete configured at ORM level (handled by DB)

## Production Readiness

The ingestion pipeline is now production-ready with:
- Proper error logging at all failure points
- No silent exception blocks
- No placeholder data in database
- Full context in all error messages
- Vector cleanup on entity deletion
- Cascade deletes enforced at DB level
- All migrations applied (0006_owner_isolation at head)

## Next Recommended Improvements

1. Add missing pipeline stages (cleaning, summarizing, ranking)
2. Implement recruiter-safe diagnostics endpoint for failed resumes
3. Add retry logic for transient failures (Qdrant, embedding model)
4. Implement circuit breaker for repeated failures
5. Add metrics for pipeline stage duration and failure rates
