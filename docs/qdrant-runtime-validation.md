# Qdrant Runtime Validation

Qdrant responsibilities:

- Store candidate resume vectors in `candidate_embeddings`.
- Store JD vectors in `job_description_embeddings`.
- Preserve metadata needed to aggregate vector hits back into candidate/job intelligence.

Candidate payload contract:

- `organization_id`
- `candidate_id`
- `resume_id`
- `chunk_index`
- `text`
- `model`
- optional profile metadata such as `skills`, `full_name`, `headline`, `location`, `education`

Job payload contract:

- `organization_id`
- `job_description_id`
- `job_id`
- `chunk_index`
- `text`
- `model`

Repair applied:

- JD Qdrant payloads now include both `job_description_id` and `job_id`.
- Runtime diagnostics expose Qdrant collection counts.
- `/api/v1/diagnostics/qdrant` validates required metadata fields from sample payloads.

Validation checklist:

- Candidate upload completes with `resume.embedding_indexing.success`.
- JD upload/index completes with job metadata `indexing.status = embedded`.
- Qdrant candidate collection contains points with `candidate_id`.
- Qdrant job collection contains points with `job_description_id` and `job_id`.
- Semantic search returns candidate-level aggregates, not raw vector chunks.
