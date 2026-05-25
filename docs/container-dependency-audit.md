# Container Dependency Audit

## API Container

Validated after clean rebuild:

```text
protobuf==6.31.1
grpcio==1.76.0
grpcio-tools==1.76.0
grpcio-status==1.76.0
```

`assert_core_dependency_runtime()` passes inside the running API container.

## Worker Container

Validated after clean rebuild:

```text
protobuf==6.31.1
grpcio==1.76.0
grpcio-tools==1.76.0
grpcio-status==1.76.0
```

`validate_worker_dependency_layer()` passes inside the running worker container.

The worker no longer contains stale packages:

- `mlflow-skinny`
- `databricks-sdk`

## Runtime Services

Validated services:

- API: healthy
- Worker: healthy through Celery ping
- Redis: `PONG`
- PostgreSQL: accepting connections
- Qdrant: `healthz check passed`
- MinIO: healthy
- MLflow: healthy

## Functional Checks

Completed:

- Alembic migrations applied to the fresh Postgres volume.
- Auth register/login route works.
- Authenticated resumes, candidates, jobs, workspace activation, and analytics routes work.
- Demo workspace loads and writes candidates, jobs, resumes, matches, ATS scores, processing events, and activity.
- Semantic search returns ranked Qdrant results.
- Real DOCX upload reaches `embedded`.
- Celery worker task round-trip returns `{'ok': True}`.
- OCR binaries are present: Tesseract and Poppler.
- Embedding dependency guard passes in the worker.

## Build Determinism

Future Docker builds are protected by:

- Requirements pins.
- Shared constraints file.
- Offline wheel install in runtime stage.
- Build-time protobuf/gRPC assertion.
- `pip check`.
- Worker-specific healthcheck in Compose.
