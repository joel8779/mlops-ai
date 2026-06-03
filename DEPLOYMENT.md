# Production Deployment Guide

This guide details the step-by-step instructions to deploy the AI Resume Intelligence Platform to production services.

## Infrastructure Target Architecture

*   **Frontend**: Vercel (Next.js App Router)
*   **Backend**: Railway (FastAPI + Celery Workers)
*   **Database**: Neon (Serverless PostgreSQL)
*   **Cache & Message Broker**: Upstash (Serverless Redis)
*   **Vector Search**: Qdrant Cloud (Managed Vector database)

---

## 1. Database Provisioning (Neon)

1.  Sign in to [Neon Console](https://console.neon.tech/).
2.  Create a new project named `resume-intelligence`.
3.  Choose your region (e.g., US East) and PostgreSQL version (16).
4.  Copy the connection string (with pooled connection pooling `postgres://...` for API connection, and direct string for migrations).
    *   **Direct URL (Migrations)**: `postgresql+psycopg://alex:password@ep-cool-snowflake-123456.us-east-2.aws.neon.tech/neondb`
    *   **Pooled URL (App)**: `postgresql+asyncpg://alex:password@ep-cool-snowflake-123456-pooler.us-east-2.aws.neon.tech/neondb`

---

## 2. Redis Provisioning (Upstash)

1.  Sign in to [Upstash Console](https://console.upstash.com/).
2.  Create a Redis Database with SSL enabled.
3.  Copy the SSL Redis URL (e.g. `rediss://default:password@useful-panda-12345.upstash.io:6379`).
4.  Configure three separate databases or use keyspaces. For isolation:
    *   **Rate Limits / Session Cache**: `rediss://.../0`
    *   **Celery Broker**: `rediss://.../1`
    *   **Celery Results**: `rediss://.../2`

---

## 3. Vector Database (Qdrant Cloud)

1.  Sign in to [Qdrant Cloud Console](https://cloud.qdrant.io/).
2.  Provision a free-tier cluster.
3.  Create an API key.
4.  Copy the cluster URL (e.g. `https://xxxx-xxxx-xxxx.aws.qdrant.io:6333`) and API key.

---

## 4. Backend Deployment (Railway)

1.  Create a new project on [Railway](https://railway.app/).
2.  Connect your GitHub repository.
3.  Deploy the backend directory (`apps/api`):
    *   Create a service for the **FastAPI API** with start command:
        `alembic upgrade head && uvicorn app.main:create_app --factory --host 0.0.0.0 --port ${PORT} --workers 4`
    *   Create a second service for the **Celery Worker** with start command:
        `celery -A app.workers.celery_app.celery_app worker --loglevel=INFO --concurrency=4`
4.  Configure the environment variables (see `production.env.example`).

---

## 5. Frontend Deployment (Vercel)

1.  Create a new project on [Vercel](https://vercel.com/).
2.  Connect your GitHub repository and select the `apps/web` folder as root.
3.  Vercel automatically detects Next.js.
4.  Set the environment variables:
    *   `NEXT_PUBLIC_API_URL`: Your Railway API URL (e.g. `https://api.yourdomain.com`)
5.  Deploy the frontend.

---

## 6. Post-Deployment Verification

1.  Run the health probe on the backend:
    `curl -i https://your-railway-api.up.railway.app/ready`
2.  Test login, registration, password reset, and resume uploading via the Vercel frontend.
