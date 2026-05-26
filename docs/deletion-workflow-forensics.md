# Deletion Workflow Forensics

Date: 2026-05-26

## Failure

Candidate deletion failed during ATS cleanup because the service used the current ORM model against an older runtime table:

```sql
DELETE FROM ats_scores WHERE ats_scores.candidate_id = ...
```

The older table only had `resume_id`, so PostgreSQL raised `UndefinedColumnError`.

## Repair

The delete workflow now checks the real runtime table shape before ATS deletion:

- If `ats_scores.candidate_id` exists, delete ATS rows by candidate.
- If not, delete ATS rows through the candidate's linked resume ids.

This makes deletion resilient during schema drift and rolling migration windows.

## Candidate Cleanup Order

The workflow removes:

1. Qdrant candidate vector points.
2. ATS score rows.
3. Candidate/job match rows.
4. Pipeline and shortlist rows.
5. Bookmarks and recruiter notes.
6. Ranking feedback analytics rows.
7. Candidate skills.
8. Candidate embedding metadata.
9. Resume processing events.
10. Recruiter activity candidate references.
11. Resume candidate links.
12. Candidate soft-delete marker.

The DB cleanup is rollback-protected. If relational cleanup fails, the DB transaction rolls back.

## Validation

A synthetic candidate deletion test was run against local PostgreSQL after migration repair.

Result:

- `ats_scores`: 0 rows for deleted candidate/resume
- `candidate_matches`: 0
- `candidate_pipeline_stages`: 0
- `candidate_bookmarks`: 0
- `recruiter_notes`: 0
- `ranking_feedback`: 0
- `candidate_skills`: 0
- `candidate_embeddings`: 0
- `resume_processing_events`: 0
- recruiter activity candidate references: 0
- Qdrant candidate point deletion path called
- candidate no longer appears in normal candidate queries because `deleted_at` is set
