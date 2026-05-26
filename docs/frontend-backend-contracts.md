# Frontend / Backend Contracts

Date: 2026-05-26

## API Base URL

Frontend API client:

```text
apps/web/lib/api.ts
```

Primary variable:

```text
NEXT_PUBLIC_API_BASE_URL
```

Default:

```text
http://localhost:8000/api/v1
```

Legacy fallback:

```text
NEXT_PUBLIC_API_URL
```

## Main Workflow Contracts

Documents:

- `GET /api/v1/resumes`
- `POST /api/v1/resumes/upload`
- `GET /api/v1/resumes/{id}`
- `DELETE /api/v1/resumes/{id}`

Jobs:

- `GET /api/v1/jobs`
- `POST /api/v1/jobs`
- `POST /api/v1/jobs/upload`
- `POST /api/v1/jobs/extract`
- `GET /api/v1/jobs/{id}`
- `GET /api/v1/jobs/{id}/intelligence`
- `DELETE /api/v1/jobs/{id}`

Candidates:

- `GET /api/v1/candidates`
- `GET /api/v1/candidates/{id}`
- `DELETE /api/v1/candidates/{id}`

Search and scoring:

- `POST /api/v1/search/candidates`
- `POST /api/v1/matching/rank`
- `POST /api/v1/ats/jobs/{job_id}/candidates/{candidate_id}/score`
- `POST /api/v1/feedback/ranking`

Dashboard and analytics:

- `GET /api/v1/workspace/activation`
- `POST /api/v1/workspace/demo`
- `GET /api/v1/analytics/executive`

## Hydration Notes

Candidate list and job intelligence views hydrate from different surfaces:

- global candidate list uses candidate records, skills, resume status, and best match
- job context uses job intelligence rankings, ATS scores, matches, and pipeline stage

Deletion now updates UI progress and reloads the active context after cleanup.

## Contract Risks To Monitor

- Resume upload is async; frontend must poll resume status before assuming embeddings exist.
- Job indexing is async; job ranking may work before job vector indexing completes, but semantic job-vector features depend on worker completion.
- If workers are down, upload endpoints return saved queued records with failure metadata when enqueue fails.
