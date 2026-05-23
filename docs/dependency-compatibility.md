# Dependency Compatibility Matrix

**Generated**: 2025-01-23
**Phase**: PHASE 13 — FINAL RELEASE ENGINEERING
**Status**: COMPLETED

---

# Python Version Compatibility

**Supported Versions**: Python 3.11, 3.12
**Unsupported**: Python 3.14 (local development only)

---

# Core Dependencies

## Web API and ASGI Server

| Package | Version | Python 3.11 | Python 3.12 | Notes |
|---------|---------|-------------|-------------|-------|
| fastapi | 0.115.6 | ✅ | ✅ | Compatible |
| uvicorn[standard] | 0.34.0 | ✅ | ✅ | Compatible |
| python-multipart | 0.0.20 | ✅ | ✅ | Compatible |
| websockets | 13.1 | ✅ | ✅ | Downgraded for prefect compatibility |

## Settings and Validation

| Package | Version | Python 3.11 | Python 3.12 | Notes |
|---------|---------|-------------|-------------|-------|
| pydantic | 2.10.4 | ✅ | ✅ | Compatible |
| pydantic-settings | 2.7.1 | ✅ | ✅ | Compatible |
| email-validator | 2.2.0 | ✅ | ✅ | Compatible |

## PostgreSQL and ORM

| Package | Version | Python 3.11 | Python 3.12 | Notes |
|---------|---------|-------------|-------------|-------|
| SQLAlchemy[asyncio] | 2.0.36 | ✅ | ✅ | Compatible |
| asyncpg | 0.30.0 | ✅ | ✅ | Compatible |
| psycopg[binary] | 3.2.3 | ✅ | ✅ | Compatible |
| alembic | 1.14.0 | ✅ | ✅ | Compatible |

## Redis and Task Queue

| Package | Version | Python 3.11 | Python 3.12 | Notes |
|---------|---------|-------------|-------------|-------|
| redis | 5.2.1 | ✅ | ✅ | Compatible |
| celery[redis] | 5.4.0 | ✅ | ✅ | Compatible |
| slowapi | 0.1.9 | ✅ | ✅ | Compatible |

## Authentication and Security

| Package | Version | Python 3.11 | Python 3.12 | Notes |
|---------|---------|-------------|-------------|-------|
| python-jose[cryptography] | 3.3.0 | ✅ | ✅ | Compatible |
| passlib[bcrypt] | 1.7.4 | ✅ | ✅ | Compatible |
| bcrypt | 4.2.1 | ✅ | ✅ | Compatible |
| cryptography | 44.0.0 | ✅ | ✅ | May require system dependencies |

## Object Storage and Integrations

| Package | Version | Python 3.11 | Python 3.12 | Notes |
|---------|---------|-------------|-------------|-------|
| boto3 | 1.35.90 | ✅ | ✅ | Compatible |
| botocore | 1.35.90 | ✅ | ✅ | Compatible |
| httpx | 0.28.1 | ✅ | ✅ | Compatible |
| tenacity | 9.0.0 | ✅ | ✅ | Compatible |
| stripe | 11.4.1 | ✅ | ✅ | Compatible |
| neo4j | 5.27.0 | ✅ | ✅ | Compatible |

## Vector Search and ML

| Package | Version | Python 3.11 | Python 3.12 | Notes |
|---------|---------|-------------|-------------|-------|
| qdrant-client | 1.12.1 | ✅ | ✅ | Compatible |
| sentence-transformers | 3.3.1 | ✅ | ✅ | Compatible |
| transformers | 4.47.1 | ✅ | ✅ | Compatible |
| torch | 2.5.1 | ✅ | ✅ | May require system dependencies |
| networkx | 3.4.2 | ✅ | ✅ | Compatible |

## MLOps and Orchestration

| Package | Version | Python 3.11 | Python 3.12 | Notes |
|---------|---------|-------------|-------------|-------|
| mlflow | 2.19.0 | ✅ | ✅ | Compatible |
| prefect | 3.1.12 | ✅ | ✅ | Requires websockets<14.0 |

## OCR and Document Parsing

| Package | Version | Python 3.11 | Python 3.12 | Notes |
|---------|---------|-------------|-------------|-------|
| pdfplumber | 0.11.5 | ✅ | ✅ | Compatible |
| pymupdf | 1.25.1 | ✅ | ✅ | Requires Poppler |
| python-docx | 1.1.2 | ✅ | ✅ | Compatible |
| pytesseract | 0.3.13 | ✅ | ✅ | Requires Tesseract |
| Pillow | 11.0.0 | ✅ | ✅ | Compatible |

