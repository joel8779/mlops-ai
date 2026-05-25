# Semantic Ranking Repair

Problem observed:

- Ranking could collapse to `0 job fit` when Qdrant or embedding search returned no semantic hits.
- Search UX must return candidate intelligence, not vector chunks.
- Frontend job-context candidate lists received `candidate_id`, while parts of the candidates page expected `id`.

Repairs applied:

- `MatchingService.rank_candidates` now degrades around embedding/Qdrant failure instead of failing ranking outright.
- Matching uses a lexical/skill fallback semantic score when vector retrieval returns no hit for a candidate.
- Ranking persists per-job `CandidateMatch` and marks candidates as `ranked` for that job.
- `SemanticSearchService.search` already aggregates hits by candidate and hydrates name, ATS alignment, matched skills, missing skills, summary, and reasoning.
- Candidates page now resolves `candidate.id || candidate.candidate_id`, so job-ranked candidates can be opened, shortlisted, and deleted correctly.

Expected search result shape:

- candidate name
- ATS/job alignment when job context exists
- semantic overlap
- matched skills
- missing skills
- recruiter-ready summary
- experience alignment
- overlap reasoning

Remaining work:

- Add integration coverage for empty Qdrant, unavailable embedding model, and mixed candidate/job contexts.
- Add richer Gemini-generated recruiter summaries after deterministic candidate aggregation.
