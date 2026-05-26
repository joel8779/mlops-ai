# Alembic Integrity Audit

Date: 2026-05-26

## Revision State

Before repair:

```text
runtime revision: 0003_enterprise_scale
code head:        0005_pipeline_stage_contract
```

After repair:

```text
runtime revision: 0005_pipeline_stage_contract
code head:        0005_pipeline_stage_contract
```

## Pending Migrations

The runtime database had not applied:

- `0004_job_context_ats`
- `0005_pipeline_stage_contract`

This explained both ATS schema drift and the old pipeline enum labels.

## Migration Risk Found

The original `0004_job_context_ats` assumed a clean migration path and deleted ATS rows that could not be backfilled.

That was unsafe because the live DB had legacy resume-scoped ATS rows and duplicate score rows for the same inferred candidate/job context.

## Migration Repair

`0004_job_context_ats` now:

- Checks for existing columns, indexes, constraints, and foreign keys before creating them.
- Adds ATS candidate/job fields idempotently.
- Backfills candidate context from `resumes`.
- Backfills job context from the strongest `candidate_matches` record.
- Archives duplicate legacy ATS rows into `ats_score_migration_archive`.
- Creates the candidate/job uniqueness constraint only after duplicates are archived.
- Avoids deleting ATS data without preserving it.

## Startup Integrity Check

The API now validates critical schema assumptions at startup:

- expected Alembic head
- required ATS columns
- candidate/job/resume foreign keys
- candidate match columns
- shortlist pipeline columns
- feedback analytics columns
- semantic embedding metadata columns

If drift is detected, startup raises a clear `Runtime PostgreSQL schema drift detected` error before user workflows fail at runtime.
