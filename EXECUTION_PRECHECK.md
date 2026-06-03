# Execution Precheck

Pre-execution state audit of the ATS platform.

## 1. Git Status
- Active modifications in:
  - `.env.example`
  - `apps/api/app/` (various routes, services, models)
  - `apps/web/` (middleware, components, pages)
- Untracked files:
  - `apps/api/alembic/versions/` (versions 0007, 0008, 0009)
  - `apps/api/app/services/` (email, OTP, password reset services)
  - `apps/api/app/tests/` (OTP, email, extraction, password reset tests)

## 2. Migration Head
- Current head in repository: `0009_recruiter_workflow_completion` (complete recruiter auth and email workflow).

## 3. Docker Status
- Docker daemon is **not running** (failed to connect to the Docker API). This is a known local environment setup constraint.

## 4. Failing Tests
- 0 failing tests. All 38/38 unit tests pass successfully.

## 5. Existing Environment Variables
- Core configs parsed from environment:
  - `LLM_PROVIDER`: `gemini`
  - `GEMINI_API_KEY`: present
  - `DATABASE_URL`: local PostgreSQL asyncpg URL
  - `REDIS_URL`: `redis://localhost:6379/0`
  - `SMTP_PORT`: `587`
  - `SMTP_HOST`: `smtp.gmail.com`

## 6. Known Blockers
- The Docker daemon is not active, which means direct Docker-based verification must rely on static/local verification and unit-test mocking.
