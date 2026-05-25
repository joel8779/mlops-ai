# Requirements File Reconciliation - PHASE 22

## Requirements Files Overview

### File Hierarchy
```
apps/api/
├── requirements.txt                 (Monolithic - 79 lines)
├── requirements-core.txt            (Layer 1 - 50 lines)
├── requirements-observability.txt  (Layer 3 - 25 lines)
├── requirements-ai.txt             (Layer 4 - 9 lines)
├── requirements-ml.txt              (Layer 2 - 30 lines)
├── requirements-dev.txt            (Dev - 32 lines, references layers)
└── constraints.txt                  (CI/Docker constraints - 13 lines)
```

---

## Detailed Comparison

### 1. requirements.txt vs requirements-core.txt

#### Packages in requirements.txt but NOT in requirements-core.txt
- sentence-transformers==3.3.1 (ML layer)
- transformers==4.47.1 (ML layer)
- torch==2.12.0 (ML layer)
- networkx==3.4.2 (ML layer)
- mlflow==2.19.0 (ML layer)
- prefect==3.1.12 (ML layer)
- pdfplumber==0.11.5 (ML layer)
- pymupdf==1.25.1 (ML layer)
- python-docx==1.1.2 (ML layer)
- pytesseract==0.3.13 (ML layer)
- Pillow==11.0.0 (ML layer - version mismatch)
- pandas==2.2.3 (ML layer)
- numpy==1.26.4 (ML layer - version mismatch)
- scikit-learn==1.6.0 (ML layer)
- google-generativeai==0.8.3 (AI layer)
- xgboost==2.1.3 (ML layer)
- joblib==1.4.2 (ML layer)
- structlog==24.4.0 (Observability layer)
- prometheus-client==0.21.1 (Observability layer)
- prometheus-fastapi-instrumentator==7.0.0 (Observability layer)
- opentelemetry-api==1.29.0 (Observability layer)
- opentelemetry-sdk==1.29.0 (Observability layer)
- opentelemetry-exporter-otlp==1.29.0 (Observability layer)
- opentelemetry-instrumentation-fastapi==0.50b0 (Observability layer)
- opentelemetry-instrumentation-sqlalchemy==0.50b0 (Observability layer)
- opentelemetry-instrumentation-redis==0.50b0 (Observability layer)
- opentelemetry-instrumentation-httpx==0.50b0 (Observability layer)
- opentelemetry-instrumentation-celery==0.50b0 (Observability layer)

#### Packages in requirements-core.txt but NOT in requirements.txt
- grpcio==1.76.0 (GRPC ecosystem)
- grpcio-tools==1.76.0 (GRPC ecosystem)
- grpcio-status==1.76.0 (GRPC ecosystem)
- protobuf==6.31.1 (GRPC ecosystem)

#### Version Conflicts
- **numpy**: requirements.txt has 1.26.4, requirements-ml.txt has 2.2.3
- **Pillow**: requirements.txt has 11.0.0, requirements-ml.txt has 11.3.0

### 2. requirements-dev.txt Structure

#### References Other Files
```
-r requirements-core.txt
-r requirements-observability.txt
-r requirements-ai.txt
-r requirements-ml.txt
```

#### Additional Dev Packages
- pytest==8.3.4
- pytest-asyncio==0.25.0
- pytest-cov==6.0.0
- coverage[toml]==7.6.10
- factory-boy==3.3.1
- freezegun==1.5.1
- respx==0.21.1
- locust==2.32.5
- pip-audit==2.7.3
- bandit==1.7.10
- PyYAML==6.0.3
- ruff==0.8.4
- mypy==1.14.0
- black==24.10.0
- types-python-jose==3.3.4.20240106
- types-passlib==1.7.7.20240819
- types-redis==4.6.0.20241004
- ipython==8.31.0
- pre-commit==4.0.1

### 3. constraints.txt Issues

#### Contains Both Direct Pins and File Reference
```
grpcio==1.76.0
grpcio-tools==1.76.0
grpcio-status==1.76.0
protobuf==6.31.1
-r requirements-core.txt
```

#### Problem
- Mixes direct package pins with file reference
- Creates potential circular reference if used with requirements-dev.txt
- Unclear whether constraints.txt should be used standalone or with other files

---

## Which File Should Be Authoritative?

### Analysis

#### Option A: requirements.txt (Monolithic)
**Pros**:
- Single file for all dependencies
- Simple for basic deployment
- Compatible with traditional pip install -r requirements.txt

