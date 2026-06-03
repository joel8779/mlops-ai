# Changelog

All notable changes to the AI Resume Intelligence Platform are documented in this file.

---

## [1.0.0] - 2026-06-03

### Added
- **Security Hardening**:
  - Redis-backed sliding window rate-limiting for critical authentication and upload routes (e.g. `/login`, `/register`, `/send-otp`, `/upload`).
  - Strict file-type header validation verifying magic bytes for uploads (rejecting extensions renamed to bypass scanner).
  - OpenTelemetry monthly budget controls and queue throttling ($100 budget limit and concurrent requests pool).
- **Recruiter OTP & Forgot Password Flows**:
  - Implemented `/forgot-password`, `/verify-reset-otp`, and `/reset-password` API endpoints backed by Redis lifecycle management.
  - Implemented OTP verification logic on registration schemas.
  - SMTP connection support with implicit SSL/STARTTLS and safe console logging fallback during local testing.
- **Database Optimizations**:
  - Created composite indices on `candidate_pipeline_stages(organization_id, deleted_at, stage)` to speed up dashboard analytics queries.
  - Database schema validations and alembic migrations integration checks at API startup.
- **Next.js Middleware Refactor**:
  - Support for silent token refreshing in frontend middleware when the access token has expired but the refresh token remains active.
- **Release Packaging**:
  - Docker parity load balancing setups with horizonal scaling Nginx proxy configuration.
  - Deployment configuration setups for Vercel, Railway, Neon, and Cloudflare.
  - Portfolio release documentation (`README.md`, `LICENSE`, `REPO_AUDIT.md`, `RELEASE_NOTES.md`).

### Fixed
- Next.js build errors by securing `.gitkeep` placeholders on empty web directories.
- Alembic database migration discrepancies in startup validation.
- Experience classification rules to score candidate profile timeline years rather than relying purely on title keywords.
