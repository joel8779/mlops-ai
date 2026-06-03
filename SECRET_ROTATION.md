# Secret Rotation Guide

This document was generated as part of the pre-release security validation.

## 1. Audit Summary
A strict audit of the active workspace and the full commit history (32 commits) was conducted using signature analysis.
- **Result**: **No leaks detected**.
- All detected patterns match either development placeholders (e.g., `your-gemini-api-key`, `your-jwt-secret-key`) or default local connection strings (e.g., `postgresql://resume:resume@postgres:5432/resume_ai`). No production secrets are present in the repository.

---

## 2. Standard Secret Rotation Policy
If production credentials are ever accidentally committed or need periodic updates, use the following procedures:

### Google Gemini API Key
1. Generate a new API key in the [Google AI Studio Console](https://aistudio.google.com/).
2. Update the environment variables in your deployment manager (e.g., Railway, Vercel, or Kubernetes Secret Config):
   ```bash
   GEMINI_API_KEY=AIzaSy...newkey...
   ```
3. Restart the backend API gateway service to refresh memory cache.
4. Revoke the old key in the Google AI Studio console.

### Database Credentials
1. Change the user password in your hosted database instance (e.g. Neon, RDS).
2. Update the database URL configuration on the backend API service:
   ```bash
   DATABASE_URL=postgresql+asyncpg://user:new_password@host:5432/dbname
   SYNC_DATABASE_URL=postgresql+psycopg://user:new_password@host:5432/dbname
   ```
3. Redeploy/restart the backend gateway and worker nodes to apply the new connection pool.

### JWT Token Signature Key
1. Generate a new 32-byte hexadecimal secret key:
   ```bash
   openssl rand -hex 32
   ```
2. Update the secret key variable:
   ```bash
   JWT_SECRET_KEY=new_secret_hex...
   ```
3. Restart the services. Note that rotating this key will invalidate all active recruiter login sessions, forcing users to log in again.
