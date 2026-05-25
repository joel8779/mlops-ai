# Repository Runtime Map - PHASE 22 Forensics

## Overview
Complete inventory of all dependency files, configurations, and runtime scripts in the repository.

---

## Dependency Files

### Requirements Files (apps/api/)

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `requirements.txt` | Monolithic - ALL dependencies | 79 | **CONFLICTS** with layered approach |
| `requirements-core.txt` | Layer 1: Core + DB + GRPC | 50 | **AUTHORITATIVE** for core |
| `requirements-observability.txt` | Layer 3: Telemetry stack | 25 | Missing from venv |
| `requirements-ai.txt` | Layer 4: AI SDKs | 9 | Missing from venv |
| `requirements-ml.txt` | Layer 2: ML/AI stack | 30 | Missing from venv |
| `requirements-dev.txt` | Dev dependencies (references layers) | 32 | **NOT INSTALLED** |
| `constraints.txt` | CI/Docker constraints | 13 | **CONFLICTS** with Dockerfile |

### Python Configuration

| File | Location | Python Version | Status |
|------|----------|----------------|--------|
| `pyproject.toml` | apps/api/ | `>=3.11,<3.13` | **CORRECT** |
| Dockerfile | apps/api/ | 3.11-slim | **CORRECT** |

---

## Docker Configuration

### Dockerfiles

| File | Base Image | GRPC Version | Status |
|------|------------|---------------|--------|
| `apps/api/Dockerfile` | python:3.11-slim | grpcio==1.60.0 | **CONFLICTS** with requirements |
| `apps/web/Dockerfile` | (not analyzed) | - | - |

### Docker Compose Files

| File | Services | Status |
|------|----------|--------|
| `docker-compose.yml` | postgres, redis, qdrant, minio, mlflow, api, worker | Production config |
| `docker-compose.dev.yml` | + neo4j, prometheus, loki, grafana | Development config |
| `docker-compose.prod.yml` | (not analyzed) | - |

---

## Bootstrap Scripts

| Script | Purpose | Python Version Detection | Status |
|--------|---------|-------------------------|--------|
| `scripts/bootstrap.sh` | Initial setup | 3.11 or 3.12 | **CORRECT** |
| `scripts/full_runtime_recovery.sh` | Runtime recovery | 3.11 or 3.12 | **CORRECT** |
| `scripts/bootstrap_database.sh` | DB initialization | - | - |
| `scripts/dev-start.sh` | Dev startup | - | - |
| `scripts/dev-up.sh` | Dev environment | - | - |
| `scripts/rebuild_local_env.sh` | Local rebuild | - | - |

---

## Validation Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| `scripts/backend_validation.py` | Backend validation | - |
| `scripts/bootstrap_local_env.py` | Local env bootstrap | - |
| `scripts/grpc_recovery.py` | GRPC recovery | - |
| `scripts/release_candidate_validation.py` | Release validation | - |
| `scripts/runtime_validation_matrix.py` | Runtime matrix | - |
| `scripts/security_release_validation.py` | Security validation | - |
| `scripts/seed_demo_data.py` | Demo data seeding | - |
| `scripts/setup_demo_environment.py` | Demo setup | - |
| `scripts/validate_build_toolchain.py` | Build toolchain validation | - |
| `scripts/validate_env.py` | Environment validation | - |
| `scripts/validate_grpc.py` | GRPC validation | - |
| `scripts/validate_local_infra.py` | Infrastructure validation | - |
| `scripts/validate_ml_stack.py` | ML stack validation | - |
| `scripts/verify_env.py` | Environment verification | - |
| `scripts/verify_python_runtime.py` | Python runtime verification | - |
| `scripts/verify_services.py` | Service verification | - |

---

## Environment Files

| File | Purpose | Status |
|------|---------|--------|
| `.env` | Local environment variables | **ACTIVE** |
| `.env.example` | Environment template | - |

---

## Critical Conflicts Identified

### 1. GRPC Version Conflict
- **Dockerfile**: grpcio==1.60.0
- **requirements-core.txt**: grpcio==1.76.0
- **constraints.txt**: grpcio==1.76.0
- **Impact**: Docker builds will fail or use wrong version

### 2. Requirements File Strategy Conflict
- **requirements.txt**: Monolithic file with ALL dependencies
- **Layered files**: Split into core, observability, ai, ml
- **requirements-dev.txt**: References layered files
- **Impact**: Unclear which file is authoritative

### 3. Circular Reference in constraints.txt
- **constraints.txt** contains: `-r requirements-core.txt`
- **Impact**: If used with requirements-dev.txt, creates circular reference

### 4. Missing Layer Installation
- **Venv state**: Only core dependencies installed
- **Missing**: observability, ai, ml layers
- **Impact**: App imports fail due to missing dependencies

---

## Python Environment State

### System Python
- **Default**: Python 3.14.5 (INCOMPATIBLE)
- **Available**: 3.14.5, 3.13, 3.11.9
- **Required**: 3.11-3.12

### Venv Python
- **Version**: Python 3.11.9 (CORRECT)
- **Location**: `.venv/Scripts/python.exe`
- **Pip**: 26.1.1
- **Site-packages**: Isolated (no user-site leakage)

### PATH Issue
- **Problem**: Running `python` uses system 3.14.5 instead of venv 3.11.9
- **Impact**: All manual python commands fail unless full venv path is used

---

## Installed Dependencies (Venv)

### Present (Core Layer)
- fastapi, uvicorn, pydantic, sqlalchemy, asyncpg
- redis, celery, boto3, httpx, stripe, neo4j
- qdrant-client, numpy
- grpcio-tools, grpcio-status (but NOT grpcio itself - BROKEN)

### Missing (Observability Layer)
- structlog
- prometheus-client
- prometheus-fastapi-instrumentator
- opentelemetry-api
- opentelemetry-sdk
- opentelemetry-exporter-otlp
- All opentelemetry-instrumentation-* packages

### Missing (AI Layer)
- google-generativeai

### Missing (ML Layer)
- torch
- transformers
- sentence-transformers
- pandas
- scikit-learn
- xgboost
- joblib
- pdfplumber
- pymupdf
- python-docx
- pytesseract
- Pillow
- mlflow
- prefect

---

## Configuration Issues

### .env File Issues
- **backend_cors_origins**: Parsing error (likely malformed JSON/list)
- **GEMINI_API_KEY**: Hardcoded key present (security risk)

---

## Next Steps

1. Fix Python PATH issue to use venv by default
2. Install missing dependency layers in correct order
3. Resolve GRPC version conflict between Dockerfile and requirements
4. Fix backend_cors_origins configuration
5. Remove hardcoded API key from .env
6. Establish single authoritative requirements strategy
