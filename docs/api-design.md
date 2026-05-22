# API Design

## Authentication

All business endpoints require a Bearer JWT. In local development, `AUTH_DEV_BYPASS=true` injects a deterministic development user and organization.

## Initial Endpoints

- `GET /health`: process health.
- `GET /api/v1/me`: current auth context.
- `POST /api/v1/resumes/upload`: upload one resume and enqueue parsing.
- `GET /api/v1/resumes/{resume_id}`: fetch resume processing state.

## Future Endpoints

- `POST /api/v1/jobs`: create job description.
- `POST /api/v1/jobs/{job_id}/rank`: rank candidates.
- `GET /api/v1/search/candidates`: semantic candidate search.
- `POST /api/v1/candidates/{candidate_id}/notes`: recruiter notes.
- `POST /api/v1/candidates/{candidate_id}/interview-questions`: generated interview questions.
- `GET /api/v1/analytics/funnel`: hiring pipeline analytics.
