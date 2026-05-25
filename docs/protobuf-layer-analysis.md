# Protobuf Layer Analysis

## Required Runtime Contract

The stabilized backend requires:

```text
protobuf>=6.31.1,<7.0.0
grpcio>=1.76.0,<2.0.0
grpcio-tools>=1.76.0,<2.0.0
grpcio-status>=1.76.0,<2.0.0
```

The deterministic lock used by Docker is:

```text
protobuf==6.31.1
grpcio==1.76.0
grpcio-tools==1.76.0
grpcio-status==1.76.0
```

## Requirement Audit

Current files are aligned:

- `requirements-core.txt` pins protobuf and all gRPC packages to the required versions.
- `constraints.txt` repeats those pins.
- `requirements-observability.txt` uses OpenTelemetry `1.42.1`, which is compatible with protobuf 6.x.
- `requirements-ai.txt` uses `google-genai==2.6.0` and avoids legacy Gemini packages.
- `requirements-worker.txt` contains Celery, Redis, and Prefect only.
- `requirements-embeddings.txt` is CPU-only and does not downgrade protobuf.
- `requirements-ocr.txt` has no protobuf dependency.

## Downgrade Source

The protobuf 5.29.6 runtime came from an old worker image, not current source files.

The stale worker image still contained:

- `mlflow-skinny==2.19.0`
- `databricks-sdk==0.110.0`
- `opentelemetry-proto==1.29.0`

`opentelemetry-proto==1.29.0` is from the old protobuf 5.x compatibility line. The current observability layer uses `opentelemetry-proto==1.42.1`.

## Guardrail

The Dockerfile now fails the build if any layer leaves the runtime with the wrong protobuf/gRPC versions. This catches future transitive downgrades before an image can be exported.
