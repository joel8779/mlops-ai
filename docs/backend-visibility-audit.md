# Backend Visibility Audit

## Preserved Stable Systems

Phase 35 does not modify the core ingestion, auth, Docker, OCR, Celery, Redis, Qdrant, protobuf, gRPC, or embedding runtime paths.

The new backend surface is additive:

- `GET /api/v1/workspace/activation`
- `POST /api/v1/workspace/demo`

## Backend State Exposed

The activation endpoint reads:

- PostgreSQL candidates from `candidates`.
- Jobs from `job_descriptions`.
- Resume state from `resumes`.
- ATS scoring state from `ats_scores`.
- Semantic match state from `candidate_matches`.
- Resume processing activity from `resume_processing_events`.
- Recruiter workflow activity from `recruiter_activities`.

## Frontend Consumers

The dashboard uses activation as its source of truth for:

- Whether onboarding should be shown.
- Operational counts.
- Pipeline state.
- Activity feed.
- Match insights.
- Next best actions.

The semantic search page continues to use the existing `/search/candidates` endpoint and now explains the backend ranking path.

Phase 36 removed the frontend Copilot route and navigation item. Backend AI summary, comparison, and interview endpoints remain available for candidate workflows, but `/copilot` is no longer part of the authenticated frontend route map.

## Remaining Gaps

Some advanced operational signals are still indirect:

- Redis queue depth is not yet exposed as a first-class API field.
- Qdrant collection health is only attempted during demo indexing and not reported as continuous health.
- Worker execution metrics remain primarily in observability dashboards rather than product UI.

Recommended next backend-safe additions:

- Read-only worker queue status endpoint.
- Read-only vector index health endpoint.
- SSE or WebSocket bridge from existing notification manager into the dashboard activity feed.
