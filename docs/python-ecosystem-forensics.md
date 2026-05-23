# Python Ecosystem Forensics - PHASE 21

**Date**: 2026-05-23
**Phase**: STEP 1 - COMPLETE DEPENDENCY FORENSICS

## Overview

This document provides a deep forensic analysis of the Python ecosystem, focusing on binary dependency conflicts, grpc ecosystem issues, OpenTelemetry compatibility, Qdrant dependencies, and Windows-specific challenges.

## Critical Issue: GRPC Binary Failure

**Error**:
```
ImportError: cannot import name 'cygrpc' from 'grpc._cython' (C:\Users\Lenovo\Desktop\mlops-ai\.venv\Lib\site-packages\grpc\_cython\__init__.py)
```

**Root Cause**:
- qdrant-client==1.12.1 depends on grpcio
- grpcio installation is corrupted or incompatible
- cygrpc (Cython-based gRPC extension) failed to compile or install
- Windows-specific binary wheel compatibility issue

**Impact**:
- Backend cannot start
- qdrant-client cannot be imported
- Vector search functionality unavailable
- All downstream services that depend on qdrant-client fail

---

## Dependency Analysis

### Current Requirements Structure

**requirements-core.txt** (59 lines):
- Web API: fastapi, uvicorn, python-multipart, websockets
- Settings: pydantic, pydantic-settings, email-validator
- DB: SQLAlchemy, asyncpg, psycopg, alembic
- Redis/Queue: redis, celery, slowapi
- Auth: python-jose, passlib, bcrypt, cryptography
- Storage/Billing: boto3, botocore, httpx, tenacity, stripe, neo4j
- Vector: qdrant-client (PROBLEMATIC)
- Observability: structlog, prometheus-client, prometheus-fastapi-instrumentator, opentelemetry-* (5 packages)
- LLM: google-generativeai

**requirements.txt** (79 lines):
- All of requirements-core.txt PLUS:
- ML: sentence-transformers, transformers, torch, networkx
- MLOps: mlflow, prefect
- OCR: pdfplumber, pymupdf, python-docx, pytesseract, Pillow
- Data: pandas, numpy, scikit-learn
- LTR: xgboost, joblib

---

## GRPC Ecosystem Analysis

### Direct Dependencies

**qdrant-client==1.12.1**:
- Depends on grpcio>=1.34.0
- Depends on grpcio-tools>=1.34.0
- Depends on protobuf>=3.19.0
- Depends on httpx>=0.24.0

**OpenTelemetry Exporters**:
- opentelemetry-exporter-otlp==1.29.0
  - Depends on grpcio>=1.34.0
  - Depends on protobuf>=3.19.0

**Transitive Dependencies**:
- googleapis-common-protos (from google-generativeai)
- grpcio-status (from qdrant-client)

---

## Binary Wheel Compatibility Issues

### Windows-Specific Challenges

**grpcio**:
- Requires compiled C++ extensions
- Binary wheels may not be available for Python 3.11 on Windows
- Requires Visual C++ Build Tools if wheel unavailable
- cygrpc module must be compiled from source if wheel missing

**protobuf**:
- Generally has good wheel support
- Version compatibility with grpcio critical

---

## OpenTelemetry Ecosystem Analysis

### Installed Packages

- opentelemetry-api==1.29.0
- opentelemetry-sdk==1.29.0
- opentelemetry-exporter-otlp==1.29.0
- opentelemetry-instrumentation-fastapi==0.50b0
- opentelemetry-instrumentation-sqlalchemy==0.50b0
- opentelemetry-instrumentation-redis==0.50b0
- opentelemetry-instrumentation-httpx==0.50b0
- opentelemetry-instrumentation-celery==0.50b0

### Compatibility Matrix

| Package | Version | grpcio Requirement | Status |
|---------|---------|-------------------|--------|
| opentelemetry-exporter-otlp | 1.29.0 | >=1.34.0 | BROKEN (grpcio broken) |
| qdrant-client | 1.12.1 | >=1.34.0 | BROKEN (grpcio broken) |

---

## Qdrant Client Dependencies

### Dependency Tree

```
qdrant-client==1.12.1
├── grpcio>=1.34.0 (BROKEN)
├── grpcio-tools>=1.34.0
├── protobuf>=3.19.0
├── httpx>=0.24.0
└── grpcio-status>=1.50.0
```

### Issue Analysis

**grpcio**:
- Version requirement: >=1.34.0
- Current state: BROKEN (cygrpc import failure)
- Likely cause: Corrupted installation or incompatible wheel

**grpcio-tools**:
- Version requirement: >=1.34.0
- Current state: Installed (grpcio-tools==1.71.2)
- May be incompatible with broken grpcio

---

## ML Ecosystem Analysis

### ML Dependencies (Not Installed)

