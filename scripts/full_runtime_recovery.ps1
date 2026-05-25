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
    Write-Host "  OK Python version is compatible"
} else {
    Write-Host "  FAIL Python version is not compatible (requires 3.11 or 3.12)"
    Write-Host "`nPlease install Python 3.11 or 3.12 from https://www.python.org/downloads/"
    exit 1
}

# Step 2: Remove corrupted venv
Write-Host "`nStep 2: Removing corrupted virtual environment..."
if (Test-Path ".venv") {
    Write-Host "  Removing existing .venv..."
    Remove-Item -Recurse -Force ".venv"
    Write-Host "  OK Virtual environment removed"
} else {
    Write-Host "  OK No existing .venv found"
}

# Step 3: Purge pip cache
Write-Host "`nStep 3: Purging pip cache..."
pip cache purge
Write-Host "  OK Pip cache purged"

# Step 4: Recreate venv
Write-Host "`nStep 4: Recreating virtual environment..."
python -m venv .venv
Write-Host "  OK Virtual environment created"

# Step 5: Activate virtual environment
Write-Host "`nStep 5: Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1
Write-Host "  OK Virtual environment activated"

# Step 6: Upgrade pip/setuptools/wheel
Write-Host "`nStep 6: Upgrading pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel
Write-Host "  OK pip, setuptools, wheel upgraded"

# Step 7: Install core dependencies (without GRPC/qdrant for now)
Write-Host "`nStep 7: Installing core dependencies (without GRPC/qdrant)..."
pip install --no-cache-dir -r apps/api/requirements-core.txt -c apps/api/constraints.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Core dependencies installed"
} else {
    Write-Host "  FAIL Core dependencies installation failed"
    exit 1
}

Write-Host "`n" + "=" * 60
Write-Host "Full runtime recovery complete"
Write-Host "=" * 60
Write-Host "`nNOTE: GRPC/qdrant not installed due to missing Visual C++ Build Tools"
Write-Host "Core API will work without vector search capabilities"
Write-Host "`nTo install GRPC/qdrant:"
Write-Host "1. Install Visual C++ Build Tools from https://visualstudio.microsoft.com/downloads/"
Write-Host "2. Select 'Desktop development with C++'"
Write-Host "3. Run: pip install grpcio==1.76.0 grpcio-tools==1.76.0 grpcio-status==1.76.0 protobuf==6.31.1 qdrant-client==1.12.1"
Write-Host "`nNext steps:"
Write-Host "1. Validate runtime: python scripts\runtime_validation_matrix.py"
Write-Host "2. Start infrastructure: docker compose up -d postgres redis minio mlflow"
Write-Host "3. Run migrations: cd apps/api && alembic upgrade head"
Write-Host "4. Start backend: cd apps/api && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload"
Write-Host "`nOptional: Install ML dependencies"
Write-Host "  pip install -r apps/api/requirements-ml.txt"
