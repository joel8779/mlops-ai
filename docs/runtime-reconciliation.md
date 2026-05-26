# Runtime Reconciliation

Date: 2026-05-26

## Confirmed Working Subsystems

- PostgreSQL connectivity
- Alembic at head after repair
- Redis connectivity
- Qdrant connectivity
- Candidate embeddings and vector indexing
- ATS candidate/job relation model
- Celery worker topology
- Candidate deletion cleanup
- Frontend TypeScript contract check

## Reconciled Contracts

### Schema

Runtime schema is validated against critical ORM assumptions:

- `ats_scores` candidate/job/resume fields
- candidate match fields
- pipeline/shortlist fields
- ranking feedback fields
- candidate embedding fields
- resume candidate linkage

Schema drift now makes readiness fail with a clear report, while startup logs a warning unless strict mode is enabled.

Strict startup mode:

```text
RUNTIME_SCHEMA_STRICT=true
```

### Health

- `/health`: process liveness
- `/live`: process liveness
- `/ready`: dependency and schema readiness
- `/api/v1/health/ready`: versioned readiness endpoint

### Frontend API

The frontend and config now agree on:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

Older `NEXT_PUBLIC_API_URL` remains supported as a fallback.

## Graceful Degradation

Gemini is treated as capability/configuration state rather than a hard startup dependency. Missing Gemini config degrades AI extraction quality but should not make liveness fail.

Readiness is strict for core infrastructure:

- PostgreSQL
- Redis
- Qdrant
- schema contract

## Remaining Operational Watchpoints

- Worker availability is not currently part of API readiness because workers may scale independently.
- OCR binary health is visible through diagnostics, but not a hard readiness dependency.
- Frontend aliases should be rationalized only after confirming no deployed links rely on them.
