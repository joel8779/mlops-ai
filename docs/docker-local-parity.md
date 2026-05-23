# Docker + Local Parity - PHASE 21

**Date**: 2026-05-23
**Phase**: STEP 9 - DOCKER + LOCAL PARITY

## Overview

This document audits Docker and local environment parity to ensure consistent behavior across development and production environments.

## Dockerfile Audit

### Python Version

**Docker**: `python:3.11-slim`
**Local**: Python 3.11.9
**Status**: ✅ MATCH

### Dependency Strategy

**Before PHASE 21**:
- Docker: Used `requirements.txt` (monolithic)
- Local: Used `requirements.txt` (monolithic)
- Status: ✅ MATCH (but problematic)

**After PHASE 21**:
- Docker: Uses layered requirements (core, observability, ai, ml)
- Local: Uses layered requirements (core, observability, ai, ml)
- Status: ✅ MATCH (improved)

### GRPC Ecosystem

**Docker**:
- Installs grpcio==1.60.0 first
- Installs grpcio-tools==1.60.0
- Installs grpcio-status==1.60.0
- Installs protobuf==4.25.1
- Status: ✅ PINNED

**Local**:
- requirements-core.txt includes grpcio==1.60.0
- requirements-core.txt includes grpcio-tools==1.60.0
- requirements-core.txt includes grpcio-status==1.60.0
- requirements-core.txt includes protobuf==4.25.1
- Status: ✅ PINNED

### Build Tools

**Docker**:
- build-essential (for compilation)
- libpq-dev (for PostgreSQL)
- Status: ✅ INCLUDED

**Local**:
- Requires Visual C++ Build Tools on Windows
- Status: ⚠️ PLATFORM-SPECIFIC

### Runtime Dependencies

**Docker**:
- curl (for health checks)
- libpq5 (for PostgreSQL client)
- tesseract-ocr (for OCR)
- poppler-utils (for PDF parsing)
- Status: ✅ INCLUDED

**Local**:
- tesseract-ocr (optional, in requirements-ml.txt)
- poppler-utils (optional, in requirements-ml.txt)
- Status: ⚠️ OPTIONAL

---

## Docker Compose Audit

### Infrastructure Services

**PostgreSQL**:
- Image: postgres:16-alpine
- Port: 5432
- Status: ✅ CONSISTENT

**Redis**:
- Image: redis:7-alpine
- Port: 6379
- Status: ✅ CONSISTENT

**Qdrant**:
- Image: qdrant/qdrant:v1.12.6
- Ports: 6333 (HTTP), 6334 (GRPC)
- Status: ✅ CONSISTENT

**MinIO**:
- Image: minio/minio:RELEASE.2024-12-18T13-15-44Z
- Ports: 9000 (API), 9001 (Console)
- Status: ✅ CONSISTENT

**MLflow**:
- Image: ghcr.io/mlflow/mlflow:v2.19.0
- Port: 5000
- Status: ✅ CONSISTENT

### Application Services

**API**:
- Build: ./apps/api
- Command: uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
- Ports: 8000
- Status: ✅ CONSISTENT

**Worker**:
- Build: ./apps/api
- Command: celery -A app.workers.celery_app.celery_app worker --loglevel=INFO --concurrency=2
- Status: ✅ CONSISTENT

---

## Local Environment Audit

### Python Version

**Current**: Python 3.11.9
**Required**: Python >=3.11,<3.13
**Status**: ✅ COMPLIANT

### Virtual Environment

**Location**: `.venv` (project root)
**Python**: 3.11.9
**Status**: ✅ CORRECT

### Dependency Installation

**Method**: Layered requirements
- requirements-core.txt
- requirements-observability.txt
- requirements-ai.txt
- requirements-ml.txt
- constraints.txt
**Status**: ✅ IMPROVED

---

## Parity Issues

### Platform-Specific Differences

**Windows vs Linux**:
- Windows requires Visual C++ Build Tools for grpcio
- Linux has pre-built wheels for grpcio
- Docker uses Linux (no Windows-specific issues)
- Status: ⚠️ EXPECTED

### Path Handling

**Windows**:
- Path length limit: 260 characters
- Backslash separators
- Case-insensitive

**Linux (Docker)**:
- No path length limit
- Forward slash separators
- Case-sensitive
- Status: ⚠️ EXPECTED

### Multiprocessing

**Windows**:
- uvicorn --reload uses multiprocessing
- May have spawn issues
- Status: ⚠️ PLATFORM-SPECIFIC

**Linux (Docker)**:
- uvicorn --reload uses fork
- No spawn issues
- Status: ✅ STABLE

---

## Recommendations

### For Windows Development

1. **Use WSL 2 + Docker** (Recommended):
   - Avoid Windows-specific issues entirely
   - Use Linux environment for development
   - Docker for containerized development
   - Full parity with production

2. **Native Windows with Visual C++ Tools**:
   - Install Visual C++ Build Tools
   - Use layered dependency installation
   - Accept platform-specific differences
   - Test in Docker before deployment

### For Linux/Mac Development

1. **Native Development**:
   - Direct parity with Docker
   - No platform-specific issues
   - Use layered dependencies
   - Full parity with production

### For CI/CD

1. **Use Linux Runners**:
   - GitHub Actions: ubuntu-latest
   - GitLab CI: linux
   - Full parity with Docker
   - No platform-specific issues

---

## Next Steps

1. ✅ STEP 1: Complete dependency forensics (COMPLETE)
2. ✅ STEP 2: GRPC ecosystem stabilization (COMPLETE)
3. ✅ STEP 3: Full venv reconstruction (COMPLETE)
4. ✅ STEP 4: Layered dependency strategy (COMPLETE)
5. ✅ STEP 5: Windows compatibility hardening (COMPLETE)
6. ✅ STEP 6: Optional ML degradation (COMPLETE)
7. ✅ STEP 7: Startup isolation hardening (COMPLETE)
8. ✅ STEP 8: Backend validation matrix (COMPLETE)
9. ✅ STEP 9: Docker + local parity (COMPLETE)
10. ⏭️ STEP 10: Final target validation

---

## Conclusion

Docker and local environment parity has been improved by:
1. Updating Dockerfile to use layered dependencies
2. Pinning GRPC ecosystem versions in both environments
3. Installing GRPC ecosystem first for binary compatibility
4. Using consistent Python versions (3.11)

Platform-specific differences (Windows vs Linux) are expected and documented. For best parity, use WSL 2 + Docker on Windows.
