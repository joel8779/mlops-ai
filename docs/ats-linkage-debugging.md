# ATS Linkage Debugging

ATS remains job-specific.

Required relationship:

- `candidate_id`
- `job_description_id`
- `resume_id`

Repair applied:

- `JobIntelligence` now calls ranking when no match rows exist.
- After ranking, backend generates missing ATS rows for the top ranked candidates.
- ATS scoring reuses the persisted `CandidateMatch.semantic_score` when available.
- Matching persists a per-job `CandidatePipelineStage` with stage `ranked`.
- Recruiter feedback persists per-job stages: `shortlisted`, `interviewing`, `rejected`, `hired`.

Validation checklist:

- Candidate has at least one embedded resume row in `candidate_embeddings`.
- Job has at least one embedded JD row in `job_description_embeddings`.
- `candidate_matches` has a row for candidate and job.
- `ats_scores` has a row for candidate, job, and resume.
- `/api/v1/jobs/{job_id}/intelligence` returns `ats_score` or a nonzero `overall_score`.
- `/api/v1/diagnostics/runtime` reports nonzero ATS and embedding counts after pipeline completion.

Common failure signatures:

- `0 job fit`: no candidate match, no ATS row, or resume text/skills were not persisted.
- Empty job intelligence: JD parse/index failed or no candidate embeddings exist.
- Missing ATS score but nonzero match: ATS generation has not run or failed on resume lookup.
