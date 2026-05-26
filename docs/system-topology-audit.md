# System Topology Audit

Date: 2026-05-26

## Application Shape

Neural Ops is a full-stack AI recruiting intelligence platform.

- Frontend: Next.js app under `apps/web`
- Backend: FastAPI app under `apps/api`
- Database: PostgreSQL with Alembic migrations
- Queue/cache: Redis
- Vector store: Qdrant
- Workers: Celery workers under `app.workers`
- Storage: S3-compatible object storage, MinIO in local Docker
- AI: Gemini-backed extraction and scoring, sentence-transformer embeddings
- OCR: Tesseract, Poppler, DOCX/PDF parsing
- Observability: Prometheus, Grafana, Loki, OpenTelemetry hooks

## Frontend Routes

Primary recruiter routes:

- `/landing`
- `/login`
- `/signup`, `/sign-up`, `/sign-in`
- `/dashboard`
- `/documents`
- `/jobs`, `/jobs/[id]`
- `/candidates`, `/candidates/[id]`
- `/search`
- `/analytics`
- `/settings`

Compatibility/legacy surface:

- `/resumes`
- `/copilot`

These were not removed because deployed links or user bookmarks may still depend on them.

## Backend Route Modules

API router modules:

- `auth`
- `me`
- `workspace`
- `resumes`
- `candidates`
- `jobs`
- `matching`
- `ats`
- `search`
- `feedback`
- `analytics`
- `diagnostics`
- `health`
- `realtime`
- `recommendations`
- `workflow`
- `billing`
- `ai`

Primary frontend API client: `apps/web/lib/api.ts`.

## Runtime Flow

Resume upload:

```text
Frontend /documents
  -> POST /api/v1/resumes/upload
  -> object storage
  -> Resume row queued
  -> Celery resume.parse
  -> document parsing / OCR
  -> candidate extraction
  -> candidate hydration
  -> skill persistence
  -> embeddings
  -> Qdrant candidate index
  -> resume embedded
```

Job upload:

```text
Frontend /jobs
  -> POST /api/v1/jobs/upload
  -> file extraction
  -> job intelligence parse
  -> JobDescription row
  -> Celery job_description.index
  -> embeddings
  -> Qdrant job index
```

Ranking:

```text
GET /api/v1/jobs/{id}/intelligence
  -> ensure candidate matches
  -> ensure ATS scores
  -> hydrate ranked candidates
```

Deletion:

```text
DELETE /api/v1/candidates/{id}
  -> Qdrant point cleanup
  -> ATS/match/shortlist/feedback cleanup
  -> embedding metadata cleanup
  -> ingestion event cleanup
  -> resume unlink
  -> candidate soft delete
```

## Stabilization Changes

- Docker compose API startup now runs `alembic upgrade head` before Uvicorn.
- `/ready` is now dependency-aware and schema-aware.
- `/health` remains liveness-oriented.
- Runtime schema drift validation now reports readiness failure without hard-crashing by default.
- Frontend API base URL config is reconciled to `NEXT_PUBLIC_API_BASE_URL`.
