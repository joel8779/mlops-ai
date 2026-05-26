# Environment Consistency Audit

Date: 2026-05-26

## Environment Sources Audited

- `.env`
- `.env.example`
- `docker-compose.yml`
- `docker-compose.dev.yml`
- `docker-compose.prod.yml`
- `apps/api/app/core/config.py`
- `apps/web/lib/api.ts`
- `apps/web/next.config.js`
- Kubernetes manifests under `infra/k8s`
- production compose under `infra/docker`

## Reconciled Variables

Added to `.env` and `.env.example`:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
RUNTIME_SCHEMA_STRICT=false
```

Frontend config now exposes `NEXT_PUBLIC_API_BASE_URL` and keeps `NEXT_PUBLIC_API_URL` fallback compatibility.

## Local vs Container URLs

Local host runtime:

```text
DATABASE_URL=postgresql+asyncpg://resume:resume@localhost:5432/resume_ai
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
S3_ENDPOINT_URL=http://localhost:9000
```

Docker service runtime:

```text
DATABASE_URL=postgresql+asyncpg://resume:resume@postgres:5432/resume_ai
REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333
S3_ENDPOINT_URL=http://minio:9000
```

Compose files override local `.env` URLs with container-network URLs for API and worker services.

## Parser Hardening

`DEBUG=release` is now interpreted as `false`. This protects deployment shells that use `DEBUG=release` or similar values from breaking Pydantic settings loading.

## Secret Handling

The active `.env` contains real secret values. Keep it out of commits and do not paste it into issue trackers, logs, or docs.

`.env.example` remains the deployable template with placeholders.

## Remaining Differences

`.env.example` includes optional observability keys not present in active `.env`:

- `JAEGER_AGENT_HOST`
- `JAEGER_AGENT_PORT`

Those are optional because OTLP is the primary configured tracing path.
