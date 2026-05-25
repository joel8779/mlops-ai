# Recruiting Intelligence Runtime

NEURAL OPS runtime flow:

1. Resume upload stores the document, creates a `Resume`, and queues `resume.parse`.
2. Resume worker extracts text through `ExtractionService`, resolves identity, extracts skills, writes candidate profile data, generates embeddings, upserts Qdrant candidate points, and records `ResumeProcessingEvent`.
3. JD upload/extract parses the JD document, infers title, extracts requirements, writes `JobDescription`, and queues JD vector indexing.
4. Matching ranks candidates for a specific job and persists `CandidateMatch`.
5. ATS scoring generates `ATSScore` for `candidate_id + job_description_id + resume_id`.
6. Recruiter feedback updates both `RankingFeedback` and per-job `CandidatePipelineStage`.
7. Analytics reads real runtime tables: candidates, resumes, jobs, matches, ATS scores, workflow stages, skills, and recruiter activities.

Runtime ownership:

- Gemini: structured extraction, recruiter summaries, explanations, gap analysis, semantic reasoning.
- Embeddings + Qdrant: retrieval and semantic similarity.
- ATS scoring: deterministic job-context scoring engine, optionally explained by Gemini later.
- PostgreSQL: source of truth for candidates, jobs, matches, ATS scores, workflow stages, analytics.
- Celery: document/JD processing outside the request path.

Non-negotiable product rule:

ATS scores are never global candidate scores. They only exist for a candidate relative to a job.

Workflow state contract:

- `uploaded`
- `ranked`
- `shortlisted`
- `interviewing`
- `rejected`
- `hired`

Frontend hydration rule:

Pages should use backend intelligence outputs directly and should not fabricate analytics, raw vector payloads, or placeholder recruiter data.