- sentence-transformers==3.3.1 (MISSING)
- transformers==4.47.1 (MISSING)
- torch==2.12.0 (MISSING)
- networkx==3.4.2 (MISSING)
- mlflow==2.19.0 (MISSING)
- prefect==3.1.12 (MISSING)
- pdfplumber==0.11.5 (MISSING)
- pymupdf==1.25.1 (MISSING)
- python-docx==1.1.2 (MISSING)
- pytesseract==0.3.13 (MISSING)
- Pillow==11.0.0 (MISSING)
- pandas==2.2.3 (MISSING)
- numpy==1.26.4 (MISSING)
- scikit-learn==1.6.0 (MISSING)
- xgboost==2.1.3 (MISSING)
- joblib==1.4.2 (MISSING)

**Impact**: ML features unavailable, but core API should work without them

---

## Dependency Resolver Conflicts

### Potential Conflicts

1. **grpcio ecosystem**:
   - qdrant-client requires grpcio>=1.34.0
   - opentelemetry-exporter-otlp requires grpcio>=1.34.0
   - grpcio-tools may require specific grpcio version
   - Version mismatch possible

2. **protobuf ecosystem**:
   - qdrant-client requires protobuf>=3.19.0
   - google-generativeai may require specific protobuf version
   - opentelemetry exporters require protobuf>=3.19.0
   - Version conflict possible

3. **OpenTelemetry ecosystem**:
   - All OpenTelemetry packages must be same major version
   - Instrumentation packages must match API/SDK versions
   - Current: All at 1.29.0 / 0.50b0 (GOOD)

---

## Stale Cached Wheels

### Pip Cache Issues

**Symptoms**:
- WARNING: Cache entry deserialization failed, entry ignored
- Multiple cache warnings during install

**Impact**:
- Corrupted cache may cause installation failures
- Stale wheels may be incompatible with current Python version
- Cache corruption can propagate broken installations

**Solution Required**:
- Purge pip cache: `pip cache purge`
- Force reinstall: `pip install --force-reinstall --no-cache-dir`

---

## Duplicated Dependency Trees

### Potential Duplicates

1. **grpcio**:
   - May be installed as dependency of qdrant-client
   - May be installed as dependency of opentelemetry-exporter-otlp
   - May be installed as dependency of google-generativeai
   - Multiple install paths possible

2. **protobuf**:
   - May be installed as dependency of qdrant-client
   - May be installed as dependency of google-generativeai
   - May be installed as dependency of opentelemetry packages
   - Version conflicts possible

---

## ABI Mismatches

### Python 3.11 ABI

**Current State**:
- Python 3.11.9 (user switched from 3.14.5)
- venv created with Python 3.11
- All packages should target Python 3.11 ABI

**Potential Issues**:
- grpcio wheels may not be available for Python 3.11 on Windows
- Some packages may require compilation
- Binary wheels may be incompatible with Windows architecture

---

## Broken Compiled Extensions

### cygrpc

**Issue**:
- cygrpc is a Cython-compiled extension for grpcio
- Failed to compile or install
- Missing from grpc._cython module

**Root Cause**:
- Visual C++ Build Tools not installed
- Compilation failed during grpcio install
- Binary wheel unavailable for Python 3.11 on Windows
- Installation silently failed or partially succeeded

---

## Recommendations

### Immediate Actions

1. **Fix grpcio installation**:
   - Uninstall grpcio, grpcio-tools, grpcio-status
   - Install Visual C++ Build Tools
   - Reinstall grpcio with pre-built wheel or compile from source
   - Validate: `python -c "import grpc; from grpc._cython import cygrpc"`

2. **Purge pip cache**:
   - `pip cache purge`
   - `pip install --force-reinstall --no-cache-dir`

3. **Recreate venv**:
   - Remove corrupted .venv
   - Recreate with Python 3.11
   - Install dependencies in layers

### Short-term Actions

1. **Layered dependency strategy**:
   - Separate core dependencies from ML dependencies
   - Install grpc ecosystem first
   - Validate each layer before proceeding

2. **Pin grpc ecosystem versions**:
   - Use known-compatible grpcio version
   - Pin protobuf to compatible version
   - Pin grpcio-tools to matching version

### Long-term Actions

1. **Use Docker for development**:
   - Avoid Windows-specific binary issues
   - Use Linux-based development environment
   - Ensure parity with production

2. **Implement graceful degradation**:
   - Allow backend to start without qdrant-client
   - Provide fallback for vector search
   - Make ML features truly optional

---

## Next Steps

1. ✅ STEP 1: Complete dependency forensics (COMPLETE)
2. ⏭️ STEP 2: GRPC ecosystem stabilization
3. ⏭️ STEP 3: Full venv reconstruction
4. ⏭️ STEP 4: Layered dependency strategy
5. ⏭️ STEP 5: Windows compatibility hardening
6. ⏭️ STEP 6: Optional ML degradation
7. ⏭️ STEP 7: Startup isolation hardening
8. ⏭️ STEP 8: Backend validation matrix
9. ⏭️ STEP 9: Docker + local parity
10. ⏭️ STEP 10: Final target validation

---

## Conclusion

The primary issue is a broken grpcio installation due to Windows-specific binary wheel compatibility. The cygrpc extension failed to compile or install, causing a cascading failure that prevents the backend from starting. The solution requires fixing the grpc ecosystem, purging corrupted caches, and implementing a layered dependency strategy to ensure deterministic installations.
