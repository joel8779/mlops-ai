# ATS Job Context Design

ATS scores in Neural Ops are relative to a job description.

## Rule

Do not compute ATS scores globally for a resume. A score only exists for:

`candidate_id + job_description_id`

The `resume_id` remains attached as source evidence, but the scoring context is the selected job.

## Current Components

The job-context ATS engine combines:

- Semantic similarity.
- Skill weighting.
- Experience fit.
- Education fit.
- Keyword match.
- Resume parse quality signals.

Each score returns:

- `ats_score`
- component scores and evidence
- matched skills
- missing skills
- recommendations
- explanation

## Persistence

`ATSScore` now stores:

- `candidate_id`
- `job_description_id`
- `resume_id`
- `components`
- `issues`
- `recommendations`
- `explanation`

`CandidateMatch` remains the ranking surface. ATS scoring updates the candidate-job match record so recruiter views stay consistent.
