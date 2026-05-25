# Interpreter Contamination Analysis - PHASE 21.3

**Date**: 2026-05-23
**Phase**: STEP 1 - FULL INTERPRETER FORENSICS

## Critical Findings

### Python Installation Audit

**System Python**:
- Version: Python 3.14.5
- Location: WindowsApps (Microsoft Store)
- Status: Default system interpreter

**Available Python Versions** (via py launcher):
- Python 3.14.5 (default, marked with *)
- Python 3.13 (Microsoft Store)
- Python 3.11.9 (available via py launcher)

### PATH Configuration

**where python**: No output
- Python not in system PATH
- Only accessible via `python` alias (WindowsApps)

**where pip**: No output
- pip not in system PATH
- Only accessible via `python -m pip`

### Venv State

**Current venv**:
- Created with: System Python 3.14.5
- Python version: Python 3.14.5
- Status: CONTAMINATED - wrong Python version

### Package Installation Evidence

**Observed contamination**:
- Packages installing to: `C:\Users\Lenovo\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\`
- Wheels downloaded: `cp313-cp313-win_amd64.whl`
- User-site fallback: "Defaulting to user installation because normal site-packages is not writeable"

### Root Cause Analysis

**Primary Issue**: Venv created with wrong Python version

1. User ran: `python -m venv .venv`
2. `python` resolved to: System Python 3.14.5 (WindowsApps)
3. Venv inherited: Python 3.14.5
4. Project requires: Python 3.11 or 3.12 (>=3.11,<3.13)
5. Result: ABI mismatch, package incompatibility

**Secondary Issue**: User-site package contamination

1. Venv not properly activated or isolated
2. pip falling back to user-site installation
3. Packages installing to Python 3.13 user-site
4. Mixed ABI state (3.13 packages, 3.14 venv)

### Dependency Conflicts

**Project constraints** (`apps/api/pyproject.toml`):
- Python >=3.11,<3.13

**Current environment**:
- Python 3.14.5 (INCOMPATIBLE)
- Python 3.13 packages (INCOMPATIBLE)

**Result**:
- Package wheels not available for Python 3.14
- ABI mismatches between Python 3.14 and package wheels
- GRPC ecosystem installation failures
- ML stack compilation failures

## Required Actions

### STEP 2: Complete Environment Purge

1. Deactivate venv (if active)
2. Remove .venv completely
3. Clear pip cache
4. Identify and document PATH contamination

### STEP 3: Hard-Lock Python 3.11

Use py launcher to create venv with correct Python version:
```powershell
py -3.11 -m venv .venv
```

Validate:
```powershell
.\.venv\Scripts\python --version
# Must return: Python 3.11.9
```

### STEP 4: Force Pip Isolation

Always use:
```powershell
python -m pip install ...
```

NEVER use:
```powershell
pip install ...
```

### STEP 5: User-Site Package Isolation

Prevent user-site fallback by ensuring:
- Venv is properly activated
- Permissions are correct
- PYTHONPATH is not set
- PYTHONHOME is not set

### STEP 6: Clean Reinstall

After interpreter isolation:
```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install --only-binary=:all: --no-cache-dir -r apps/api/requirements-core.txt
```

## Validation Requirements

After recovery, validate:
- `python --version` returns Python 3.11.9
- `where python` resolves to `.venv\Scripts\python.exe`
- `where pip` resolves to `.venv\Scripts\pip.exe`
- No Python 3.13 or 3.14 artifacts in venv
- No user-site package fallback
- All packages install to venv site-packages

## Conclusion

The environment is contaminated by:
1. Wrong Python version in venv (3.14 instead of 3.11)
2. User-site package fallback to Python 3.13
3. Mixed ABI state causing installation failures

Recovery requires:
1. Complete venv purge
2. Recreate venv with Python 3.11 via py launcher
3. Force pip isolation using `python -m pip`
4. Validate interpreter isolation
5. Clean reinstall with correct Python version
