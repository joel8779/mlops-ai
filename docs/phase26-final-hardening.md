# Phase 26 Final Hardening Notes

## Scope

This phase focused on SaaS demo readiness without changing the backend architecture.

## Hardened Areas

- Frontend API client handles JSON and multipart requests correctly.
- Protected recruiter routes now share a common auth gate in `AppShell`.
- Candidate, job, feedback, ATS, and AI actions are wired to live backend APIs.
- Analytics response includes dashboard counters expected by the frontend.
- Candidate search payloads include recruiter-visible metadata for semantic results.
- Demo seeding is root-level, deterministic, and can optionally index vectors.

## Deployment Checklist

- Vercel: set `NEXT_PUBLIC_API_BASE_URL` to the deployed backend `/api/v1`.
- Backend: set production `DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `QDRANT_URL`, `GEMINI_API_KEY`, JWT secrets, and storage credentials.
- Neon: enable pooled PostgreSQL URL for API and worker.
- Upstash: use separate Redis DBs or key prefixes for API cache, Celery broker, and Celery result backend.
- Qdrant Cloud: pre-create or allow runtime creation of candidate/job embedding collections.
- Storage: configure S3-compatible storage or MinIO; keep upload limits aligned with `MAX_UPLOAD_BYTES`.
- Workers: run Celery separately from API with the same env vars and OCR binaries only where OCR is needed.

## Operational Guardrails

- Keep OCR, embeddings, AI routes, and worker execution optional or degraded where possible.
- Keep API startup independent of Tesseract, model downloads, and worker availability.
- Validate with:
  - `scripts/backend_validation.py`
  - `scripts/test_embeddings_runtime.py --dependency-only`
  - `scripts/test_worker_runtime.py --dependency-only`
  - `scripts/test_ocr_runtime.py`
  - frontend `npm run build`
