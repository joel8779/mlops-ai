# Vector Indexing Report

Vector architecture remains in place:
- Candidate and job embeddings are persisted in PostgreSQL metadata tables.
- Qdrant collections are configured through environment variables.
- Celery workers continue to index resumes and job descriptions asynchronously.
- Delete service retains vector cleanup responsibilities.

Deployment readiness notes:
- Local Compose includes Qdrant health checks.
- Production deployment should use Qdrant Cloud with `QDRANT_URL` and `QDRANT_API_KEY`.
- Worker startup must be deployed separately from the API on Railway/Render.

Not live-validated in this pass:
- Qdrant Cloud connectivity.
- End-to-end vector cleanup against a live Qdrant instance.

