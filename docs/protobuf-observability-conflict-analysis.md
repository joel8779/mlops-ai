# Protobuf Observability Conflict Analysis - PHASE 27

Date: 2026-05-25

## Executive Summary

The backend runtime is standardized on:

- `protobuf==6.31.1`
- `grpcio==1.76.0`
- `grpcio-tools==1.76.0`
- `grpcio-status==1.76.0`

The conflict came from `opentelemetry-exporter-otlp==1.29.0`, which pulls `opentelemetry-proto==1.29.0`. Pip resolver forensics confirmed that `opentelemetry-proto==1.29.0` requires `protobuf>=5,<6`, directly conflicting with the stable protobuf 6 runtime.

## Root Cause

- `requirements-core.txt` pinned OpenTelemetry API/SDK at `1.29.0`.
- `requirements-observability.txt` pinned `opentelemetry-exporter-otlp==1.29.0`.
- Docker wheel and runtime install commands did not pass `-c constraints.txt`.
- `apps/api/Dockerfile` still preinstalled `grpcio==1.60.0` and `protobuf==4.25.1` before building wheels.
- Legacy recovery scripts still recommended protobuf 4.x.
- Docker protobuf forensics also exposed `mlflow-skinny==2.19.0`, pulled by `mlflow==2.19.0`, requiring `protobuf<6`.

## Resolution

- Preserve protobuf/gRPC pins in `requirements-core.txt` and `constraints.txt`.
- Upgrade the OpenTelemetry family together:
  - `opentelemetry-api==1.42.1`
  - `opentelemetry-sdk==1.42.1`
  - `opentelemetry-exporter-otlp==1.42.1`
  - `opentelemetry-proto==1.42.1`
  - instrumentation packages `==0.63b1`
- Add explicit OpenTelemetry constraints so Docker, CI, and local installs resolve the same set.
- Remove Docker bootstrap pins for grpc/protobuf 1.60/4.25.
- Apply `-c constraints.txt` to Docker wheel builds and runtime installs.
- Add `pip check` to the Docker runtime layer.
- Exclude MLflow from stable runtime layers; keep it deferred/training-only until an MLflow line compatible with protobuf 6 is selected.
- Keep the API Docker image on runtime layers only: core, observability, AI, embeddings, OCR, and worker orchestration. Do not install broad training/MLOps requirements into the API image.

## Stability Policy

Telemetry is optional. Runtime stability wins over exporter completeness.

- OpenTelemetry API/SDK remain in core because tracing modules import them.
- OTLP exporters live in the observability layer.
- Exporter initialization is already deferred and catches failures in `app/observability/tracing/exporters.py`.
- FastAPI startup must continue if OTLP exporter import or initialization fails.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pip install --dry-run -r apps\api\requirements-observability.txt -c apps\api\constraints.txt
.\.venv\Scripts\python.exe -m pip check
$env:DEBUG='false'; .\.venv\Scripts\python.exe scripts\test_gemini_runtime.py --dependency-only
$env:DEBUG='false'; .\.venv\Scripts\python.exe scripts\test_worker_runtime.py --dependency-only
$env:DEBUG='false'; .\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'apps/api'); import app.main; print('api_startup_import_ok')"
docker build -f apps/api/Dockerfile apps/api
```

## Expected Outcome

- No package may resolve `protobuf<6`.
- No package may resolve `grpcio<1.76`.
- OpenTelemetry exporters resolve on a protobuf 6-compatible line.
- Gemini, Qdrant/gRPC, embeddings, workers, and FastAPI startup remain stable.
