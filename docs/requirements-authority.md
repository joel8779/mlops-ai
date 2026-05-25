# Requirements Authority - Phase 23

**Captured**: 2026-05-25  
**Scope**: Backend startup recovery only. No dependency redesign is authorized by this audit.

## Selected Bootstrap Authority

Use exactly one requirements input for the clean core boot attempt:

```text
apps/api/requirements-core.txt
```

Install command:

```powershell
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: --no-cache-dir -r apps/api/requirements-core.txt
```

This is the existing file explicitly labelled as the first runtime layer and it is the file directed by Phase 23. It is authoritative for the recovery bootstrap only. Its inclusion of Redis, Celery, gRPC, Neo4j, and Qdrant means it is not a perfectly minimal HTTP-only set; changing that boundary before observing a clean-environment startup failure would be speculative.

## File Audit

| File | Current role | Phase 23 decision |
| --- | --- | --- |
| `requirements-core.txt` | Existing Layer 1 runtime/DB/integration set | Sole authoritative bootstrap input |
| `requirements-observability.txt` | Logging, metrics, OpenTelemetry | Do not install during core-only attempt |
| `requirements-ai.txt` | Gemini SDK | Do not install during core-only attempt |
| `requirements-ml.txt` | Embeddings, torch, OCR, MLOps/data science | Do not install during core-only attempt |
| `requirements-dev.txt` | Includes all four layers plus test/dev tooling | Not a backend bootstrap input |
| `requirements.txt` | Monolithic production-style list including optional stacks | Legacy for this recovery; do not install |
| `constraints.txt` | gRPC pins plus `-r requirements-core.txt` | Not an install input for this recovery |
| `pyproject.toml` | Packaging metadata dynamically points dependencies at `requirements.txt` | Packaging entrypoint conflicts with minimal recovery path; do not run package install |

## Conflicts And Drift Found

- `pyproject.toml` dynamically sources `requirements.txt`, so a package install would pull the monolithic optional stack rather than the selected minimal bootstrap file.
- `requirements.txt` contains ML, Gemini, OCR, and observability packages that Phase 23 explicitly excludes from the initial boot.
- `requirements.txt` pins `numpy==1.26.4` and `Pillow==11.0.0`; `requirements-ml.txt` pins `numpy==2.2.3` and `Pillow==11.3.0`.
- `requirements-core.txt` and `constraints.txt` declare `grpcio==1.76.0`, `grpcio-tools==1.76.0`, `grpcio-status==1.76.0`, and `protobuf==6.31.1`.
- `apps/api/Dockerfile` explicitly pre-installs conflicting older values: `grpcio==1.60.0`, `grpcio-tools==1.60.0`, `grpcio-status==1.60.0`, and `protobuf==4.25.1`.
- The pre-recovery venv is already drifted from declarations: it has `grpcio==1.80.0` and `protobuf==6.33.6`.
- `constraints.txt` includes `-r requirements-core.txt`, so it acts partly as an installer manifest instead of a constraints-only boundary.

## Deferred Layers

These are intentionally outside the clean core attempt and must only be considered after a successful core startup:

1. `requirements-observability.txt`
2. Redis/Qdrant runtime validation already declared by the current core file
3. `requirements-ai.txt`
4. Embeddings, sentence-transformers, torch, OCR, and advanced ML from `requirements-ml.txt`

## Changes Proven Necessary During Recovery

The initial audit itself did not edit requirements. Subsequent clean-start failures proved that several packages previously classified as observability-only are imported by mandatory startup and route paths. Their existing pins were moved from `requirements-observability.txt` into the authoritative `requirements-core.txt`:

- `prometheus-client==0.21.1`, imported by metrics used from required routes.
- `structlog==24.4.0`, imported by startup logging.
- `opentelemetry-api==1.29.0`, imported by request/log correlation and tracing paths.
- `opentelemetry-sdk==1.29.0`, imported unconditionally by the tracing module.

`prometheus-fastapi-instrumentator` and `opentelemetry-exporter-otlp` remain deferred. The latter cannot be placed in the current core set: its OpenTelemetry 1.29 transitive protobuf requirement (`protobuf<6`) conflicts with the existing core gRPC requirement (`protobuf>=6.31.1`).
