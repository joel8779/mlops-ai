# Phase 44 - Post-Embedding Pipeline Forensics

Phase 44 conclusion:

The platform is past the infrastructure failure layer. Upload, Celery, embeddings, Qdrant indexing, ATS similarity, and semantic ranking are operational. The remaining failures are post-processing persistence and hydration failures.

Repairs applied:

- Candidate identity can no longer remain `Candidate Profile`; deterministic fallback now derives identity from header, email, filename, metadata, regex, or final imported name.
- Candidate read/list endpoints repair stale `Candidate Profile` records from linked resume text without invoking Gemini on list views.
- Resume DB persistence now has an explicit `db_persistence` trace stage.
- SQLAlchemy errors now include table/schema/constraint/statement/params summary/stack trace in structured error details.
- PDF extraction default page limit increased from 5 to 20.
- PDF extraction truncates to configured pages instead of hard failing on longer JDs.
- Candidate deletion now uses one DB transaction for relational cleanup before best-effort Qdrant/storage cleanup.
- Added candidate relation audit endpoint for post-ATS persistence footprint.

Backend diagnostics:

- `/api/v1/diagnostics/runtime`
- `/api/v1/diagnostics/qdrant`
- `/api/v1/diagnostics/candidates/{candidate_id}/relations`
- `/api/v1/resumes/{resume_id}/diagnostics`

Candidate deletion cleanup now covers:

- ATS scores
- candidate matches
- pipeline/shortlist stages
- bookmarks
- recruiter notes
- ranking feedback
- skills
- embedding metadata
- resume processing events
- recruiter activity candidate references
- soft-deleted candidate and linked resumes
- best-effort Qdrant point deletion
- best-effort storage object deletion

Validation performed:

- `python -m compileall apps/api/app` passed.
- API import passed with `DEBUG=false`.
- Identity fallback probe no longer returns `Candidate Profile` or a skills line as the candidate name.

Remaining runtime validation:

- Upload a 7+ page JD and confirm it extracts first 20 pages instead of failing.
- Open candidate diagnostics after ATS generation and verify `candidate_matches`, `ats_scores`, `pipeline_stages`, and `candidate_embeddings` counts.
- Delete a candidate and verify relation counts drop to zero and semantic search skips the deleted candidate.
