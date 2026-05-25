# Final Runtime Strategy - PHASE 22

## Single Authoritative Runtime Strategy

Based on comprehensive forensic analysis, this document defines the single authoritative runtime strategy for the project.

---

## Python Version Strategy

### Authoritative Python Version
- **Version**: Python 3.11.9
- **Range**: 3.11.x (specifically 3.11.9 for consistency)
- **Maximum**: 3.11.x (no 3.12, no 3.13, no 3.14)
- **Rationale**: 
  - pyproject.toml specifies `>=3.11,<3.13`
  - Dockerfile uses 3.11-slim
  - Venv is correctly using 3.11.9
  - 3.12 and 3.13 have potential compatibility issues with some ML packages

### Implementation
1. **Update pyproject.toml**:
   ```toml
   requires-python = ">=3.11,<3.12"
   ```

2. **Update Dockerfile**:
   ```dockerfile
   FROM python:3.11.9-slim AS builder
   FROM python:3.11.9-slim AS runtime
   ```

3. **Update bootstrap scripts**:
   ```bash
   # Only accept Python 3.11.x
   if [[ $PYTHON_VERSION =~ "Python 3.11" ]]; then
       echo "  ✓ Python version is compatible"
   else
       echo "  ✗ Python version is not compatible (requires 3.11.x)"
       exit 1
   fi
   ```

---

## Dependency Authority Strategy

### Authoritative Dependency Files

#### Production Dependencies
- **Primary**: requirements.txt (references layered files)
- **Layers**: 
  - requirements-core.txt (core + GRPC)
  - requirements-observability.txt (telemetry)
  - requirements-ai.txt (AI SDKs)
  - requirements-ml.txt (ML stack)

#### Development Dependencies
- **Primary**: requirements-dev.txt (references layered files + dev tools)

#### CI/Docker Constraints
- **Primary**: constraints.txt (direct package pins only, no file references)

### Updated requirements.txt
```txt
# Layered dependencies - PHASE 22
# Install in order: core -> observability -> ai -> ml
-r requirements-core.txt
-r requirements-observability.txt
-r requirements-ai.txt
-r requirements-ml.txt
```

### Updated constraints.txt
```txt
# Generated project constraints for deterministic CI installs.
# Runtime and dev requirements are intentionally pinned; this file exists so CI,
# Docker, and local bootstrap commands share one resolver boundary.

# GRPC ecosystem - pinned for Windows compatibility
grpcio==1.76.0
grpcio-tools==1.76.0
grpcio-status==1.76.0
protobuf==6.31.1

# Core dependencies - pinned for consistency
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
SQLAlchemy[asyncio]==2.0.36
asyncpg==0.30.0
redis==5.2.1
celery[redis]==5.4.0
qdrant-client==1.12.1
```

---

## Installation Order Strategy

### Authoritative Installation Order

#### Step 1: Environment Setup
```bash
# Validate Python version
python --version  # Must be 3.11.x

# Create venv
python -m venv .venv

# Activate venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
```

#### Step 2: Upgrade Build Tools
```bash
python -m pip install --upgrade pip setuptools wheel
```

#### Step 3: Install GRPC Ecosystem First
```bash
# Install GRPC first for binary compatibility (especially on Windows)
pip install --no-cache-dir grpcio==1.76.0 grpcio-tools==1.76.0 grpcio-status==1.76.0 protobuf==6.31.1
```

#### Step 4: Validate GRPC Installation
```bash
python -c "import grpc; from grpc._cython import cygrpc; print('✓ GRPC validated')"
```

#### Step 5: Install Core Dependencies
```bash
pip install --no-cache-dir -r requirements-core.txt
```

#### Step 6: Install Observability Dependencies
```bash
pip install --no-cache-dir -r requirements-observability.txt
```

#### Step 7: Install AI Dependencies
```bash
pip install --no-cache-dir -r requirements-ai.txt
```

#### Step 8: Install ML Dependencies
```bash
pip install --no-cache-dir -r requirements-ml.txt
```

#### Step 9: Validate Installation
```bash
python scripts/startup_forensics.py
```

#### Step 10: Install Dev Dependencies (Optional)
```bash
pip install --no-cache-dir -r requirements-dev.txt
```

---

## Version Standardization

### Standardized Versions

#### GRPC Ecosystem
- grpcio: 1.76.0
- grpcio-tools: 1.76.0
- grpcio-status: 1.76.0
- protobuf: 6.31.1

#### Core
- fastapi: 0.115.6
- uvicorn[standard]: 0.34.0
- pydantic: 2.10.4
- SQLAlchemy[asyncio]: 2.0.36
- asyncpg: 0.30.0
- redis: 5.2.1
- celery[redis]: 5.4.0
- qdrant-client: 1.12.1

#### Observability
- structlog: 24.4.0
- prometheus-client: 0.21.1
- prometheus-fastapi-instrumentator: 7.0.0
- opentelemetry-api: 1.29.0
- opentelemetry-sdk: 1.29.0
- opentelemetry-exporter-otlp: 1.29.0
- opentelemetry-instrumentation-fastapi: 0.50b0
- opentelemetry-instrumentation-sqlalchemy: 0.50b0
- opentelemetry-instrumentation-redis: 0.50b0
- opentelemetry-instrumentation-httpx: 0.50b0
- opentelemetry-instrumentation-celery: 0.50b0

#### AI
- google-generativeai: 0.8.3

#### ML
- sentence-transformers: 3.3.1
- transformers: 4.47.1
- torch: 2.12.0
- numpy: 2.2.3 (standardized)
- pandas: 2.2.3
- scikit-learn: 1.6.0
- xgboost: 2.1.3
- Pillow: 11.3.0 (standardized)
- pdfplumber: 0.11.5
- pymupdf: 1.25.1
- python-docx: 1.1.2
- pytesseract: 0.3.13
- mlflow: 2.19.0
- prefect: 3.1.12

