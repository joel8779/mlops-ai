# Docker Startup Analysis

Date: 2026-05-26

## Previous Risk

Docker volumes can preserve an older PostgreSQL schema while newer API containers boot with newer ORM models.

This caused:

```text
UndefinedColumnError: ats_scores.candidate_id does not exist
```

## Startup Order

Local/dev compose order:

```text
postgres healthy
redis healthy
qdrant healthy
minio healthy + bucket init
api runs alembic upgrade head
api starts uvicorn
api /ready reports healthy
worker starts after api healthy
```

Dev compose also waits on Neo4j because the dev topology includes graph infrastructure.

## Healthcheck Split

- API liveness: `/health`
- API readiness: `/ready`
- Worker health: Celery ping
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- Qdrant: `/healthz`
- MinIO: `mc ready`

## Stabilization Changes

- `docker-compose.yml` API command runs Alembic before Uvicorn.
- `docker-compose.dev.yml` API command runs Alembic before Uvicorn.
- `docker-compose.prod.yml` API command runs Alembic before Uvicorn.
- Main compose API healthcheck now uses `/ready`.
- API readiness includes schema drift validation.

## Deployment Safety

The image-level Dockerfile `CMD` remains Uvicorn only, so platforms with release phases can run migrations explicitly. Compose files own compose-specific migration timing.
