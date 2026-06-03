# Technical Debt Summary

Code-level debt:
- Analytics had mixed owner/org scoping; dashboard metrics were corrected, but remaining owner-based services should be reviewed feature by feature.
- Prompt manager contains legacy templates beyond the current allowed Gemini scope.
- Frontend lint script is stale for Next.js 15 and requires an ESLint migration.
- Health test fixture naming is inconsistent.
- Some services still contain broad exception handling; critical paths should log structured causes and re-raise where appropriate.

Migrations added in current workspace:
- `0007_add_organization_pin.py`
- `0008_add_otp_verification.py`

Validation results:
- Passed: `python -m pytest app/tests/test_email_service.py app/tests/test_otp_service.py app/tests/test_analytics_stage_counts.py app/tests/test_ai_summary.py app/tests/test_job_intelligence.py`
- Passed: `python -m compileall app`
- Passed: `npm exec tsc -- --noEmit`
- Blocked: `npm run lint` because ESLint is not installed.
- Blocked: `test_health.py` because `async_client` fixture is missing.

