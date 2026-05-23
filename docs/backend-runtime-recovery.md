# Backend Runtime Recovery - PHASE 20

**Date**: 2026-05-23
**Phase**: STEP 9 - DEVELOPER EXPERIENCE HARDENING

## Overview

This guide provides comprehensive instructions for recovering the backend runtime environment, addressing Python setup, virtual environment recreation, dependency recovery, startup troubleshooting, common ML dependency failures, Windows-specific fixes, and Docker troubleshooting.

## Python Setup

### Supported Python Versions

The platform requires:
- Python 3.11
- Python 3.12

**Unsupported**:
- Python 3.10 and below
- Python 3.13 and above (including 3.14)

### Installing Python

#### Windows

1. Download Python 3.11 or 3.12 from https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH"
4. Verify installation:
   ```powershell
   python --version
   ```

#### Linux/Mac

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv

# macOS (using Homebrew)
brew install python@3.11
```

### Verifying Python Version

```powershell
python --version
```

Expected output: `Python 3.11.x` or `Python 3.12.x`

---

## Virtual Environment Recreation

### Recreate from Scratch

#### Windows PowerShell

```powershell
cd c:\Users\Lenovo\Desktop\mlops-ai
.\scripts\rebuild_local_env.ps1
```

#### Linux/Mac

```bash
cd /path/to/mlops-ai
chmod +x scripts/rebuild_local_env.sh
./scripts/rebuild_local_env.sh
```

### Manual Recreation

#### Windows

```powershell
# Remove existing venv
Remove-Item -Recurse -Force .venv

# Create new venv
python -m venv .venv

# Activate venv
.venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel
```

#### Linux/Mac

```bash
# Remove existing venv
rm -rf .venv

# Create new venv
python -m venv .venv

# Activate venv
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel
```

---

## Dependency Recovery

### Install Core Dependencies

```powershell
# Windows
pip install -r apps/api/requirements-core.txt

# Linux/Mac
pip install -r apps/api/requirements-core.txt
```

### Install ML Dependencies (Optional)

```powershell
# Windows
pip install -r apps/api/requirements-ml.txt

# Linux/Mac
pip install -r apps/api/requirements-ml.txt
```

### Validate Dependencies

```powershell
python scripts/verify_python_runtime.py
python scripts/backend_validation.py
python scripts/validate_ml_stack.py
```

---

## Startup Troubleshooting

### Backend Won't Start

#### Symptom: Import Error

**Error**: `ModuleNotFoundError: No module named 'xxx'`

**Solution**:
```powershell
# Reinstall dependencies
pip install -r apps/api/requirements-core.txt
```

#### Symptom: Python Version Error

**Error**: Python version is not compatible

**Solution**:
```powershell
# Verify Python version
python --version

# If wrong version, install correct Python and recreate venv
.\scripts\rebuild_local_env.ps1
```

#### Symptom: Database Connection Error

**Error**: `OSError: Connect call failed ('127.0.0.1', 5432)`

**Solution**:
```powershell
# Start infrastructure
docker compose up -d postgres redis qdrant minio mlflow

# Wait for services to be healthy
docker compose ps

# Run migrations
cd apps/api
alembic upgrade head
```

#### Symptom: ML Dependency Error

**Error**: `RuntimeError: sentence-transformers is not installed`

**Solution**:
```powershell
# Install ML dependencies
pip install -r apps/api/requirements-ml.txt
```

---

## Common ML Dependency Failures

### pandas Installation Fails

**Error**: `ERROR: Could not find C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe`

**Cause**: Missing Visual Studio Build Tools

**Solution**:
1. Install Visual Studio Build Tools from https://visualstudio.microsoft.com/downloads/
2. Select "Desktop development with C++"
3. Reinstall pandas:
   ```powershell
   pip install pandas
   ```

**Alternative**: Use pre-built wheels
```powershell
pip install --only-binary :all: pandas
```

### torch Installation Fails

**Error**: `ERROR: Could not find a version that satisfies the requirement torch`

**Cause**: Python version incompatible or wheel not available

**Solution**:
```powershell
# Install from PyTorch website with correct Python version
# Visit https://pytorch.org/get-started/locally/
```

### sentence-transformers Installation Fails

**Error**: `ModuleNotFoundError: No module named 'sentence_transformers'`

**Cause**: Not installed or installation failed

**Solution**:
```powershell
# Install with pip
pip install sentence-transformers

