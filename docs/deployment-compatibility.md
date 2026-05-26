# Deployment Compatibility

Date: 2026-05-26

## Preserved Targets

The stabilization preserves:

- Local Docker Compose
- Docker Compose dev stack
- Docker Compose production profile
- External managed PostgreSQL/Redis/Qdrant deployments
- Vercel-style frontend deployments
- Railway/Render-style API deployments
- Kubernetes manifests under `infra/k8s`

No deployment directory or Docker support was removed.

## Docker Compose Behavior

Compose API services now run:

```sh
alembic upgrade head && uvicorn ...
```

This fixes the confirmed schema drift class where containers start against an old volume and the ORM assumes newer columns.

## Container Readiness

Compose healthchecks now target `/ready` instead of plain liveness where appropriate. This prevents API and worker startup from racing ahead before:

- PostgreSQL responds
- Redis responds
- Qdrant responds
- Alembic schema head is present
- critical runtime columns/FKs exist

## Cloud Deployments

The Dockerfile default command remains a normal Uvicorn command. Cloud platforms can still use:

- release-phase migrations
- platform-specific build/start commands
- managed environment variables
- external DB/Redis/Qdrant URLs

`docker-compose.prod.yml` runs migrations before API startup because it is an orchestrated Docker runtime, not a platform release phase.

## Frontend

The frontend runtime API base is:

```text
NEXT_PUBLIC_API_BASE_URL
```

Fallback compatibility remains for older `NEXT_PUBLIC_API_URL`.

Recommended values:

- Local browser: `http://localhost:8000/api/v1`
- Docker browser against local API: `http://localhost:8000/api/v1`
- Vercel/cloud frontend: `https://<api-domain>/api/v1`

## Secrets

The active `.env` contains real secret material and must remain local-only. `.env.example` contains placeholders and deployment-safe defaults.
