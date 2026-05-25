# Docker vs Local Parity Analysis - PHASE 22

## Docker Runtime Configuration

### Dockerfile Analysis (apps/api/Dockerfile)

#### Base Image
```
FROM python:3.11-slim AS builder
FROM python:3.11-slim AS runtime
```
**Status**: ✅ Correct Python version (3.11)

#### GRPC Installation
```dockerfile
RUN python -m pip install --no-cache-dir \
   grpcio==1.60.0 \
   grpcio-tools==1.60.0 \
   grpcio-status==1.60.0 \
   protobuf==4.25.1
```
**Status**: ❌ Version mismatch with requirements files
- Docker: grpcio 1.60.0
- Requirements: grpcio 1.76.0
- **Impact**: Runtime inconsistency

#### Dependency Installation Order
```dockerfile
# Install GRPC ecosystem first (for binary compatibility)
RUN python -m pip install grpcio==1.60.0 ...

# Build wheels for all layers
RUN python -m pip wheel --wheel-dir /wheels -r requirements-core.txt
RUN python -m pip wheel --wheel-dir /wheels -r requirements-observability.txt
RUN python -m pip wheel --wheel-dir /wheels -r requirements-ai.txt
RUN python -m pip wheel --wheel-dir /wheels -r requirements-ml.txt
```
**Status**: ✅ Correct layered installation order
- GRPC installed first for binary compatibility
- All layers installed in correct order

#### Runtime Installation
```dockerfile
RUN python -m pip install --no-index --find-links=/wheels -r requirements-core.txt
RUN python -m pip install --no-index --find-links=/wheels -r requirements-observability.txt
RUN python -m pip install --no-index --find-links=/wheels -r requirements-ai.txt
RUN python -m pip install --no-index --find-links=/wheels -r requirements-ml.txt
```
**Status**: ✅ Correct layered installation order

#### Startup Command
```dockerfile
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
```
**Status**: ✅ Correct factory pattern

---

## Local Runtime Configuration

### Current State
- **Python Version**: 3.11.9 (venv) ✅
- **System Python**: 3.14.5 (incompatible) ❌
- **Installation**: Partial (only core layer) ❌
- **GRPC**: Broken (grpcio missing) ❌

### Bootstrap Script Analysis (scripts/bootstrap.sh)

#### Python Version Detection
```bash
resolve_python() {
  for candidate in python3.11 python3.12 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] < (3, 13) else 1'; then
      echo "$candidate"
      return 0
    fi
  done
}
```
**Status**: ✅ Correct version detection (3.11-3.12)

#### Installation Command
```bash
python -m pip install -r apps/api/requirements-dev.txt
```
**Status**: ❌ Incorrect
- Should install layers in order
- requirements-dev.txt references layered files, but this may not work correctly if layers are missing
- No validation after installation

#### Missing Steps
- No GRPC pre-installation for binary compatibility
- No layered installation validation
- No GRPC installation validation

### Runtime Recovery Script (scripts/full_runtime_recovery.sh)

#### Installation Order
```bash
# Step 7: Install GRPC ecosystem first
pip install --no-cache-dir grpcio==1.60.0 grpcio-tools==1.60.0 grpcio-status==1.60.0 protobuf==4.25.1

# Step 9: Install core dependencies
pip install --no-cache-dir -r apps/api/requirements-core.txt
```
**Status**: ❌ Version mismatch with requirements files
- Script uses grpcio 1.60.0
- Requirements files use grpcio 1.76.0
- **Impact**: Runtime inconsistency with Docker

#### Missing Steps
- Does not install observability layer
- Does not install AI layer
- Does not install ML layer
- Only installs core layer

---

## docker-compose.yml Analysis

### API Service Configuration
```yaml
api:
  build:
    context: ./apps/api
  command: uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
  env_file:
    - .env
  volumes:
    - ./apps/api/app:/app/app
    - ./apps/api/alembic:/app/alembic
    - ./apps/api/alembic.ini:/app/alembic.ini
```
**Status**: ✅ Correct configuration
- Uses Dockerfile for build
- Correct factory pattern
- Mounts app directory for development

### docker-compose.dev.yml Analysis

#### Additional Services
- neo4j
- prometheus
- loki
- grafana

**Status**: ✅ Correct development configuration

---

## Environment Variables Comparison

### Docker Environment
```yaml
environment:
  DATABASE_URL: postgresql+asyncpg://resume:resume@postgres:5432/resume_ai
  SYNC_DATABASE_URL: postgresql+psycopg://resume:resume@postgres:5432/resume_ai
  REDIS_URL: redis://redis:6379/0
  CELERY_BROKER_URL: redis://redis:6379/1
  CELERY_RESULT_BACKEND: redis://redis:6379/2
  QDRANT_URL: http://qdrant:6333
  S3_ENDPOINT_URL: http://minio:9000
  MLFLOW_TRACKING_URI: http://mlflow:5000
  NEO4J_URI: bolt://neo4j:7687
  OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
  LOKI_URL: http://loki:3100
```

