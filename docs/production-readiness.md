# Production Readiness Audit

## Runtime
- Python is constrained to 3.11/3.12 because the ML stack depends on PyTorch wheels.
- FastAPI startup is import-verified in CI with route, worker, and observability checks.
- Celery tasks use late acknowledgements, worker-lost rejection, startup broker retries, and task time limits.

## Observability
- OpenTelemetry traces cover FastAPI, SQLAlchemy, Redis, HTTPX, Celery, AI orchestration, retrieval, and recommendations.
- Prometheus metrics expose API latency, LLM economics, retrieval latency, recommendation quality, websocket health, Redis stream lag, and ranking drift.
- Structured logs include correlation IDs and trace/span IDs for Loki-compatible querying.

## Resilience
- Circuit breaker, retry, fallback, and degradation primitives exist under `app.resilience`.
- Redis stream backpressure is visible through consumer lag metrics.
- Websocket cleanup updates active connection gauges and dropped-connection counters.

## Security
- CI includes Bandit, pip-audit, npm audit, and Trivy image/filesystem scans.
- Secrets are excluded from the repo and `.env.example` only contains local/example values.
- Production JWT, Stripe, Gemini, S3, and database credentials must come from secret managers.

## Deployment Safety
- Docker CI validates compose syntax, image build, image smoke checks, and critical vulnerability scans.
- Release flow validates semantic tags, migration state, builds an image artifact, and creates GitHub releases.
- Rollback preparation should pin deployed image tags and migration revisions before production deploy.

## Recovery Procedures
- API degradation can switch AI-heavy paths to retrieval-only or read-only modes.
- Redis lag alerts indicate queue saturation before data loss.
- LLM failure alerts should trigger fallback model routing or reduced-AI mode.

## Open Items
- Validate Docker Compose locally after Docker is installed.
- Execute full pytest under Python 3.11/3.12.
- Connect Alertmanager receivers to Slack/PagerDuty in production.
- Add signed images once registry and signing keys are finalized.
