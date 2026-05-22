# Implementation Roadmap

## Phase 1: Foundation

- Monorepo, Docker Compose, FastAPI, Postgres, Redis, Qdrant, MLflow.
- Auth middleware and organization-scoped API dependencies.
- Resume upload, object storage, async parsing task.
- Database schema and initial migrations.

## Phase 2: Parsing Intelligence

- PDF and DOCX text extraction.
- OCR for image resumes.
- Skill extraction and ontology normalization.
- Candidate profile generation.
- Duplicate detection by email, phone, normalized name, and embedding similarity.

## Phase 3: Search and Matching

- Resume and job embedding pipeline.
- Qdrant collections for candidates and job descriptions.
- Semantic search API.
- Candidate-job matching model with explainability factors.
- ATS scoring and ranking views.

## Phase 4: Recruiter Product

- Next.js dashboard.
- Hiring pipelines, notes, comments, status updates.
- Candidate comparison and interview question generation.
- Email notifications.
- Analytics dashboard.

## Phase 5: MLOps

- MLflow experiments and model registry.
- Feature store tables.
- Batch inference and retraining orchestration.
- A/B testing for ranking models.
- Feedback loop and active learning.
- Bias/fairness and drift dashboards.

## Phase 6: Production Hardening

- CI/CD gates.
- Prometheus and Grafana dashboards.
- Structured logging and ELK export.
- Rate limiting, retries, secrets management.
- Vercel, Railway/Render, and Docker service deployments.
