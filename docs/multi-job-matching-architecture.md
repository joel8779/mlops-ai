# Multi-Job Matching Architecture

Neural Ops now treats recruiting intelligence as job-centric.

## Core Relationships

- A job has many candidate matches.
- A candidate can match many jobs.
- ATS scoring belongs to a candidate and a job.
- Candidate ranking inside a job is sorted by job-specific fit, not upload chronology.

## Runtime Objects

- `JobDescription`: canonical job description and parsed JD intelligence.
- `Candidate`: canonical person/profile record.
- `Resume`: uploaded source document and extracted text.
- `CandidateMatch`: semantic and structured match between one candidate and one job.
- `ATSScore`: job-context ATS score for one candidate and one job.

## Ranking Order

Inside a job, candidates are ranked by:

1. Job-context ATS score when it exists, otherwise match overall score.
2. Semantic similarity.
3. Experience fit.

This supports the correct multi-job behavior: the same candidate can score highly for one role and weakly for another.

## APIs

- `GET /api/v1/jobs/{job_id}/intelligence`: job intelligence page data, ranked candidates, and semantic insights.
- `POST /api/v1/matching/rank`: generate candidate matches for a selected job.
- `POST /api/v1/ats/jobs/{job_id}/candidates/{candidate_id}/score`: generate explainable ATS score for a candidate-job pair.

The old global resume ATS route now rejects requests because ATS without a JD is misleading.
