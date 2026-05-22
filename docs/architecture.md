# Architecture

## Platform Shape

The platform is a microservice-oriented monorepo with a thin API gateway, async background processing, typed contracts, and MLOps infrastructure from day one.

```text
Recruiter UI -> FastAPI API -> PostgreSQL
                    |            |
                    |            -> domain events
                    -> Redis -> Celery workers
                    -> S3-compatible storage
                    -> Qdrant vector search
                    -> MLflow model registry
                    -> LLM providers
```

## Services

- `apps/web`: recruiter dashboard, candidate profiles, upload flow, search, ranking views, notes, analytics.
- `apps/api`: API gateway, auth, tenancy, REST endpoints, request validation, rate limiting, audit logging.
- `services/workers`: resume parsing, OCR, embeddings, duplicate detection, notifications, batch inference.
- `services/ml`: training pipelines, evaluation, feature generation, model registration, drift checks.
- `infra`: local and production deployment, monitoring, CI/CD, observability.

## Event Flow

1. Recruiter uploads a resume.
2. API stores the original document in S3-compatible storage.
3. API writes `resumes` and `resume_processing_events` rows.
4. API enqueues `parse_resume_task`.
5. Worker extracts text from PDF/DOCX/image, normalizes skills, creates candidate profile fields, generates embeddings, and updates processing status.
6. Ranking and search services consume embeddings, skills, profile facts, and feedback events.

## Core Design Decisions

- PostgreSQL is the source of truth for business state.
- Qdrant stores candidate, resume, and job description embeddings for semantic retrieval.
- MLflow is used for experiment tracking and model registry.
- Celery handles long-running and retryable work.
- Prefect or Airflow will orchestrate scheduled retraining and batch inference.
- Authentication is externalized through Clerk/Auth.js compatible JWTs.
- Every model decision should be explainable through persisted factors and evidence snippets.

## Production Concerns

- Multi-tenancy is enforced through `organization_id` on every domain aggregate.
- APIs require auth context and should be rate-limited per organization and user.
- Background tasks are idempotent and use database state transitions.
- Structured logs include `request_id`, `organization_id`, and `user_id`.
- Metrics are exported for latency, queue depth, task failures, ranking quality, and drift.
