# Rollback and Disaster Recovery Plan

This document details the emergency rollback procedures for the AI Resume Intelligence Platform in the event of a critical post-deployment failure.

## 1. Rollback Triggers

Initiate rollback procedures if any of the following conditions are met:
1.  **API Crash Loop**: API service fails to start or healthcheck `/ready` returns `503 Service Unavailable` for > 3 minutes.
2.  **Auth Failures**: Core user flows (signup, OTP verification, login) fail completely.
3.  **Data Corruption**: Migration execution fails or causes database locks that degrade system performance.

---

## 2. Frontend Rollback (Vercel)

Vercel stores all historical deployments, allowing for instant rollback:

1.  Navigate to the project dashboard on Vercel.
2.  Click on the **Deployments** tab.
3.  Locate the last known stable deployment (prior to the current failing release).
4.  Click the vertical ellipsis (...) next to the stable deployment and select **Promote to Production**.
5.  Vercel will redirect production traffic to the stable build instantly without rebuilding.

---

## 3. Backend API & Worker Rollback (Railway)

To roll back the backend API and worker services on Railway:

1.  Navigate to the service dashboard in Railway.
2.  Click on the **Deployments** tab.
3.  Locate the previous stable deployment.
4.  Click **Redeploy** to roll back container images and restore the stable state.
5.  Ensure both the `api` and `worker` services are reverted to the same deployment.

---

## 4. Database Rollback

### Reverting Schema Migrations
If the new schema migration needs to be reverted:
1.  Connect to the database via direct (non-pooled) URL.
2.  Downgrade the schema by 1 version:
    ```bash
    alembic downgrade -1
    ```

### Neon Point-in-Time Recovery (PITR)
If data corruption occurred:
1.  Navigate to the **Branches** tab in Neon Console.
2.  Click **Create Branch** and select **Point in Time**.
3.  Specify the timestamp of a known healthy state prior to the deployment.
4.  Update the application env variables (`DATABASE_URL` and `SYNC_DATABASE_URL`) to point to the new healthy database branch.

---

## 5. Cache / Redis Recovery (Upstash)

If rate limits are locked or Celery tasks are hung after a rollback:
1.  Flush the Celery task queue in Upstash:
    ```bash
    # Clear Redis db 1 (Celery broker)
    redis-cli -u rediss://default:<upstash_password>@<upstash_host>.upstash.io:6379/1 FLUSHDB
    ```
2.  Clear rate limit counters to unblock users:
    ```bash
    # Clear Redis db 0 (Rate limits / cache)
    redis-cli -u rediss://default:<upstash_password>@<upstash_host>.upstash.io:6379/0 KEYS "rate:*" | xargs redis-cli -u rediss://default:<upstash_password>@<upstash_host>.upstash.io:6379/0 DEL
    ```
