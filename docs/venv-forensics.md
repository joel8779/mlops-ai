# Venv Forensics - PHASE 22

## Virtual Environment Configuration

### Creation Details
- **Python Version**: 3.11.9 ✅ (CORRECT)
- **Base Interpreter**: C:\Users\AppData\Local\Python\pythoncore-3.11-64\python.exe
- **Creation Command**: `python -m venv C:\Users\Lenovo\Desktop\mlops-ai\.venv`
- **Isolation**: No system-site-packages ✅

### pyvenv.cfg Contents
```
home = C:\Users\AppData\Local\Python\pythoncore-3.11-64
include-system-site-packages = false
version = 3.11.9
executable = C:\Users\AppData\Local\Python\pythoncore-3.11-64\python.exe
command = C:\Users\AppData\Local\Python\pythoncore-3.11-64\python.exe -m venv C:\Users\Lenovo\Desktop\mlops-ai\.venv
```

---

## Installation State Analysis

### Pip Configuration
- **Pip Version**: 26.1.1
- **Location**: C:\Users\Lenovo\Desktop\mlops-ai\.venv\Lib\site-packages\pip
- **Status**: Latest stable version ✅

### Installed Packages Count
- **Total Packages**: 62 packages
- **Expected Total**: ~100+ packages (if all layers installed)
- **Missing**: ~40+ packages (observability, AI, ML layers)

---

## Dependency Layer Installation Status

### Layer 1: Core Dependencies ✅ PARTIALLY INSTALLED
**Expected from**: requirements-core.txt

**Installed**:
- fastapi==0.115.6 ✅
- uvicorn[standard]==0.34.0 ✅
- pydantic==2.10.4 ✅
- SQLAlchemy[asyncio]==2.0.36 ✅
- asyncpg==0.30.0 ✅
- redis==5.2.1 ✅
- celery[redis]==5.4.0 ✅
- qdrant-client==1.12.1 ✅
- boto3==1.35.90 ✅
- neo4j==5.27.0 ✅
- numpy==2.4.6 ⚠️ (version mismatch)

**Missing/Broken**:
- grpcio==1.76.0 ❌ (CRITICAL - grpcio-tools and grpcio-status are installed but grpcio itself is missing)
- grpcio-tools==1.76.0 ✅ (installed without grpcio - BROKEN STATE)
- grpcio-status==1.76.0 ✅ (installed without grpcio - BROKEN STATE)
- protobuf==6.31.1 ❌

### Layer 2: ML Dependencies ❌ NOT INSTALLED
**Expected from**: requirements-ml.txt

**Missing**:
- sentence-transformers==3.3.1 ❌
- transformers==4.47.1 ❌
- torch==2.12.0 ❌
- networkx==3.4.2 ❌
- mlflow==2.19.0 ❌
- prefect==3.1.12 ❌
- pdfplumber==0.11.5 ❌
- pymupdf==1.25.1 ❌
- python-docx==1.1.2 ❌
- pytesseract==0.3.13 ❌
- Pillow==11.3.0 ❌
- pandas==2.2.3 ❌
- scikit-learn==1.6.0 ❌
- xgboost==2.1.3 ❌
- joblib==1.4.2 ❌

### Layer 3: Observability Dependencies ❌ NOT INSTALLED
**Expected from**: requirements-observability.txt

**Missing**:
- structlog==24.4.0 ❌
- prometheus-client==0.21.1 ❌
- prometheus-fastapi-instrumentator==7.0.0 ❌
- opentelemetry-api==1.29.0 ❌
- opentelemetry-sdk==1.29.0 ❌
- opentelemetry-exporter-otlp==1.29.0 ❌
- opentelemetry-instrumentation-fastapi==0.50b0 ❌
- opentelemetry-instrumentation-sqlalchemy==0.50b0 ❌
- opentelemetry-instrumentation-redis==0.50b0 ❌
- opentelemetry-instrumentation-httpx==0.50b0 ❌
- opentelemetry-instrumentation-celery==0.50b0 ❌

### Layer 4: AI Dependencies ❌ NOT INSTALLED
**Expected from**: requirements-ai.txt

**Missing**:
- google-generativeai==0.8.3 ❌

---

## Critical Issues

### 1. Broken GRPC Installation
- **grpcio-status** and **grpcio-tools** are installed
- **grpcio** itself is NOT installed
- This is a broken dependency state
- grpcio-tools depends on grpcio, so this should not be possible
- **Likely cause**: Partial installation or installation failure

### 2. Missing Observability Layer
- All telemetry packages are missing
- App imports will fail at:
  - `app.logging` (requires structlog)
  - `app.observability.tracing` (requires opentelemetry)
  - `prometheus_fastapi_instrumentator` (requires prometheus packages)

### 3. Missing AI Layer
- google-generativeai is not installed
- App imports will fail at:
  - Any Gemini/AI integration code

### 4. Missing ML Layer
- All ML packages are missing
- App imports will fail at:
  - Embedding services
  - Semantic search
  - Document parsing
  - OCR services

### 5. Numpy Version Drift
- **Installed**: numpy 2.4.6
- **requirements-ml.txt**: numpy 2.2.3
- **requirements.txt**: numpy 1.26.4
- **Impact**: Potential compatibility issues with ML packages

---

## Installation Strategy Failure

### Expected Installation Order (from PHASE 21)
1. Install core dependencies (requirements-core.txt)
2. Install observability dependencies (requirements-observability.txt)
3. Install AI dependencies (requirements-ai.txt)
4. Install ML dependencies (requirements-ml.txt)
5. Install dev dependencies (requirements-dev.txt)

### Actual Installation State
- **Step 1**: Partially completed (grpcio broken)
- **Step 2**: Not completed
- **Step 3**: Not completed
- **Step 4**: Not completed
- **Step 5**: Not completed

### Root Cause
The layered installation strategy was designed but not executed. Only the core layer was partially installed, and even that has a broken GRPC installation.

---

## Site-packages Contamination Check

### User-Site Leakage
- **include-system-site-packages**: false ✅
- **User site-packages in sys.path**: No ✅
- **Global site-packages in sys.path**: No ✅

### Conclusion
The venv is properly isolated. There is no site-packages contamination. The issue is purely missing dependencies, not environment contamination.

---

## ABI Wheel Compatibility

### Python 3.11.9 ABI Tags
- **Expected wheel tags**: cp311, cp311-win_amd64
- **Installed packages**: All appear to be correct cp311 wheels
- **No cp313 wheels detected**: ✅

### Conclusion
No ABI mismatch issues. All installed packages are compatible with Python 3.11.9.

---

## Remediation Plan

### Immediate Actions Required
1. **Fix GRPC installation**:
   ```bash
   .venv\Scripts\pip.exe install grpcio==1.76.0
   ```

2. **Install observability layer**:
   ```bash
   .venv\Scripts\pip.exe install -r apps/api/requirements-observability.txt
   ```

3. **Install AI layer**:
   ```bash
   .venv\Scripts\pip.exe install -r apps/api/requirements-ai.txt
   ```

4. **Install ML layer**:
   ```bash
   .venv\Scripts\pip.exe install -r apps/api/requirements-ml.txt
   ```

5. **Validate installation**:
   ```bash
   .venv\Scripts\python.exe scripts/startup_forensics.py
   ```

### Long-term Fix
- Ensure bootstrap scripts install all layers in correct order
- Add validation after each layer installation
- Fix GRPC version conflict between Dockerfile and requirements files
