# Onboarding Flow

## Entry

Users authenticate through the existing login or signup flow. After authentication, `/dashboard` performs a workspace activation check.

## Activation Check

Frontend endpoint:

- `GET /api/v1/workspace/activation`

The response determines whether to show onboarding or the command center.

Activation is true when the organization has recruiting intelligence such as candidates, resumes, or jobs.

## Empty State

If the workspace is empty, the user sees two activation paths:

- Upload resumes: routes to `/documents` and uses the existing `POST /api/v1/resumes/upload` pipeline.
- Load demo workspace: calls `POST /api/v1/workspace/demo`.

## Upload Path

The upload path remains connected to the stable ingestion stack:

1. Browser uploads PDF or DOCX through the resumes API.
2. Backend stores the file and creates a queued `Resume`.
3. Celery worker parses, extracts text, creates or updates candidate state, generates embeddings, and writes processing events.
4. The frontend polls resume status until it reaches `parsed`, `embedded`, or `failed`.

## Demo Path

The demo path seeds normal backend domain records for the authenticated organization:

- Candidates.
- Resumes.
- Jobs.
- Candidate skills.
- Candidate embeddings.
- Candidate matches.
- ATS scores.
- Pipeline stages.
- Resume processing events.
- Recruiter activity.

The dashboard then reloads activation state and becomes operational.
