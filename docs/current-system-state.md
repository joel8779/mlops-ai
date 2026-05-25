# Neural Ops Current System State

Neural Ops is an AI recruiting intelligence platform, not a generic ATS or job scraping product. The current product flow is landing, auth, dashboard, JD creation/upload, resume upload, AI processing, semantic matching, explainable ATS scoring, and recruiter workflows.

## Backend

The backend is a FastAPI service with PostgreSQL, Redis/Celery, Qdrant, S3-compatible object storage, OCR/document extraction, embeddings, auth, analytics, and recruiter workflow APIs.

Important existing surfaces:

- Jobs: `POST /api/v1/jobs`, `POST /api/v1/jobs/upload`, `GET /api/v1/jobs`, `GET /api/v1/jobs/{id}`, `DELETE /api/v1/jobs/{id}`
- Resumes: `POST /api/v1/resumes/upload`, `GET /api/v1/resumes`, `GET /api/v1/resumes/{id}`, `DELETE /api/v1/resumes/{id}`
- Candidates: `GET /api/v1/candidates`, `GET /api/v1/candidates/{id}`, `DELETE /api/v1/candidates/{id}`
- Matching: `POST /api/v1/matching/rank`
- ATS: `POST /api/v1/ats/jobs/{job_id}/candidates/{candidate_id}/score`
- Analytics/workspace activation surfaces are already used by the dashboard.

## Intelligence Implemented

- JD text and JD file upload create `JobDescription` records.
- JD parsing extracts skills, education terms, experience ranges, role category, and keywords.
- JD indexing runs asynchronously through Celery and writes Qdrant job embeddings.
- Resume upload stores files, queues parsing, extracts text, creates candidates, extracts skills, embeds resumes, and indexes Qdrant candidate vectors.
- Matching combines semantic score, skill match, experience, education, keyword fit, and recruiter preferences.
- ATS scoring is now job-contextual and returns component-level explanations, issues, recommendations, and candidate-job fit evidence.
- Candidate identity extraction now avoids `Unnamed Candidate` and falls back to `Candidate Profile`.

## Frontend

The Next.js frontend has auth, app shell, sidebar, dashboard, documents, jobs, candidates, search, analytics, and settings routes. It uses real backend APIs and empty states rather than fake metrics.

Recent operational UX additions:

- JD upload on Jobs.
- Resume/document delete on Documents.
- Candidate delete on Candidates.
- Job delete on Jobs.
- Candidate labels now use `Candidate Profile` instead of `Unnamed`.

## Stability Boundaries

Do not casually refactor protobuf/gRPC, embeddings, workers, OCR, Docker runtime, auth, or semantic search. Changes should be incremental and backed by focused tests.
