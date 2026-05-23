# Windows Runtime Hardening - PHASE 21

**Date**: 2026-05-23
**Phase**: STEP 5 - WINDOWS COMPATIBILITY HARDENING

## Overview

This document addresses Windows-specific Python ecosystem issues, compiled wheel availability, Visual C++ runtime requirements, and grpc wheel compatibility.

## Critical Windows Issues

### 1. GRPC Binary Wheel Compatibility

**Issue**: grpcio requires compiled C++ extensions (cygrpc)

**Symptoms**:
```
ImportError: cannot import name 'cygrpc' from 'grpc._cython'
```

**Root Cause**:
- grpcio binary wheels may not be available for Python 3.11 on Windows
- cygrpc is a Cython-compiled extension that requires compilation
- Visual C++ Build Tools may not be installed
- Compilation fails silently or partially

**Solution**:
1. Install Visual C++ Build Tools
2. Use pre-built wheels when available
3. Pin grpcio to version with known Windows compatibility
4. Install grpcio ecosystem first before other dependencies

---

### 2. Visual C++ Build Tools Requirements

**Required for**:
- grpcio (if binary wheel unavailable)
- pandas (if binary wheel unavailable)
- numpy (if binary wheel unavailable)
- scikit-learn (if binary wheel unavailable)
- torch (if binary wheel unavailable)

**Installation**:
1. Download from https://visualstudio.microsoft.com/downloads/
2. Select "Desktop development with C++"
3. Ensure MSVC v143 - VS 2022 C++ x64/x86 build tools is selected
4. Ensure Windows 10 SDK is selected
5. Install and restart

**Verification**:
```powershell
vswhere.exe -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64
```

---

### 3. Compiled Wheel Availability

**Packages requiring compilation**:
- grpcio (Cython extension)
- pandas (C extensions)
- numpy (C extensions)
- scikit-learn (C extensions)
- torch (C++ extensions)
- xgboost (C++ extensions)

**Windows Wheel Status**:
- Python 3.11: Most packages have pre-built wheels
- Python 3.12: Some packages may lack wheels
- Python 3.10+: Generally good wheel support

**Troubleshooting**:
```powershell
# Check if wheel is available
pip install --only-binary :all: <package>

# Force reinstallation with wheel
pip install --force-reinstall --no-cache-dir <package>
```

---

### 4. Path Length Issues

**Issue**: Windows has a 260 character path limit

**Symptoms**:
- Installation failures with "path too long" errors
- Import failures due to long paths
- Virtual environment creation failures

**Solution**:
1. Enable long path support in Windows 10/11:
   - Open Group Policy Editor
   - Navigate to Computer Configuration > Administrative Templates > System > Filesystem
   - Enable "Enable Win32 long paths"
   - Restart computer

2. Use shorter project paths:
   - Avoid deep directory structures
   - Use shorter folder names
   - Keep project close to drive root

---

### 5. Multiprocessing Behavior

**Issue**: uvicorn reload uses multiprocessing on Windows

**Symptoms**:
- Backend fails to start with multiprocessing errors
- Reload doesn't work correctly
- Child process spawn failures

**Solution**:
1. Use `--reload` flag (works on Windows)
2. Avoid `--workers` flag on Windows (use single process)
3. For production, use Docker instead of Windows native

**Startup Command**:
```powershell
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

---

### 6. PowerShell Execution Policy

**Issue**: PowerShell may block script execution

**Symptoms**:
```
cannot be loaded because running scripts is disabled
```

**Solution**:
```powershell
# For current session only
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

# For current user
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

### 7. GRPC Wheel Compatibility

**Pinned Versions**:
- grpcio==1.60.0 (known Windows compatibility)
- grpcio-tools==1.60.0
- grpcio-status==1.60.0
- protobuf==4.25.1

**Installation Order**:
1. Install grpcio ecosystem first
2. Validate cygrpc import
3. Then install other dependencies

**Validation**:
```powershell
python -c "import grpc; from grpc._cython import cygrpc; print('✓ GRPC OK')"
```

