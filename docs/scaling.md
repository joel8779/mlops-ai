# Scaling Strategy

- API scales horizontally behind Kubernetes HPA.
- Celery workers scale independently for parsing, OCR, embedding, and indexing.
- Qdrant collections are tenant-filtered by organization and can be sharded by tenant tier.
- Redis Streams provide retryable event workflows and dead-letter capture.
- Read-heavy analytics are served from aggregated snapshots.
- MLflow model registry separates training cadence from online inference rollout.
