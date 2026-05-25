# Recruiting Intelligence Roadmap

## Priority 1: JD Intelligence

- Deepen JD parsing beyond keyword heuristics: responsibilities, must-have skills, nice-to-have skills, seniority, domain, compensation hints, location, work mode, and screening criteria.
- Persist richer parsed JD metadata in `JobDescription.metadata_json`.
- Add a JD intelligence detail view showing extracted requirements and embedding/index status.

## Priority 2: Explainable ATS Scoring

- Continue evolving ATS components from format-only scoring into job-aware scoring.
- Add a job-context scoring route that compares a resume against a selected JD.
- Persist component explanations in a dedicated JSON field or scoring artifact table.

## Priority 3: Semantic Matching

- Keep the current hybrid matching service as the canonical path.
- Add persisted match detail views with score components, matched evidence snippets, and missing critical requirements.
- Add reranking when recruiter feedback data is available.

## Priority 4: Candidate Identity

- The extraction hierarchy is implemented in `CandidateIdentityExtractor`.
- Next step: add optional NER/LLM identity extraction ahead of deterministic fallbacks when the model provider is configured.
- Add test coverage for headers, email fallback, filename fallback, and the final `Candidate Profile` fallback.

## Priority 5: Delete Workflows

- Soft-delete jobs, resumes, and candidates through API routes.
- Cleanup now includes SQL relationships, Qdrant points, uploaded resume files, matches, ATS scores, processing events, and activity references.
- Next step: add audit log entries for delete actions and idempotency tests.

## Priority 6: Operational Dashboard

- Expand workspace activation with JD indexing status, queue depth, failed worker events, recent ATS scores, and match generation state.
- Avoid fake charts. Every metric must come from PostgreSQL, Qdrant, Redis, Celery, or explicit empty states.

## Priority 7: Upload Orchestration UX

- Documents already show upload progress and resume processing status.
- Next step: show worker event timeline from `ResumeProcessingEvent` and JD indexing completion from `JobDescriptionEmbedding`.
