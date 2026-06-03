# Deployment Readiness Report

Target deployment:
- Frontend: Vercel.
- Backend API: Railway or Render.
- Worker: Railway or Render background worker.
- Database: Neon Postgres.
- Redis: Upstash Redis.
- Qdrant: Qdrant Cloud.

Required runtime variables:
- `DATABASE_URL`
- `SYNC_DATABASE_URL`
- `REDIS_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `JWT_SECRET_KEY`
- `GEMINI_API_KEY`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `OTP_EXPIRY_MINUTES`
- `OTP_RATE_LIMIT_SECONDS`
- `BACKEND_CORS_ORIGINS`
- `FRONTEND_URL`
- `NEXT_PUBLIC_API_BASE_URL`

Readiness:
- Docker deployment support remains intact.
- API `/ready`, `/health`, `/live`, and `/smtp-health` are available.
- Alembic startup remains in Docker command.
- Celery worker command remains intact.

Production readiness score: 82/100.

Recommended deployment sequence:
1. Provision Neon, Upstash, Qdrant Cloud, SMTP provider, and Gemini credentials.
2. Deploy API with migrations enabled.
3. Deploy Celery worker using the same backend image and env.
4. Deploy frontend on Vercel with `NEXT_PUBLIC_API_BASE_URL`.
5. Run smoke tests for auth, OTP, upload, ATS, search, summaries, dashboards, and deletion.
6. Enable monitoring alerts after the first successful smoke pass.

Recommended monitoring stack:
- Prometheus metrics from `/metrics`.
- Grafana dashboards.
- Loki or provider log drains.
- Sentry for frontend/backend exceptions.
- Uptime checks for `/health`, `/ready`, and `/smtp-health`.

Recommended GitHub Actions setup:
- Backend: install Python deps, run `pytest`, `compileall`, Alembic head check, import validation.
- Frontend: `npm ci`, `npm exec tsc -- --noEmit`, `npm run build`.
- Security: pip-audit, npm audit policy, Trivy image scan.
- Docker: build API and web images, run Compose health smoke when services are available.

