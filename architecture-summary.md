# Architecture Summary

The system is a multi-tenant recruiting intelligence platform with a FastAPI backend, Next.js frontend, PostgreSQL persistence, Redis/Celery background workers, Qdrant vector search, Gemini-assisted summaries/JD extraction, and Docker deployment support.

Core boundaries:
- Backend: `apps/api/app` owns auth, tenancy, ingestion, ATS, analytics, search, LLM, SMTP, workers, and health checks.
- Frontend: `apps/web` owns auth hydration, route guarding, dashboards, candidate/job workflows, and API calls.
- Deployment: Docker Compose remains present for local and production-style runs, with Postgres, Redis, Qdrant, MinIO, Celery, Prometheus, Loki, and Grafana support.

Current hardening changes keep the existing organization model, Celery worker flow, Qdrant indexing, Docker stack, OTP flow, ATS engine, semantic search, and Gemini summary/JD features intact.

Validated in this pass:
- SMTP config validation and masked health state.
- OTP resend cooldown and expiry env support.
- Auth cleanup for expired/invalid browser tokens.
- Same-organization dashboard metric sharing.
- Gemini prompts constrained against fabricated years, seniority, skills, and scores.