### Local Environment (.env)
```
DATABASE_URL=postgresql+asyncpg://resume:resume@localhost:5432/resume_ai
SYNC_DATABASE_URL=postgresql+psycopg://resume:resume@localhost:5432/resume_ai
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
QDRANT_URL=http://localhost:6333
S3_ENDPOINT_URL=http://localhost:9000
MLFLOW_TRACKING_URI=http://localhost:5000
NEO4J_URI=bolt://localhost:7687
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
LOKI_URL=http://localhost:3100
```

**Status**: ✅ Correct parity
- Docker uses service names (postgres, redis, qdrant)
- Local uses localhost
- This is expected and correct

---

## Dependency Version Comparison

### GRPC Ecosystem
| Source | grpcio | grpcio-tools | grpcio-status | protobuf |
|--------|--------|--------------|---------------|----------|
| Dockerfile | 1.60.0 | 1.60.0 | 1.60.0 | 4.25.1 |
| requirements-core.txt | 1.76.0 | 1.76.0 | 1.76.0 | 6.31.1 |
| constraints.txt | 1.76.0 | 1.76.0 | 1.76.0 | 6.31.1 |
| full_runtime_recovery.sh | 1.60.0 | 1.60.0 | 1.60.0 | 4.25.1 |
| Local venv | MISSING | 1.76.0 | 1.76.0 | 6.31.1 |

**Status**: ❌ CRITICAL MISMATCH
- Docker uses 1.60.0
- Requirements use 1.76.0
- Local venv has broken installation

### Numpy
| Source | numpy |
|--------|-------|
| requirements.txt | 1.26.4 |
| requirements-ml.txt | 2.2.3 |
| Local venv | 2.4.6 |

**Status**: ❌ VERSION DRIFT
- Three different versions across files
- Local venv has yet another version

### Pillow
| Source | Pillow |
|--------|--------|
| requirements.txt | 11.0.0 |
| requirements-ml.txt | 11.3.0 |
| Local venv | MISSING |

**Status**: ❌ VERSION DRIFT
- Two different versions across files
- Local venv missing entirely

---

## Installation Strategy Comparison

### Docker Strategy
1. Install GRPC ecosystem first (1.60.0)
2. Build wheels for all layers
3. Install all layers from wheels
4. Use --no-index for reproducibility

**Status**: ✅ Correct layered strategy
**Issue**: Wrong GRPC version

### Local Strategy (bootstrap.sh)
1. Detect Python version
2. Create venv
3. Install requirements-dev.txt (single command)

**Status**: ❌ Incorrect
- No layered installation
- No GRPC pre-installation
- No validation

### Local Strategy (full_runtime_recovery.sh)
1. Validate Python version
2. Remove venv
3. Recreate venv
4. Install GRPC ecosystem (1.60.0)
5. Install core dependencies only

**Status**: ❌ Incomplete
- Only installs core layer
- Wrong GRPC version
- Missing observability, AI, ML layers

---

## Parity Issues Summary

### Critical Issues
1. **GRPC version mismatch** - Docker uses 1.60.0, requirements use 1.76.0
2. **Local installation incomplete** - Only core layer installed locally
3. **GRPC installation broken locally** - grpcio missing
4. **Bootstrap scripts outdated** - Do not implement layered strategy

### High Issues
1. **Numpy version drift** - Three different versions
2. **Pillow version drift** - Two different versions
3. **System Python mismatch** - Local uses 3.14.5 by default

### Medium Issues
1. **Configuration parsing error** - backend_cors_origins malformed
2. **Missing validation** - No post-installation validation in scripts

---

## Root Cause

### Primary Root Cause
The layered dependency strategy was designed for Docker but not implemented for local development. Bootstrap scripts do not follow the same installation order as Dockerfile, leading to:
1. Incomplete local installation
2. Version mismatches between environments
3. Broken GRPC installation

### Secondary Root Cause
Version drift between requirements files was not resolved when transitioning to layered strategy. Old monolithic requirements.txt was kept alongside new layered files, leading to confusion about which file is authoritative.

---

## Resolution Strategy

### Immediate Actions
1. **Standardize GRPC version** to 1.76.0 across all sources:
   - Update Dockerfile to use grpcio 1.76.0
   - Update full_runtime_recovery.sh to use grpcio 1.76.0
   - Fix local grpcio installation

2. **Complete local installation**:
   - Install observability layer
   - Install AI layer
   - Install ML layer

3. **Fix bootstrap scripts**:
   - Update bootstrap.sh to use layered installation
   - Update full_runtime_recovery.sh to install all layers
   - Add validation after each layer

### Long-term Actions
1. **Standardize numpy version** to 2.2.3 across all files
2. **Standardize Pillow version** to 11.3.0 across all files
3. **Update requirements.txt** to reference layered files
4. **Remove hardcoded API key** from .env
5. **Fix backend_cors_origins** configuration
