# SMTP Configuration Guide

Required environment variables:
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `OTP_EXPIRY_MINUTES`
- `OTP_RATE_LIMIT_SECONDS`

Optional SMTP tuning:
- `SMTP_USE_TLS=true`
- `SMTP_TIMEOUT_SECONDS=10`
- `SMTP_RETRY_ATTEMPTS=3`
- `SMTP_RETRY_BACKOFF_SECONDS=5`
- `OTP_RATELIMIT_WINDOW_SECONDS=3600`
- `OTP_RATELIMIT_MAX_REQUESTS=5`

Behavior:
- Startup logs `smtp_configured` only when all required SMTP fields are present.
- Missing config logs `smtp_not_configured` with secret-safe masking and exposes SMTP as `disabled`.
- `/smtp-health` verifies SMTP connectivity with `NOOP`.
- `/ready` includes SMTP state but does not mark the API unready when SMTP is disabled, allowing graceful startup.
- OTP sends and shortlist email paths fail explicitly in logs when SMTP delivery fails; secrets are not logged.

Production recommendation:
- Use provider app passwords or SMTP credentials stored in Railway/Render secrets.
- Use a verified `SMTP_FROM_EMAIL` domain.
- Monitor `smtp_email_send_failed`, `smtp_health_check_failed`, and OTP rate-limit events.

