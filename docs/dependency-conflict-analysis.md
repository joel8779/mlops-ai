# Dependency Conflict Analysis - PHASE 22

## Critical Conflicts Identified

---

## 1. GRPC Version Conflict (CRITICAL)

### Conflict Sources
- **Dockerfile**: grpcio==1.60.0
- **requirements-core.txt**: grpcio==1.76.0
- **constraints.txt**: grpcio==1.76.0

### Impact
- Docker builds will use grpcio 1.60.0
- Local development will use grpcio 1.76.0
- Runtime inconsistency between environments
- Potential ABI compatibility issues

### Root Cause
Dockerfile was not updated when GRPC version was pinned to 1.76.0 in requirements files.

### Resolution
- **Option 1**: Downgrade requirements to 1.60.0 (match Docker)
- **Option 2**: Upgrade Dockerfile to 1.76.0 (match requirements)
- **Recommendation**: Option 2 - use latest stable version

---

## 2. Numpy Version Drift

### Conflict Sources
- **Installed**: numpy 2.4.6
- **requirements-ml.txt**: numpy 2.2.3
- **requirements.txt**: numpy 1.26.4

### Impact
- Version mismatch between different requirements files
- Potential compatibility issues with ML packages
- Unclear which version is authoritative

### Root Cause
requirements.txt was not updated when numpy version was changed in requirements-ml.txt.

### Resolution
- Standardize on numpy 2.2.3 (latest in requirements-ml.txt)
- Update requirements.txt to match
- Remove numpy from requirements.txt (let requirements-ml.txt be authoritative)

---

## 3. Requirements File Strategy Conflict

### Conflict Sources
- **requirements.txt**: Monolithic file with ALL dependencies
- **requirements-core.txt**: Layer 1 dependencies
- **requirements-observability.txt**: Layer 3 dependencies
- **requirements-ai.txt**: Layer 4 dependencies
- **requirements-ml.txt**: Layer 2 dependencies
- **requirements-dev.txt**: References layered files

### Impact
- Unclear which file is authoritative
- Potential for version drift between files
- Confusing installation strategy
- Docker uses layered files, but local may use monolithic file

### Root Cause
Transition to layered dependency strategy was incomplete. Old monolithic requirements.txt was kept alongside new layered files.

### Resolution
- **Option 1**: Remove requirements.txt, use only layered files
- **Option 2**: Make requirements.txt reference layered files (like requirements-dev.txt)
- **Recommendation**: Option 2 - update requirements.txt to reference layered files

---

## 4. Circular Reference in constraints.txt

### Conflict Sources
- **constraints.txt** contains: `-r requirements-core.txt`
- **requirements-dev.txt** references: requirements-core.txt, requirements-observability.txt, requirements-ai.txt, requirements-ml.txt
- If constraints.txt is used with requirements-dev.txt, creates circular reference

### Impact
- Pip resolver may fail or produce unexpected results
- Unclear dependency resolution order

### Root Cause
constraints.txt was designed to be used alone, but also references requirements-core.txt.

### Resolution
- Remove `-r requirements-core.txt` from constraints.txt
- List actual package versions in constraints.txt instead

---

## 5. Missing Dependency Layers

### Conflict Sources
- **Venv state**: Only core dependencies installed
- **App code**: Imports from all layers (core, observability, AI, ML)
- **Installation strategy**: Layered installation defined but not executed

### Impact
- App imports fail due to missing dependencies
- Cannot start backend
- Cannot run tests
- Cannot develop features

### Root Cause
Layered installation strategy was designed but bootstrap scripts did not implement it correctly.

### Resolution
- Update bootstrap scripts to install all layers in correct order
- Add validation after each layer installation
- Ensure all layers are installed before attempting to run app

---

## 6. Broken GRPC Installation

### Conflict Sources
- **Installed**: grpcio-status==1.76.0, grpcio-tools==1.76.0
- **Missing**: grpcio==1.76.0
- **Dependency chain**: grpcio-tools depends on grpcio

### Impact
- GRPC tools cannot function without grpcio
- Any code using GRPC will fail
- Broken dependency state

### Root Cause
Likely installation failure or partial installation. grpcio installation may have failed but tools were still installed.

### Resolution
- Reinstall grpcio: `pip install grpcio==1.76.0 --force-reinstall`
- Validate installation: `python -c "import grpc; from grpc._cython import cygrpc"`

---

## 7. Pillow Version Drift

### Conflict Sources
- **requirements.txt**: Pillow==11.0.0
- **requirements-ml.txt**: Pillow==11.3.0

### Impact
- Version mismatch between files
- Potential compatibility issues

