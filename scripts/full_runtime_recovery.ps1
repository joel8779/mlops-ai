# Full Runtime Recovery Script - PHASE 21
# PowerShell version for Windows

Write-Host "=" * 60
Write-Host "Full Runtime Recovery - PHASE 21"
Write-Host "=" * 60

# Step 1: Validate Python version
Write-Host "`nStep 1: Validating Python version..."
$pythonVersion = python --version 2>&1
Write-Host "  Current Python: $pythonVersion"

if ($pythonVersion -match "3\.1[12]") {
    Write-Host "  ✓ Python version is compatible"
} else {
    Write-Host "  ✗ Python version is not compatible (requires 3.11 or 3.12)"
    Write-Host "`nPlease install Python 3.11 or 3.12 from https://www.python.org/downloads/"
    exit 1
}

# Step 2: Remove corrupted venv
Write-Host "`nStep 2: Removing corrupted virtual environment..."
if (Test-Path ".venv") {
    Write-Host "  Removing existing .venv..."
    Remove-Item -Recurse -Force ".venv"
    Write-Host "  ✓ Virtual environment removed"
} else {
    Write-Host "  ✓ No existing .venv found"
}

# Step 3: Purge pip cache
Write-Host "`nStep 3: Purging pip cache..."
pip cache purge
Write-Host "  ✓ Pip cache purged"

# Step 4: Recreate venv
Write-Host "`nStep 4: Recreating virtual environment..."
python -m venv .venv
Write-Host "  ✓ Virtual environment created"

# Step 5: Activate virtual environment
Write-Host "`nStep 5: Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1
Write-Host "  ✓ Virtual environment activated"

# Step 6: Upgrade pip/setuptools/wheel
Write-Host "`nStep 6: Upgrading pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel
Write-Host "  ✓ pip, setuptools, wheel upgraded"

# Step 7: Install GRPC ecosystem first (for Windows compatibility)
Write-Host "`nStep 7: Installing GRPC ecosystem..."
pip install --no-cache-dir grpcio==1.60.0 grpcio-tools==1.60.0 grpcio-status==1.60.0 protobuf==4.25.1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ GRPC ecosystem installed"
} else {
    Write-Host "  ✗ GRPC ecosystem installation failed"
    Write-Host "  This may require Visual C++ Build Tools on Windows"
    Write-Host "  Install from: https://visualstudio.microsoft.com/downloads/"
    exit 1
}

# Step 8: Validate GRPC installation
Write-Host "`nStep 8: Validating GRPC installation..."
python scripts\validate_grpc.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ GRPC validation failed"
    exit 1
}

# Step 9: Install core dependencies
Write-Host "`nStep 9: Installing core dependencies..."
pip install --no-cache-dir -r apps/api/requirements-core.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Core dependencies installed"
} else {
    Write-Host "  ✗ Core dependencies installation failed"
    exit 1
}

# Step 10: Validate compiled packages
Write-Host "`nStep 10: Validating compiled packages..."
python -c "import grpc; from grpc._cython import cygrpc; print('✓ GRPC cygrpc validated')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Compiled package validation failed"
    exit 1
}

# Step 11: Validate imports
Write-Host "`nStep 11: Validating imports..."
cd apps/api
python -c "import app.main"
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Imports validated"
} else {
    Write-Host "  ✗ Import validation failed"
    cd ../..
    exit 1
}
cd ../..

# Step 12: Validate FastAPI startup
Write-Host "`nStep 12: Validating FastAPI startup..."
cd apps/api
python -c "from app.main import create_app; app = create_app(); print('✓ FastAPI app created successfully')"
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ FastAPI startup validated"
} else {
    Write-Host "  ✗ FastAPI startup validation failed"
    cd ../..
    exit 1
}
cd ../..

Write-Host "`n" + "=" * 60
Write-Host "✓ Full runtime recovery complete"
Write-Host "=" * 60
Write-Host "`nNext steps:"
Write-Host "1. Start infrastructure: docker compose up -d postgres redis qdrant minio mlflow"
Write-Host "2. Run migrations: cd apps/api && alembic upgrade head"
Write-Host "3. Start backend: cd apps/api && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload"
Write-Host "`nOptional: Install ML dependencies"
Write-Host "  pip install -r apps/api/requirements-ml.txt"
