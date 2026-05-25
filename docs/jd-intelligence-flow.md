# JD Intelligence Flow

## Current Flow

1. Recruiter creates a JD by pasting text or uploading a PDF/DOCX.
2. `JobIntelligenceService` extracts text for uploads through the document extraction service.
3. The parser extracts skills, experience ranges, education requirements, role category, and keywords.
4. A `JobDescription` record is created in PostgreSQL.
5. A Celery task indexes the JD asynchronously.
6. `EmbeddingService` chunks the JD, generates embeddings, writes Qdrant points, and records `JobDescriptionEmbedding` rows.
7. Matching uses the JD description and parsed requirements to rank candidates.

## Backend Objects

- `JobDescription`: canonical JD record and parsed intelligence fields.
- `JobDescriptionEmbedding`: chunk-level embedding metadata and Qdrant point IDs.
- `CandidateMatch`: persisted match results for a candidate and JD.

## Operational Signals To Surface

- JD parsed successfully.
- Required and optional skills extracted.
- Experience/education requirements extracted.
- Embedding chunks created.
- Qdrant indexing completed.
- Candidate matches generated.

## Next Improvements

- Persist richer metadata in `metadata_json`.
- Add JD processing events, similar to resume processing events.
- Add a JD detail screen that shows parsed intelligence and matching readiness.