---

## Docker Strategy

### Updated Dockerfile

```dockerfile
FROM python:3.11.9-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy layered requirements
COPY requirements-core.txt requirements-observability.txt requirements-ai.txt requirements-ml.txt ./
COPY constraints.txt ./

# Install GRPC ecosystem first (for binary compatibility)
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir \
       grpcio==1.76.0 \
       grpcio-tools==1.76.0 \
       grpcio-status==1.76.0 \
       protobuf==6.31.1

# Build wheels for all layers
RUN python -m pip wheel --wheel-dir /wheels -r requirements-core.txt \
    && python -m pip wheel --wheel-dir /wheels -r requirements-observability.txt \
    && python -m pip wheel --wheel-dir /wheels -r requirements-ai.txt \
    && python -m pip wheel --wheel-dir /wheels -r requirements-ml.txt


FROM python:3.11.9-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       libpq5 \
       tesseract-ocr \
       poppler-utils \
    && useradd --create-home --shell /usr/sbin/nologin appuser \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
COPY requirements-core.txt requirements-observability.txt requirements-ai.txt requirements-ml.txt ./
COPY constraints.txt ./
RUN python -m pip install --no-index --find-links=/wheels -r requirements-core.txt \
    && python -m pip install --no-index --find-links=/wheels -r requirements-observability.txt \
    && python -m pip install --no-index --find-links=/wheels -r requirements-ai.txt \
    && python -m pip install --no-index --find-links=/wheels -r requirements-ml.txt \
    && rm -rf /wheels

COPY app app
COPY alembic alembic
COPY alembic.ini alembic.ini

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:8000/ready || exit 1

CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Bootstrap Script Strategy

### Updated bootstrap.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

resolve_python() {
  # Only accept Python 3.11.x
  for candidate in python3.11 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 11) else 1)'; then
      echo "$candidate"
      return 0
    fi
  done
  echo "Python 3.11.x is required. Install Python 3.11.x, then rerun scripts/bootstrap.sh." >&2
  return 1
}

if [ ! -f ".env" ]; then
  cp ".env.example" ".env"
  echo "Created .env from .env.example. Update secrets before production use."
fi

PROJECT_PYTHON="$(resolve_python)"
"$PROJECT_PYTHON" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel

# Step 1: Install GRPC ecosystem first
echo "Installing GRPC ecosystem..."
pip install --no-cache-dir grpcio==1.76.0 grpcio-tools==1.76.0 grpcio-status==1.76.0 protobuf==6.31.1

# Step 2: Validate GRPC installation
echo "Validating GRPC installation..."
python -c "import grpc; from grpc._cython import cygrpc; print('✓ GRPC validated')"

# Step 3: Install core dependencies
echo "Installing core dependencies..."
pip install --no-cache-dir -r apps/api/requirements-core.txt

# Step 4: Install observability dependencies
echo "Installing observability dependencies..."
pip install --no-cache-dir -r apps/api/requirements-observability.txt

# Step 5: Install AI dependencies
echo "Installing AI dependencies..."
pip install --no-cache-dir -r apps/api/requirements-ai.txt

# Step 6: Install ML dependencies
echo "Installing ML dependencies..."
pip install --no-cache-dir -r apps/api/requirements-ml.txt

# Step 7: Install dev dependencies
echo "Installing dev dependencies..."
pip install --no-cache-dir -r apps/api/requirements-dev.txt

# Step 8: Validate installation
echo "Validating installation..."
python scripts/startup_forensics.py

if [ -f "apps/web/package.json" ]; then
  (cd apps/web && npm install)
fi

echo "Bootstrap complete. Activate with: source .venv/bin/activate"
```

---

## Configuration Strategy

### backend_cors_origins Format

**Current (Broken)**:
```
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8000
```

**Fixed**:
```
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:8000"]
```

### Security Fix
Remove hardcoded API key from .env:
```
# Before (INSECURE):
GEMINI_API_KEY=AIzaSyBshjRojHHc4WO8T6-7PK2RNlzO_j-eVO8

# After (SECURE):
GEMINI_API_KEY=your-api-key-here
```

---

## Validation Strategy

### Startup Validation Script
Use `scripts/startup_forensics.py` to validate:
- Python version
- All dependency imports
- App module imports
- App factory creation

### CI/CD Validation
Add to CI pipeline:
1. Python version check
2. Dependency installation validation
3. Import validation
4. Startup validation

---

## Elimination of Conflicts

### Eliminated
1. **Multiple Python versions** - Standardized on 3.11.9
2. **Multiple GRPC versions** - Standardized on 1.76.0
3. **Multiple numpy versions** - Standardized on 2.2.3
4. **Multiple Pillow versions** - Standardized on 11.3.0
5. **Circular references** - Removed from constraints.txt
6. **Monolithic vs layered confusion** - Updated requirements.txt to reference layers
7. **Incomplete local installation** - Bootstrap scripts now install all layers
8. **System Python contamination** - Always use venv Python

---

## Summary

### Single Source of Truth
- **Python Version**: 3.11.9
- **Dependencies**: Layered files (core, observability, ai, ml)
- **Installation Order**: GRPC → core → observability → ai → ml → dev
- **GRPC Version**: 1.76.0
- **Configuration**: JSON-formatted backend_cors_origins

### Implementation Priority
1. Fix backend_cors_origins in .env
2. Fix GRPC installation in venv
3. Install missing dependency layers
4. Update requirements.txt to reference layers
5. Update constraints.txt
6. Update Dockerfile
7. Update bootstrap scripts
8. Remove hardcoded API key