### Root Cause
requirements.txt was not updated when Pillow version was changed in requirements-ml.txt.

### Resolution
- Standardize on Pillow 11.3.0
- Update requirements.txt to match

---

## Dependency Tree Analysis

### Core Layer Dependencies
```
fastapi==0.115.6
├── starlette>=0.40.0
├── pydantic>=2.0
├── typing-extensions>=4.8.0
├── anyio>=3.9.0
└── uvicorn[standard]==0.34.0
    ├── uvloop
    ├── httptools
    ├── websockets>=13.1
    └── watchfiles

pydantic==2.10.4
├── pydantic-core==2.27.2
├── typing-extensions>=4.6.1
└── annotated-types>=0.6.0

SQLAlchemy[asyncio]==2.0.36
├── greenlet!=0.4.17
├── typing-extensions>=4.6.0
└── asyncpg==0.30.0

redis==5.2.1
└── async-timeout>=4.0.3

celery[redis]==5.4.0
├── billiard>=4.2.0
├── kombu>=5.3.4
│   ├── amqp>=5.3.1
│   └── vine>=5.1.0
└── redis>=5.2.1

grpcio==1.76.0 (MISSING)
grpcio-tools==1.76.0 (installed without grpcio - BROKEN)
grpcio-status==1.76.0 (installed without grpcio - BROKEN)
```

### Observability Layer Dependencies
```
structlog==24.4.0 (MISSING)

prometheus-client==0.21.1 (MISSING)

prometheus-fastapi-instrumentator==7.0.0 (MISSING)
├── prometheus-client>=0.7.0

opentelemetry-api==1.29.0 (MISSING)
opentelemetry-sdk==1.29.0 (MISSING)
├── opentelemetry-api>=1.29.0
└── opentelemetry-semantic-conventions>=0.46b0

opentelemetry-exporter-otlp==1.29.0 (MISSING)
├── opentelemetry-api>=1.29.0
├── opentelemetry-sdk>=1.29.0
└── grpcio>=1.60.0

opentelemetry-instrumentation-fastapi==0.50b0 (MISSING)
opentelemetry-instrumentation-sqlalchemy==0.50b0 (MISSING)
opentelemetry-instrumentation-redis==0.50b0 (MISSING)
opentelemetry-instrumentation-httpx==0.50b0 (MISSING)
opentelemetry-instrumentation-celery==0.50b0 (MISSING)
```

### AI Layer Dependencies
```
google-generativeai==0.8.3 (MISSING)
├── google-api-core>=2.10.2
├── google-auth>=2.15.0
└── protobuf>=3.20.2
```

### ML Layer Dependencies
```
torch==2.12.0 (MISSING)
├── networkx
├── jinja2
└── sympy

transformers==4.47.1 (MISSING)
├── tokenizers>=0.15.0
├── safetensors>=0.4.1
├── huggingface-hub>=0.15.1
├── numpy>=1.17
├── packaging>=20.0
├── pyyaml>=5.1
├── regex!=2019.12.17
└── requests

sentence-transformers==3.3.1 (MISSING)
├── transformers>=4.34.0
├── torch>=1.11.0
├── sentencepiece>=0.1.99
├── scikit-learn
├── numpy
└── tqdm

numpy==2.2.3 (MISSING - installed 2.4.6 instead)

pandas==2.2.3 (MISSING)
├── numpy>=1.23.5
├── python-dateutil>=2.8.2
└── pytz>=2022.7

scikit-learn==1.6.0 (MISSING)
├── numpy>=1.19.5
├── scipy>=1.6.0
├── joblib>=1.2.0
└── threadpoolctl>=3.1.0

xgboost==2.1.3 (MISSING)
├── numpy
└── scipy

mlflow==2.19.0 (MISSING)
├── sqlalchemy
├── numpy
├── pandas
├── scikit-learn
└── protobuf

prefect==3.1.12 (MISSING)
├── pydantic>=2.0
├── sqlalchemy
└── httpx
```

---

## Impossible Resolver Combinations

### None Detected
All dependency versions appear compatible. No impossible resolver combinations found.

---

## Duplicate Package Constraints

### None Detected
No duplicate package constraints with conflicting versions found within individual requirements files.

---

## Recommendations

### Immediate Actions
1. Fix GRPC version conflict between Dockerfile and requirements
2. Fix broken GRPC installation in venv
3. Install missing dependency layers (observability, AI, ML)
4. Standardize numpy version across all requirements files

### Long-term Actions
1. Establish single authoritative requirements strategy
2. Remove or update monolithic requirements.txt
3. Fix circular reference in constraints.txt
4. Update bootstrap scripts to install all layers
5. Add dependency validation to CI/CD
