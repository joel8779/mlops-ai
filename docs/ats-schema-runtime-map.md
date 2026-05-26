# ATS Schema Runtime Map

Date: 2026-05-26

## Intended ATS Architecture

ATS scoring is candidate/job scoped:

```text
candidates.id
  -> ats_scores.candidate_id

job_descriptions.id
  -> ats_scores.job_description_id

resumes.id
  -> ats_scores.resume_id
```

This preserves job-specific ATS scoring and avoids global resume-only scores.

## Runtime State Before Repair

`ats_scores` was resume-scoped only:

```text
ats_scores.resume_id -> resumes.id
resumes.candidate_id -> candidates.id
candidate_matches.candidate_id + candidate_matches.job_description_id -> job context
```

The effective candidate relation existed indirectly through `resume_id`.
The job relation lived in `candidate_matches`, not in `ats_scores`.

## Runtime State After Repair

`ats_scores` now carries direct job-context ATS fields:

- `candidate_id`
- `job_description_id`
- `resume_id`
- `ats_score`
- `components`
- `issues`
- `recommendations`
- `explanation`
- `scoring_version`

Post-repair validation:

- `ats_scores` rows: 6
- `ats_score_migration_archive` rows: 7
- rows missing candidate/job context: 0
- duplicate candidate/job ATS contexts: 0
- `pipelinestage` enum labels: `uploaded`, `ranked`, `shortlisted`, `interviewing`, `rejected`, `hired`

## Legacy Data Preservation

Older resume-scoped ATS rows were not discarded silently.

Duplicate rows that could not coexist with the candidate/job uniqueness contract were copied to:

```text
ats_score_migration_archive
```

The archive preserves:

- source ATS score id
- organization id
- resume id
- candidate id
- job description id
- score
- issues
- recommendations
- components
- explanation
- scoring version
- original timestamps
- archive reason
