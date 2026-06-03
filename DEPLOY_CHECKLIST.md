# Production Deployment Checklist

Follow this checklist before and during the release of the AI Resume Intelligence Platform to production.

## 1. Pre-Deployment Configuration

- [ ] **DNS Setup**
  - [ ] Configure custom domain (e.g., `app.yourdomain.com`) in Vercel.
  - [ ] Configure API subdomain (e.g., `api.yourdomain.com`) in Railway pointing to the API service.
  - [ ] Ensure SSL certificates are active for both domains.

- [ ] **SMTP / Email Delivery**
  - [ ] Set up a production SMTP relay (e.g., SendGrid, Mailgun).
  - [ ] Verify sender domain with SPF, DKIM, and DMARC DNS records.
  - [ ] Verify SendGrid API key and populate `SMTP_PASSWORD`.
  - [ ] Set `SMTP_USE_TLS=false` (port 465 SSL) or `SMTP_USE_TLS=true` (port 587 TLS).

- [ ] **Authentication (Clerk)**
  - [ ] Switch Clerk to production mode.
  - [ ] Configure allowed redirect URLs to point to Vercel custom domain (`https://app.yourdomain.com/dashboard`).
  - [ ] Retrieve Clerk Production Publishable Key and Secret Key.

- [ ] **Redis (Upstash)**
  - [ ] Create Upstash Redis instance with TLS enabled.
  - [ ] Verify connection URLs start with `rediss://` (secure SSL connection).
  - [ ] Configure maximum memory policy to `allkeys-lru`.

- [ ] **Vector Database (Qdrant Cloud)**
  - [ ] Provision a production Qdrant Cloud cluster.
  - [ ] Retrieve cluster URL and API key.
  - [ ] Verify target collection exists with size **384** vectors using the Cosine distance metric.

---

## 2. Release Phase

- [ ] **Secrets Audit**
  - [ ] Audit Railway and Vercel dashboards to ensure no local database passwords, local SMTP credentials, or default test keys are present.
  - [ ] Verify `JWT_SECRET_KEY` is set to a secure, cryptographically random 64-character hex string.

- [ ] **Database Migrations**
  - [ ] Run Alembic database migrations:
    ```bash
    alembic upgrade head
    ```
  - [ ] Verify the `alembic_version` table is successfully populated with the `0010_composite_indexes` revision.

- [ ] **Container Build**
  - [ ] Verify Docker images compile successfully without local environment dependency warnings.
  - [ ] Scale FastAPI service (`api`) to at least 2 instances for redundancy.
  - [ ] Deploy Celery workers (`worker`) as a separate service in Railway.

---

## 3. Post-Release Health Checks

- [ ] Check `/ready` and `/live` endpoints on the production domain:
  ```bash
  curl -i https://api.yourdomain.com/ready
  ```
  Ensure it returns `200 OK` with database, cache, and vector store connections reported as healthy.

- [ ] Run a test signup and log in with a real email address to verify SMTP OTP delivery.
- [ ] Test resume upload to ensure Magic Number security checks and parsing tasks are completed.
- [ ] Verify Celery worker active pings:
  ```bash
  celery -A app.workers.celery_app.celery_app inspect ping
  ```