**Cons**:
- Conflicts with layered strategy
- Hard to install subsets of dependencies
- Version drift between files
- Not aligned with PHASE 21 layered installation strategy

#### Option B: Layered Files (core, observability, ai, ml)
**Pros**:
- Aligned with PHASE 21 strategy
- Allows incremental installation
- Better for CI/CD (install only what's needed)
- Clear separation of concerns

**Cons**:
- More complex to manage
- Requires installation in specific order
- Not compatible with simple pip install -r requirements.txt

#### Option C: requirements-dev.txt as Primary
**Pros**:
- References all layered files
- Single entry point for development
- Maintains layered structure

**Cons**:
- Includes dev dependencies not needed for production
- Still requires layered files to exist

### Recommendation

**Primary Authoritative File**: requirements-dev.txt (for development)
**Production Authoritative**: Use layered files in Dockerfile

**Update requirements.txt** to reference layered files instead of listing all packages:
```
# Layered dependencies - PHASE 22
# Install in order: core -> observability -> ai -> ml
-r requirements-core.txt
-r requirements-observability.txt
-r requirements-ai.txt
-r requirements-ml.txt
```

This way:
- `pip install -r requirements.txt` installs all production dependencies
- `pip install -r requirements-dev.txt` installs all dependencies including dev tools
- Docker can still use layered files for multi-stage builds
- No version drift between files

---

## Version Conflicts Resolution

### 1. Numpy
- **Current state**: requirements.txt has 1.26.4, requirements-ml.txt has 2.2.3, installed has 2.4.6
- **Resolution**: Use 2.2.3 (latest in requirements-ml.txt)
- **Action**: Update requirements.txt to remove numpy (let requirements-ml.txt be authoritative)

### 2. Pillow
- **Current state**: requirements.txt has 11.0.0, requirements-ml.txt has 11.3.0
- **Resolution**: Use 11.3.0 (latest in requirements-ml.txt)
- **Action**: Update requirements.txt to remove Pillow (let requirements-ml.txt be authoritative)

### 3. GRPC
- **Current state**: Dockerfile has 1.60.0, requirements-core.txt has 1.76.0, constraints.txt has 1.76.0
- **Resolution**: Use 1.76.0 (latest in requirements)
- **Action**: Update Dockerfile to use 1.76.0

---

## Circular Reference Resolution

### constraints.txt Issue
- **Current**: Contains `-r requirements-core.txt`
- **Problem**: Creates circular reference if used with requirements-dev.txt
- **Resolution**: Remove `-r requirements-core.txt` from constraints.txt
- **New constraints.txt**:
```
# Generated project constraints for deterministic CI installs.
# Runtime and dev requirements are intentionally pinned; this file exists so CI,
# Docker, and local bootstrap commands share one resolver boundary.

# GRPC ecosystem - pinned for Windows compatibility
grpcio==1.76.0
grpcio-tools==1.76.0
grpcio-status==1.76.0
protobuf==6.31.1
```

---

## Installation Order Validation

### Correct Order (from PHASE 21)
1. Install core dependencies (requirements-core.txt)
2. Install observability dependencies (requirements-observability.txt)
3. Install AI dependencies (requirements-ai.txt)
4. Install ML dependencies (requirements-ml.txt)
5. Install dev dependencies (requirements-dev.txt)

### Why This Order?
- Core: Base runtime, DB, GRPC (must be first for GRPC binary compatibility)
- Observability: Telemetry stack (depends on core)
- AI: AI SDKs (depends on core)
- ML: ML stack (depends on core, can be installed after AI)
- Dev: Development tools (depends on all above)

---

## Final Recommendations

### Immediate Actions
1. Update requirements.txt to reference layered files instead of listing all packages
2. Update Dockerfile to use grpcio==1.76.0 (match requirements-core.txt)
3. Remove numpy and Pillow from requirements.txt (let requirements-ml.txt be authoritative)
4. Remove `-r requirements-core.txt` from constraints.txt

### Bootstrap Script Updates
1. Update scripts/bootstrap.sh to install all layers in correct order
2. Update scripts/full_runtime_recovery.sh to install all layers in correct order
3. Add validation after each layer installation
4. Add final validation to ensure all layers are installed

### Documentation Updates
1. Document the layered installation strategy in README.md
2. Add installation instructions for each layer
3. Add troubleshooting guide for dependency issues
