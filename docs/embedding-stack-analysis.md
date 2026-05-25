# Embedding Stack Analysis - Phase 24.2

Date: 2026-05-25

## Decision

Restore semantic embeddings through a minimal CPU-only layer:

| Package | Pin | Reason |
| --- | ---: | --- |
| `sentence-transformers` | `3.3.1` | Stable SBERT API used by the app; supports Python 3.11. |
| `transformers` | `4.53.0` | Compatible with `sentence-transformers>=3.3.1`; avoids known vulnerabilities listed against `4.47.1`. |
| `torch` | `2.5.1+cpu` | CPU-only PyTorch wheel; avoids CUDA/GPU package pulls. |
| `tokenizers` | `0.21.2` | Rust-backed tokenizer wheel compatible with Python 3.11 and Transformers 4.53.x. |
| `safetensors` | `0.5.3` | Lightweight model weight loader used by Hugging Face models. |

Do not install `requirements-ml.txt` for this phase. That file includes unrelated ML/OCR/training packages and an invalid `torch==2.12.0` pin for this stable-runtime restoration path.

## Constraints

The stable backend runtime remains authoritative:

| Package | Stable pin |
| --- | ---: |
| `protobuf` | `6.31.1` |
| `grpcio` | `1.76.0` |
| `grpcio-tools` | `1.76.0` |
| `grpcio-status` | `1.76.0` |

The embedding stack must not change these packages.

## Package Findings

### `sentence-transformers==3.3.1`

PyPI metadata:

- Python: `>=3.9`
- Dependencies: `transformers<5.0.0,>=4.41.0`, `torch>=1.11.0`, `huggingface-hub>=0.20.0`, `scikit-learn`, `scipy`, `tqdm`, `Pillow`
- Extras such as `onnx`, `onnx-gpu`, `openvino`, `train`, and `dev` are not used.

The project documentation recommends Python 3.9+, PyTorch 1.11+, and Transformers 4.34+.

### `transformers==4.53.0`

PyPI metadata lists Python 3.11 support. Its documentation says Transformers works with Python 3.9+ and PyTorch 2.1+.

`4.47.1` should not be restored because PyPI currently lists multiple vulnerability records fixed in `4.52.1` or `4.53.0`.

### `torch==2.5.1+cpu`

PyPI metadata for `torch==2.5.1` lists Python 3.11 support. For CPU-only installation, use PyTorch's CPU wheel index rather than a CUDA wheel source:

```powershell
pip install -r requirements-embeddings.txt -c constraints.txt
```

`requirements-embeddings.txt` includes the CPU wheel index and pins `torch==2.5.1+cpu`.

### `tokenizers==0.21.2`

Tokenizers provides Rust-backed Python wheels and supports Python 3.11. It is included as a direct pin to avoid source builds.

### `huggingface-hub`

`huggingface-hub` is intentionally left transitive through `sentence-transformers`/`transformers` so the resolver can choose a compatible version. It does not touch protobuf/gRPC.

### `safetensors==0.5.3`

Pinned directly because most Hugging Face models use `.safetensors` weights. It is small and avoids pickle-style model loading.

## Runtime Strategy

- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Vector size: `384`
- Device: CPU
- Cache: `runtime/model-cache/huggingface`
- Startup behavior: no model load during FastAPI startup
- First-use behavior: model loads lazily on first embedding request
- Timeout: `EMBEDDING_INFERENCE_TIMEOUT_SECONDS`, default `30`
- Offline/cache-only option: `EMBEDDING_LOCAL_FILES_ONLY=true`

## Validation

Install only the embedding layer:

```powershell
cd apps\api
..\..\.venv\Scripts\python.exe -m pip install -r requirements-embeddings.txt -c constraints.txt
```

Validate without backend startup:

```powershell
.\.venv\Scripts\python.exe scripts\test_embeddings_runtime.py
```

Validate vector insertion/search:

```powershell
.\.venv\Scripts\python.exe scripts\test_embeddings_runtime.py --local-files-only --with-qdrant
```

Backend validation after isolated success:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'apps/api'); from app.core.dependency_guard import assert_core_dependency_runtime; print(assert_core_dependency_runtime())"
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'apps/api'); from app.core.dependency_guard import validate_embedding_dependency_layer; print(validate_embedding_dependency_layer())"
```

## Local Validation Result

The local Windows Python 3.11 runtime validated successfully with:

```text
protobuf==6.31.1
grpcio==1.76.0
grpcio-tools==1.76.0
grpcio-status==1.76.0
torch==2.5.1+cpu
sentence-transformers==3.3.1
transformers==4.53.0
tokenizers==0.21.2
safetensors==0.5.3
```

`scripts/test_embeddings_runtime.py --local-files-only --with-qdrant` produced a `384` dimensional embedding and inserted/searched one Qdrant point with top score `1.0`.

## References

- PyPI `sentence-transformers==3.3.1`: package metadata and dependency constraints.
- PyPI `transformers==4.53.0`: Python support and PyTorch compatibility notes.
- PyPI `transformers==4.47.1`: vulnerability records fixed in later releases.
- PyPI `torch==2.5.1`: Python 3.11 wheel support.
- PyTorch Get Started: CPU wheel installation guidance.
