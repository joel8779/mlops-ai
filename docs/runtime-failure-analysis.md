# Runtime Failure Analysis - Phase 43

Phase 43 focused on backend runtime failures, not frontend design.

Confirmed root causes addressed:

- Resume worker failures were collapsed into one generic `resume.parse_failed` event.
- Candidate extraction persisted only narrow identity/skills, so failures produced `Candidate Profile` and empty skill state.
- ATS rows were only generated through a manual endpoint, so job intelligence could rank candidates without persisted ATS scores.
- Semantic search depended on Qdrant/embedding success and had no database-backed fallback.
- Database failures returned a generic message without constraint category or next action.

Repairs applied:

- Added `PipelineTrace` for stage-level resume processing events.
- Added recruiter-safe failure classification for OCR, Gemini, embedding, Qdrant, parser, and DB persistence failures.
- Added structured resume diagnostics endpoint: `/api/v1/resumes/{resume_id}/diagnostics`.
- Added runtime diagnostics endpoint: `/api/v1/diagnostics/runtime`.
- Added Qdrant payload validation endpoint: `/api/v1/diagnostics/qdrant`.
- Added real candidate extraction service with Gemini-first support and deterministic fallback.
- Expanded candidate profile persistence: name, email, phone, skills, education, experience, projects, seniority, summary.
- Expanded JD parsing: required skills, preferred skills, technologies, seniority, semantic requirements, summary.
- Job intelligence now ensures ATS scores are generated for ranked candidates.
- Semantic search now degrades to DB-backed candidate intelligence when vector search fails.

Important local blocker:

- Current `.env` has `DEBUG=release`; API startup requires boolean `DEBUG=false` or `DEBUG=true`.

Verification:

- `python -m compileall apps/api/app` passed.
- API import passed with `DEBUG=false`.
- Candidate extraction probe returned `Jane Doe`, email, skills, and `mid` seniority.
- JD extraction probe returned required/preferred technology signals and seniority.
- Docker runtime is up: API, worker, Postgres, Redis, Qdrant, MinIO, MLflow are healthy.
- Worker logs show repeated OTLP export failures to `localhost:4317`; this is observability noise, but it can obscure real worker task errors and should be disabled or pointed at a live collector.
