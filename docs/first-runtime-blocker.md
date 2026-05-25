# First Runtime Blocker - Phase 23

**Captured**: 2026-05-25  
**Environment**: Newly recreated Python 3.11.9 `.venv` with only `apps/api/requirements-core.txt` installed.

## Startup Command

Run from `apps/api`:

```powershell
..\..\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --reload
```

## First Real Error

```text
File "C:\Users\Lenovo\Desktop\mlops-ai\apps\api\app\main.py", line 7, in <module>
    from prometheus_fastapi_instrumentator import Instrumentator
ModuleNotFoundError: No module named 'prometheus_fastapi_instrumentator'
```

## Classification

- Blocker type: missing optional observability dependency imported unconditionally during core startup.
- Reason it is first: `prometheus_fastapi_instrumentator` is imported at module load before settings, routers, middleware, ML, or database checks execute.
- Intended minimal resolution: allow the existing metrics instrumentation path to be absent during a core-only boot, without installing the deferred observability layer.

## Pre-Cleanup Baseline Note

Before recreating `.venv`, the previously populated environment reached a later settings-validation error caused by ambient `DEBUG=release`. That prior error remains preserved in `docs/current-runtime-state.md`; it is not the first blocker in the clean core-only environment.

## Incremental Recovery Record

| First blocker after each run | Minimal resolution |
| --- | --- |
| `prometheus_fastapi_instrumentator` missing in `app/main.py` | Made only optional metrics instrumentation conditional. |
| Ambient `DEBUG=release` fails boolean settings validation | Ran validation with `DEBUG=false`; repository `.env` already has a valid boolean. |
| `prometheus_client` missing on required route import path | Moved its existing pin into `requirements-core.txt`. |
| `structlog` missing on startup logging path | Moved its existing pin into `requirements-core.txt`. |
| `opentelemetry` API and SDK missing on mandatory trace-context imports | Moved only the API and SDK pins into `requirements-core.txt`. |
| OTLP exporter import required a protobuf-conflicting deferred package | Deferred its import until the exporter is selected at runtime. |
| `fitz` missing through job/resume upload imports | Deferred `ExtractionService` imports to the methods/tasks that execute OCR parsing. |
| Database unavailable for `/health` and auth | Started only the existing PostgreSQL Compose service. |
| Alembic enum types created twice in revisions `0001`-`0003` | Marked the four explicitly created enum objects with `create_type=False`. |

## Result

The API reaches `Application startup complete` with the clean Python 3.11 `.venv` and no ML/OCR/Gemini packages installed. With PostgreSQL started and migrated to `0003_enterprise_scale (head)`:

```text
/live                         200
/health                       200
/docs                         200
/api/v1/auth/login            401 (expected for invalid credentials)
auth routes declared          True
pip check                     No broken requirements found.
```

Startup validation uses `DEBUG=false` because the invoking process currently supplies the invalid generic environment value `DEBUG=release`.
