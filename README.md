# AI Resume Intelligence Platform

Production-grade AI hiring infrastructure for resume ingestion, parsing, semantic search, ranking, recruiter workflows, and MLOps-managed model iteration.

## Architecture

- `apps/web`: Next.js recruiter workspace.
- `apps/api`: FastAPI API gateway and domain API.
- `services/workers`: Celery workers for parsing, embeddings, notifications, and batch inference.
- `services/ml`: training, evaluation, MLflow model registration, and ranking services.
- `infra`: Docker, monitoring, and deployment configuration.
- `docs`: system design, API, ML, and operating guides.

## First Vertical Slice

This scaffold starts with:

- FastAPI backend with async SQLAlchemy.
- PostgreSQL schema for organizations, users, jobs, candidates, resumes, notes, events, and ranking artifacts.
- JWT-ready auth dependency with Clerk/Auth.js compatible claims.
- Resume upload endpoint with content validation.
- S3-compatible local storage abstraction.
- Celery task hook for async resume parsing.
- Docker Compose for Postgres, Redis, Qdrant, MLflow, Prometheus, Grafana, API, and worker.

## Local Development

```bash
cp .env.example .env
docker compose up --build
```

API docs: `http://localhost:8000/docs`

## Product Roadmap

See [docs/architecture.md](docs/architecture.md) and [docs/roadmap.md](docs/roadmap.md).
