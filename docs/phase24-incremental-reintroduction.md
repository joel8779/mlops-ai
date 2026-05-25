# Phase 24 - Incremental Feature Reintroduction

**Date**: 2026-05-25  
**Rule applied**: Introduce one layer, run the startup gate, and stop at the first regression.

## Layer 1 - Redis And Qdrant

**Status**: Passed.

Redis and Qdrant clients were already installed through `requirements-core.txt`. Only the service containers were started:

```powershell
docker compose up -d redis qdrant
```

Two runtime blockers were isolated and minimally corrected:

- The Qdrant Compose health check used `wget`, which is not present in `qdrant/qdrant:v1.12.6`. Both Compose files now use an installed `bash` HTTP probe for `/healthz`.
- `app/api/v1/routes/health.py` read raw `REDIS_URL` and `QDRANT_URL` environment variables. It now uses the existing validated `settings` values, consistent with the rest of the API.

Layer validation:

```text
postgres container                    healthy
redis container                       healthy
qdrant container                      healthy
/health                               200
/docs                                 200
/api/v1/health/ready                  ready
ready dependencies                    postgres, redis, qdrant healthy
/api/v1/auth/login (invalid creds)    401
semantic route imported               True
embeddings enabled                    False
uvicorn startup                       Application startup complete
pip check                             No broken requirements found.
```

## Layer 2 - Gemini

**Status**: Blocked and rolled back.

Only the existing Gemini layer was attempted:

```powershell
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: --no-cache-dir -r apps\api\requirements-ai.txt
```

First blocker:

```text
google-generativeai==0.8.3 pulled protobuf==5.29.6 and grpcio-status==1.71.2.
grpcio-tools==1.76.0 requires protobuf>=6.31.1,<7.0.0.
```

This breaks the already validated core gRPC/protobuf runtime. The Gemini installation was removed immediately and `requirements-core.txt` was reinstalled to restore:

```text
protobuf==6.31.1
grpcio-status==1.76.0
pip check: No broken requirements found.
```

No Gemini request, retry validation, or AI route activation was performed because the dependency layer failed before its startup gate.

## Deferred Layers

The following layers were not attempted because Layer 2 did not pass:

- sentence-transformers / embeddings
- torch validation
- OCR extraction

They remain protected by the existing graceful-degradation behavior.

## Current Stable State

The restored environment is stable with PostgreSQL, Redis, and Qdrant enabled. Gemini, sentence-transformers, torch, OCR, and MLflow are not installed in `.venv`.

The next blocker to resolve is a dependency-compatible Gemini SDK strategy that does not downgrade the core protobuf/gRPC pins.