## Observability

| Package | Version | Python 3.11 | Python 3.12 | Notes |
|---------|---------|-------------|-------------|-------|
| structlog | 24.4.0 | ✅ | ✅ | Compatible |
| prometheus-client | 0.21.1 | ✅ | ✅ | Compatible |
| prometheus-fastapi-instrumentator | 7.0.0 | ✅ | ✅ | Compatible |
| opentelemetry-api | 1.29.0 | ✅ | ✅ | Compatible |
| opentelemetry-sdk | 1.29.0 | ✅ | ✅ | Compatible |
| opentelemetry-exporter-otlp | 1.29.0 | ✅ | ✅ | Compatible |
| opentelemetry-instrumentation-fastapi | 0.50b0 | ✅ | ✅ | Compatible |
| opentelemetry-instrumentation-sqlalchemy | 0.50b0 | ✅ | ✅ | Compatible |
| opentelemetry-instrumentation-redis | 0.50b0 | ✅ | ✅ | Compatible |
| opentelemetry-instrumentation-httpx | 0.50b0 | ✅ | ✅ | Compatible |
| opentelemetry-instrumentation-celery | 0.50b0 | ✅ | ✅ | Compatible |

## Data Science

| Package | Version | Python 3.11 | Python 3.12 | Notes |
|---------|---------|-------------|-------------|-------|
| pandas | 2.2.3 | ✅ | ✅ | Compatible |
| numpy | 1.26.4 | ✅ | ✅ | Compatible |
| scikit-learn | 1.6.0 | ✅ | ✅ | Compatible |

## LLM Integration

| Package | Version | Python 3.11 | Python 3.12 | Notes |
|---------|---------|-------------|-------------|-------|
| google-generativeai | 0.8.3 | ✅ | ✅ | Compatible |

## Learning-to-Rank

| Package | Version | Python 3.11 | Python 3.12 | Notes |
|---------|---------|-------------|-------------|-------|
| xgboost | 2.1.3 | ✅ | ✅ | Compatible |
| joblib | 1.4.2 | ✅ | ✅ | Compatible |

---

# Known Constraints

## Prefect Constraints

- **websockets**: Must be <14.0 (currently 13.1)
- **Python**: 3.11, 3.12 supported

## Torch Constraints

- **Python**: 3.11, 3.12 supported (not 3.14)
- **System**: May require system libraries for CUDA support

## OCR Dependencies

- **pytesseract**: Requires Tesseract OCR engine
- **pymupdf**: Requires Poppler library
- **System**: These must be installed in Docker image

---

# System Dependencies

## Required System Libraries

### OCR
- Tesseract OCR engine
- Poppler library

### ML (Optional)
- CUDA toolkit (for GPU support)
- cuDNN (for GPU support)

---

# Dependency Conflicts Resolved

## websockets

**Issue**: websockets==14.1 conflicts with prefect==3.1.12 (requires websockets<14.0)

**Resolution**: Downgraded to websockets==13.1

**Impact**: Maintains prefect compatibility while preserving FastAPI and uvicorn functionality

---

# Recommendations

## For CI/CD

1. **Use Python 3.11 or 3.12** - Avoid Python 3.14 in CI
2. **Install system dependencies** - Ensure Tesseract and Poppler are installed in Docker image
3. **Use pinned versions** - All dependencies are pinned for reproducibility
4. **Validate dependency resolution** - Run pip check to detect conflicts

## For Local Development

1. **Use Python 3.11 or 3.12** - Python 3.14 may have compatibility issues
2. **Install system dependencies** - Install Tesseract and Poppler locally
3. **Use virtual environments** - Isolate dependencies per project

## For Production

1. **Use Python 3.11 or 3.12** - Stable and supported versions
2. **Monitor security advisories** - Keep dependencies up to date
3. **Test dependency updates** - Validate updates in staging before production

---

# Validation Checklist

- [x] All dependencies pinned with ==
- [x] websockets compatible with prefect
- [x] torch compatible with Python 3.11/3.12
- [x] OpenTelemetry versions aligned
- [x] FastAPI compatible with Pydantic
- [x] SQLAlchemy compatible with asyncpg
- [x] All dependencies have Python 3.11/3.12 support
