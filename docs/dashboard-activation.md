# Dashboard Activation

Dashboard panels must use real backend state.

## Real Signals

- active jobs
- ranked candidates
- recent uploads
- semantic match records
- ATS pipeline stats
- resume processing events
- recruiter actions
- top skills
- match averages

## Empty States

Panels may be empty when the underlying backend records do not exist. Do not fill charts with fake values.

## Current Data Sources

- `GET /api/v1/workspace/activation`
- `GET /api/v1/analytics/executive`
- `CandidateMatch`
- `ATSScore`
- `ResumeProcessingEvent`
- `RecruiterActivity`
- `CandidateSkill`
- `CandidatePipelineStage`

## Activation Rule

The dashboard becomes meaningfully active when the workspace has jobs, resumes, candidates, matches, or recruiter activity. The strongest state is a job with ranked candidates and job-context ATS scores.
