# ORM / PostgreSQL Schema Drift Analysis

Date: 2026-05-26

## Summary

Candidate deletion failed because the API ORM expected `ats_scores.candidate_id`, but the live PostgreSQL schema was still at Alembic revision `0003_enterprise_scale`.

The codebase had already advanced to the job-context ATS model introduced by `0004_job_context_ats`:

- `ats_scores.candidate_id`
- `ats_scores.job_description_id`
- `ats_scores.components`
- `ats_scores.explanation`
- unique candidate/job ATS score constraint
- job-score index

The runtime database had not applied `0004` or `0005`, so `ats_scores` remained resume-scoped.

## Confirmed Runtime Drift

Before repair:

- Alembic runtime revision: `0003_enterprise_scale`
- Alembic code head: `0005_pipeline_stage_contract`
- Runtime `ats_scores` columns:
  - `organization_id`
  - `resume_id`
  - `ats_score`
  - `issues`
  - `recommendations`
  - `scoring_version`
  - `id`
  - timestamps
- Missing ORM-required columns:
  - `candidate_id`
  - `job_description_id`
  - `components`
  - `explanation`

## True Cause

This was migration drift, not a Qdrant, Docker, or runtime infrastructure failure.

The delete workflow executed ORM SQL equivalent to:

```sql
DELETE FROM ats_scores WHERE ats_scores.candidate_id = ...
```

PostgreSQL rejected it because the live table had no `candidate_id` column.

## Repair

The live database was upgraded to Alembic head:

```text
0005_pipeline_stage_contract
```

`0004_job_context_ats` was hardened to be idempotent and non-destructive:

- Adds missing ATS candidate/job columns only when absent.
- Backfills `candidate_id` from `resumes`.
- Backfills `job_description_id` from the strongest `candidate_matches` row.
- Preserves duplicate legacy ATS rows in `ats_score_migration_archive`.
- Enforces candidate/job uniqueness only after duplicates are archived.

## Guardrail

Startup now validates critical ORM/runtime schema alignment and fails loudly if required columns or foreign keys are missing.
