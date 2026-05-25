# Job Context Ranking

Candidate ranking is meaningful only inside a selected job.

## Correct Workflow

Jobs -> open job -> ranked candidates -> ATS for that job -> shortlist/reject.

## Ranking Sort

Inside a job, candidates sort by:

1. ATS score if generated, otherwise match overall score.
2. Semantic similarity.
3. Experience fit.

## Surfaces

- `GET /api/v1/jobs/{job_id}/intelligence`
- `/jobs/[id]`
- `/candidates` with a selected job context

The global candidate page is a dossier list only. It does not display global ATS scores.
