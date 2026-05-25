# Living System UX

Phase 35 shifts Neural Ops from a styled dashboard into a visible recruiting operating system.

## Product Principle

The UI should never imply intelligence without backend evidence. Dashboard panels now activate from `/api/v1/workspace/activation`, which reads PostgreSQL-backed candidates, jobs, resumes, ATS scores, semantic matches, resume processing events, and recruiter activity.

## Activated Experience

After workspace data exists, the dashboard shows:

- Real candidate, job, embedded resume, and semantic match counts.
- Resume pipeline state across uploaded, queued, parsing, parsed, embedded, and failed.
- Operational activity from `resume_processing_events` and `recruiter_activities`.
- Semantic match insights from `candidate_matches`.
- Recent backend objects from the candidates and resumes APIs.
- Next best actions derived from current backend state.

## Empty Workspace Experience

An empty organization does not see a dead dashboard. The dashboard shows:

> Welcome to Neural Ops. Import candidate intelligence to activate your workspace.

Primary actions:

- Upload resumes through the existing ingestion workflow.
- Load demo workspace through the new backend demo seed endpoint.

## AI Visibility

The product now names concrete backend operations in the interface:

- OCR completed.
- Embedding generated.
- Semantic index ready.
- Candidate matched.
- AI ranking completed.
- Shortlist recommendation generated.

These are represented as persisted backend events rather than frontend-only decorations.
