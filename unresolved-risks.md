# Unresolved Risks

- Live SMTP delivery was not validated because real credentials were not available in this pass.
- Live Redis/Postgres/Qdrant/Celery/Docker health was not exercised here.
- `npm run lint` is blocked because `next lint` requires ESLint, which is not installed in `apps/web`.
- `app/tests/test_health.py` still references an `async_client` fixture that does not exist; the available fixture is `test_client`.
- Server-side refresh-token revocation is not implemented.
- Some recruiter-agent Gemini tools still exceed the strict allowed Gemini responsibility list and should be product-gated if required.
- Production secrets must be rotated away from local defaults before deployment.

