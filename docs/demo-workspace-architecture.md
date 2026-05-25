# Demo Workspace Architecture

## Goal

The demo workspace gives a new user a realistic recruiting command center without pretending that frontend-only metrics exist.

## Endpoint

`POST /api/v1/workspace/demo`

The endpoint is organization-scoped and idempotent. If demo candidates already exist for the organization, it returns the current activation state instead of duplicating records.

## Seeded Records

The demo loader writes ordinary domain records:

- Active job descriptions for backend, ML retrieval, and product engineering roles.
- Five realistic candidates with role, location, summary, and skill profiles.
- Embedded resume records with extracted text and parser metadata.
- Candidate skill rows.
- Candidate embedding rows.
- Candidate match rows with score components and explanations.
- ATS score rows with issues and recommendations.
- Candidate pipeline stages.
- Resume processing events for OCR, embedding generation, and semantic indexing.
- Recruiter activity events for matching, ranking, semantic readiness, and shortlist recommendations.

## Vector Indexing

The loader attempts to upsert deterministic demo vectors into Qdrant using the existing embedding service client and configured collection name.

If Qdrant is unavailable, the demo still commits PostgreSQL state and records the Qdrant status in `demo.workspace_loaded` activity payload. This keeps the demo path from destabilizing backend startup or worker runtime.

## Design Constraint

The demo workspace is not a replacement for ingestion. It is an activation bridge that makes the product understandable while preserving the real upload, OCR, parsing, embedding, and search workflows.
