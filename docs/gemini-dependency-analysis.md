# Gemini Dependency Analysis - Phase 24.1

Date: 2026-05-25

## Decision

Use `google-genai==2.6.0` for Gemini and stop using `google-generativeai`.

The existing backend runtime depends on:

| Package | Stable pin | Required by |
| --- | ---: | --- |
| `protobuf` | `6.31.1` | `grpcio-tools`, `grpcio-status` |
| `grpcio` | `1.76.0` | `grpcio-tools`, `grpcio-status`, `qdrant-client` |
| `grpcio-tools` | `1.76.0` | core gRPC/protobuf compatibility |
| `grpcio-status` | `1.76.0` | core gRPC/protobuf compatibility |

This layer must remain unchanged.

## Forensics

### `google-generativeai`

`google-generativeai` is now the legacy Gemini SDK. PyPI marks `0.8.6` inactive/deprecated and says support ended on November 30, 2025. It recommends migration to the Google Gen AI SDK.

Observed dependency problem:

| Package | Constraint |
| --- | --- |
| `google-generativeai==0.8.3` | pulls `google-ai-generativelanguage==0.6.10` |
| `google-ai-generativelanguage==0.6.10` | `protobuf<6.0.0dev,>=3.20.2` |
| `google-ai-generativelanguage==0.6.10` | `google-api-core[grpc]...` |
| `google-api-core[grpc]` | brings `grpcio-status` through the gRPC extra |

Result: installing `google-generativeai==0.8.3` is incompatible with the backend's stable `protobuf==6.31.1` and can downgrade the gRPC ecosystem.

### `google-ai-generativelanguage`

Older `0.6.x` releases require `protobuf<6`. Newer `0.10.0` supports `protobuf<7.0.0,>=3.20.2`, but it is still a GAPIC/gRPC-oriented package and pulls `google-api-core[grpc]`.

Conclusion: do not use this package directly for Gemini in the FastAPI runtime.

### `google-api-core`

Current `google-api-core==2.28.1` allows `protobuf<7.0.0,>=3.19.5`, so the base package is compatible with protobuf 6.x. The issue is the `[grpc]` extra, which adds `grpcio` and `grpcio-status` resolver pressure.

### `grpcio-status` and `grpcio-tools`

Installed metadata in the stable local runtime:

```text
grpcio-tools: protobuf>=6.31.1,<7.0.0; grpcio>=1.76.0
grpcio-status: protobuf>=6.31.1,<7.0.0; grpcio>=1.76.0
```

Any Gemini strategy that selects protobuf 5.x or a lower `grpcio-status` breaks this runtime.

## Modern SDK Evaluation

`google-genai==2.6.0` is the recommended modern SDK.

Relevant dependency metadata:

| Package | Python | protobuf | gRPC |
| --- | --- | --- | --- |
| `google-genai==2.6.0` | `>=3.10` | none by default | none by default |
| `google-genai[aiohttp]==2.6.0` | `>=3.10` | none by default | none by default |
| `google-genai[local-tokenizer]==2.6.0` | `>=3.10` | adds `protobuf` | avoid in backend runtime |

The SDK documentation states that it uses `httpx` by default for sync and async clients, with optional `aiohttp` for faster async use. This matches the Phase 24.1 preference for HTTP/REST transport instead of gRPC-heavy Gemini clients.

## Implementation Rules

1. `requirements-core.txt` remains the authority for protobuf/gRPC pins.
2. `requirements-ai.txt` installs only `google-genai==2.6.0`.
3. AI installs must use `-c constraints.txt`.
4. Do not install `google-generativeai`.
5. Do not install `google-ai-generativelanguage` for Gemini runtime code.
6. Do not use `google-genai[local-tokenizer]` in the backend runtime.

## Local Changes

- `apps/api/requirements-ai.txt` now uses `google-genai==2.6.0`.
- `apps/api/constraints.txt` pins `google-genai==2.6.0` and blocks known legacy `google-generativeai` releases.
- `app.services.llm.providers.gemini_provider` now uses the modern `google.genai` SDK and imports it lazily.
- `app.core.dependency_guard` asserts protobuf/gRPC compatibility during startup.
- `scripts/test_gemini_runtime.py` validates Gemini in isolation without backend startup, embeddings, torch, or OCR.

## Validation Commands

Core-only validation:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -c "from app.core.dependency_guard import assert_core_dependency_runtime; print(assert_core_dependency_runtime())"
```

AI dependency install:

```powershell
cd apps\api
..\..\.venv\Scripts\python.exe -m pip install -r requirements-ai.txt -c constraints.txt
```

Gemini isolated validation:

```powershell
.\.venv\Scripts\python.exe scripts\test_gemini_runtime.py
```

Dependency-only Gemini validation:

```powershell
.\.venv\Scripts\python.exe scripts\test_gemini_runtime.py --dependency-only
```

## References

- PyPI `google-generativeai==0.8.6`: legacy/deprecated SDK notice and `google-ai-generativelanguage==0.6.15` dependency.
- PyPI `google-ai-generativelanguage==0.6.10`: `protobuf<6.0.0dev,>=3.20.2` and `google-api-core[grpc]` dependency.
- PyPI `google-ai-generativelanguage==0.10.0`: protobuf 6-compatible metadata, but still GAPIC/gRPC-oriented.
- PyPI `google-genai==2.6.0`: modern SDK metadata with no default protobuf/gRPC dependency.
- Google Gen AI SDK docs: default HTTP clients use `httpx`; `aiohttp` is optional.