---

## Wheel Troubleshooting

### Check Wheel Availability

```powershell
# Check if wheel is available for your platform
pip download --only-binary :all: grpcio==1.60.0
```

### Force Wheel Installation

```powershell
# Install only from wheels, no compilation
pip install --only-binary :all: grpcio==1.60.0
```

### Fallback to Source Build

```powershell
# If wheel unavailable, compile from source
pip install grpcio==1.60.0 --no-binary grpcio
```

---

## PowerShell Execution Fixes

### Enable Script Execution

```powershell
# Check current policy
Get-ExecutionPolicy

# Set to RemoteSigned (recommended)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Run Scripts Without Execution Policy Change

```powershell
# Bypass execution policy (not recommended for security)
powershell -ExecutionPolicy Bypass -File script.ps1
```

---

## Windows Docker Notes

### Docker Desktop Requirements

1. Install Docker Desktop for Windows
2. Enable WSL 2 backend
3. Ensure sufficient disk space (10GB+)
4. Enable file sharing for project directory

### Dockerfile Compatibility

**Current Dockerfile**:
```dockerfile
FROM python:3.11-slim AS builder
# ... build steps ...

FROM python:3.11-slim AS runtime
# ... runtime steps ...
```

**Status**: Compatible with Windows Docker Desktop

**Notes**:
- Docker uses Linux containers, not Windows
- Binary wheels are for Linux, not Windows
- No Windows-specific issues in Docker
- Docker is recommended for development on Windows

---

## Recommended Windows Development Workflow

### Option 1: WSL 2 + Docker (Recommended)

1. Install WSL 2
2. Install Docker Desktop with WSL 2 backend
3. Develop in WSL 2 Linux environment
4. Use Docker for containerized development
5. Avoid Windows-specific issues entirely

### Option 2: Native Windows with Visual C++ Tools

1. Install Python 3.11
2. Install Visual C++ Build Tools
3. Use layered dependency installation
4. Install GRPC ecosystem first
5. Validate compiled packages

### Option 3: Native Windows without ML Dependencies

1. Install Python 3.11
2. Install only core dependencies (no ML)
3. Use Docker for ML features
4. Keep Windows environment minimal

---

## Recovery Procedures

### GRPC Installation Failure

```powershell
# Uninstall GRPC packages
pip uninstall grpcio grpcio-tools grpcio-status protobuf

# Purge cache
pip cache purge

# Install with pinned versions
pip install grpcio==1.60.0 grpcio-tools==1.60.0 grpcio-status==1.60.0 protobuf==4.25.1

# Validate
python scripts/validate_grpc.py
```

### Full Environment Recovery

```powershell
# Use the full recovery script
.\scripts\full_runtime_recovery.ps1
```

---

## Next Steps

1. ✅ STEP 1: Complete dependency forensics (COMPLETE)
2. ✅ STEP 2: GRPC ecosystem stabilization (COMPLETE)
3. ✅ STEP 3: Full venv reconstruction (COMPLETE)
4. ✅ STEP 4: Layered dependency strategy (COMPLETE)
5. ✅ STEP 5: Windows compatibility hardening (COMPLETE)
6. ⏭️ STEP 6: Optional ML degradation
7. ⏭️ STEP 7: Startup isolation hardening
8. ⏭️ STEP 8: Backend validation matrix
9. ⏭️ STEP 9: Docker + local parity
10. ⏭️ STEP 10: Final target validation

---

## Conclusion

Windows development requires special handling for compiled Python packages, particularly grpcio. The key issues are:
1. Visual C++ Build Tools required for compilation
2. GRPC binary wheel compatibility
3. Path length limitations
4. PowerShell execution policies
5. Multiprocessing behavior

The recommended approach is to use WSL 2 + Docker for development to avoid Windows-specific issues entirely. If native Windows development is required, ensure Visual C++ Build Tools are installed and use the layered dependency strategy with GRPC installed first.