# Or install from requirements
pip install -r apps/api/requirements-ml.txt
```

---

## Windows-Specific Fixes

### PowerShell Execution Policy

**Error**: `cannot be loaded because running scripts is disabled`

**Solution**:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### Path Issues

**Error**: `python: command not found`

**Solution**:
1. Ensure Python is added to PATH during installation
2. Restart PowerShell
3. Verify:
   ```powershell
   where python
   ```

### Docker Desktop Not Starting

**Error**: `docker: command not found`

**Solution**:
1. Install Docker Desktop for Windows
2. Start Docker Desktop
3. Verify:
   ```powershell
   docker --version
   ```

### WSL2 Issues

**Error**: Docker containers fail to start with WSL2 errors

**Solution**:
```powershell
# Restart WSL
wsl --shutdown

# Restart Docker Desktop
```

---

## Docker Troubleshooting

### Containers Won't Start

**Symptom**: Docker containers exit immediately

**Solution**:
```powershell
# Check container logs
docker compose logs <service-name>

# Check container status
docker compose ps

# Restart container
docker compose restart <service-name>

# Rebuild container
docker compose up -d --build <service-name>
```

### Port Conflicts

**Symptom**: Service fails to start with port conflict

**Solution**:
```powershell
# Windows: Check what's using port
netstat -ano | findstr :5432

# Linux/Mac: Check what's using port
lsof -i :5432

# Stop conflicting service or change port in docker-compose.yml
```

### Out of Disk Space

**Symptom**: Docker fails to start containers

**Solution**:
```powershell
# Clean up Docker resources
docker system prune -a

# Remove specific volumes
docker volume rm $(docker volume ls -q)

# Remove all volumes (WARNING: deletes data)
docker compose down -v
```

---

## Validation Scripts

### Verify Python Runtime

```powershell
python scripts/verify_python_runtime.py
```

### Validate ML Stack

```powershell
python scripts/validate_ml_stack.py
```

### Validate Backend

```powershell
python scripts/backend_validation.py
```

### Validate Infrastructure

```powershell
python scripts/validate_local_infra.py
```

---

## Quick Recovery Checklist

### Complete Environment Recovery

1. **Verify Python version**: `python --version` (must be 3.11 or 3.12)
2. **Recreate venv**: `.\scripts\rebuild_local_env.ps1` (Windows) or `./scripts/rebuild_local_env.sh` (Linux/Mac)
3. **Start infrastructure**: `docker compose up -d postgres redis qdrant minio mlflow`
4. **Run migrations**: `cd apps/api && alembic upgrade head`
5. **Validate**: `python scripts/backend_validation.py`
6. **Start backend**: `uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload`

### Quick Fix for Import Errors

1. **Reinstall dependencies**: `pip install -r apps/api/requirements-core.txt`
2. **Validate**: `python scripts/backend_validation.py`
3. **Restart backend**

### Quick Fix for ML Errors

1. **Install ML dependencies**: `pip install -r apps/api/requirements-ml.txt`
2. **Validate**: `python scripts/validate_ml_stack.py`
3. **Restart backend**

---

## Next Steps

1. ✅ STEP 1: Full backend forensic audit (COMPLETE)
2. ✅ STEP 2: Python runtime stabilization (COMPLETE)
3. ✅ STEP 3: Dependency graph reconstruction (COMPLETE)
4. ✅ STEP 4: Import + module consistency audit (COMPLETE)
5. ✅ STEP 5: Startup sequence hardening (COMPLETE)
6. ✅ STEP 6: AI/ML stack validation (COMPLETE)
7. ✅ STEP 7: Local environment reconstruction (COMPLETE)
8. ✅ STEP 8: Backend validation suite (COMPLETE)
9. ✅ STEP 9: Developer experience hardening (COMPLETE)
10. ⏭️ STEP 10: Final target validation

---

## Conclusion

This guide provides comprehensive recovery procedures for the backend runtime environment. The key issues identified during PHASE 20 were:
1. Python version drift (3.14 instead of 3.11/3.12)
2. Missing ML dependencies
3. Dependency installation failures

The recovery scripts and documentation provided address these issues and provide deterministic procedures for environment recovery.
