# Docker Runtime Forensics

## Incident

The local virtual environment had the stabilized protobuf runtime, but the Docker worker crashed during startup:

```text
RuntimeError: Core dependency runtime is incompatible:
protobuf==5.29.6 violates >=6.31.1,<7.0.0
```

## Finding

The API and worker images were split:

- API container: `protobuf==6.31.1`, `grpcio==1.76.0`, `grpcio-tools==1.76.0`, `grpcio-status==1.76.0`
- Worker image before rebuild: `protobuf==5.29.6`

The worker image contained stale dependencies that are not part of the current worker runtime:

- `mlflow-skinny==2.19.0`
- `databricks-sdk==0.110.0`
- `opentelemetry-proto==1.29.0`

This confirmed the active failure was stale Docker image content, not the checked-in requirements.

## Cleanup Performed

The stale Docker state was removed:

- `docker compose -f docker-compose.yml down -v --remove-orphans`
- `docker compose -f docker-compose.dev.yml down -v --remove-orphans`
- Removed `resume-intelligence-api:latest`
- Removed `resume-intelligence-worker:latest`
- Pruned Docker builder cache
- Rebuilt API and worker with `docker compose -f docker-compose.yml build --no-cache api worker`

The builder prune reclaimed approximately 21 GB of stale layers.

## Runtime Fixes

`apps/api/Dockerfile` now performs a build-time runtime lock assertion after all dependency layers install:

- `protobuf==6.31.1`
- `grpcio==1.76.0`
- `grpcio-tools==1.76.0`
- `grpcio-status==1.76.0`

The image also creates a writable embedding cache:

- `/app/runtime/model-cache/huggingface`

This prevents semantic search from failing after the container drops to `appuser`.

## Compose Fixes

`docker-compose.yml` now gives the worker container-network URLs instead of relying on `.env` localhost defaults:

- `DATABASE_URL=postgresql+asyncpg://resume:resume@postgres:5432/resume_ai`
- `REDIS_URL=redis://redis:6379/0`
- `CELERY_BROKER_URL=redis://redis:6379/1`
- `CELERY_RESULT_BACKEND=redis://redis:6379/2`
- `QDRANT_URL=http://qdrant:6333`
- `S3_ENDPOINT_URL=http://minio:9000`

Worker healthchecks now use Celery ping instead of inheriting the API `/ready` healthcheck.

## Final Runtime State

Validated:

- API healthy.
- Worker healthy.
- Redis healthy.
- PostgreSQL healthy.
- Qdrant healthy.
- Celery connected to `redis://redis:6379/1`.
- Worker task round-trip returned a result.
- DOCX upload reached `embedded`.
- Semantic search returned ranked Qdrant results.
