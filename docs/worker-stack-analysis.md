# Worker Stack Analysis - Phase 24.3

Date: 2026-05-25

## Decision

Restore distributed async execution in two layers:

1. Celery + Redis for task queue execution.
2. Prefect 3 local flow execution as an optional orchestration layer.

No OCR, GPU packages, training frameworks, MLflow, or distributed Prefect infrastructure are enabled in this phase.

## Celery / Redis Findings

The stable core runtime already includes:

| Package | Pin |
| --- | ---: |
| `celery[redis]` | `5.4.0` |
| `redis` | `5.2.1` |
| `websockets` | `13.1` |

PyPI metadata for Celery 5.4.0 lists Python 3.11 support and supports Redis as broker/result backend through the `redis` extra. The app uses separate Redis DBs:

| Purpose | Setting | Default |
| --- | --- | --- |
| API/cache | `REDIS_URL` | `redis://localhost:6379/0` |
| Broker | `CELERY_BROKER_URL` | `redis://localhost:6379/1` |
| Result backend | `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` |

For Windows local validation, use Celery's `solo` pool. This avoids process-fork assumptions and keeps worker validation deterministic.

## Prefect Findings

Prefect 3 is optional. PyPI currently describes Prefect as Python 3.10+ with Python 3.11 support. For Phase 24.3, Prefect is limited to direct local flow calls. No Prefect server, cloud, work pools, Kubernetes, Dask, Ray, or distributed cluster mode is introduced.

`app.pipelines.prefect_flows` now degrades gracefully if Prefect is not installed. Flow functions remain callable as plain Python functions, and `PREFECT_AVAILABLE` exposes whether the real decorators are active.

The validation harness uses explicit local runners for Prefect-decorated tasks. This avoids blocking on a Prefect API server when `PREFECT_API_URL` points at a stopped local server.

Installed orchestration package:

| Package | Version |
| --- | ---: |
| `prefect` | `3.1.12` |
| `click` | `8.1.8` |
| `packaging` | `24.2` |
| `pytz` | `2024.2` |

## Runtime Isolation

- API startup does not start a worker.
- Worker startup imports Celery tasks but does not parse resumes or load embedding models.
- Embedding model loading remains lazy inside task execution.
- Redis connection failures are reported by diagnostics, not by API startup.
- Prefect import failures degrade to plain function execution.
- Celery tracing remains optional and fails closed.

## Validation Commands

Dependency and Redis-only:

```powershell
.\.venv\Scripts\python.exe scripts\test_worker_runtime.py --dependency-only
```

Start a local Celery worker and run broker/result validation:

```powershell
.\.venv\Scripts\python.exe scripts\test_worker_runtime.py --start-worker
```

Run worker DB and vector probes:

```powershell
.\.venv\Scripts\python.exe scripts\test_worker_runtime.py --start-worker --with-db --with-embeddings
```

Validate local Prefect flow execution:

```powershell
.\.venv\Scripts\python.exe scripts\test_worker_runtime.py --with-prefect
```

Full Phase 24.3 validation:

```powershell
.\.venv\Scripts\python.exe scripts\test_worker_runtime.py --start-worker --with-db --with-embeddings --with-prefect
```

## Validation Results

Completed on 2026-05-25:

| Check | Result |
| --- | --- |
| `pip check` | Pass |
| Protobuf / gRPC guard | `protobuf==6.31.1`, `grpcio==1.76.0`, `grpcio-tools==1.76.0`, `grpcio-status==1.76.0` |
| Redis broker ping | Pass |
| Celery worker startup | Pass with Windows `solo` pool |
| Task dispatch/result backend | Pass via `worker.ping` |
| Failure-path handling | Pass via expected `worker.expected_failure` failure |
| Worker DB update probe | Pass |
| Worker embedding generation | Pass, 384-dimensional vector |
| Qdrant vector insertion/search | Pass in `candidate_embeddings` |
| Prefect local flow validation | Pass with `prefect==3.1.12` |
| FastAPI startup smoke test | Pass: `/health`, `/ready`, `/docs`, `/openapi.json` returned 200 |

## References

- PyPI Celery: https://pypi.org/project/celery/
- PyPI Redis: https://pypi.org/project/redis/
- PyPI Prefect 3.1.12: https://pypi.org/project/prefect/3.1.12/
- Prefect 3 flow docs: https://docs.prefect.io/v3/concepts/flows
