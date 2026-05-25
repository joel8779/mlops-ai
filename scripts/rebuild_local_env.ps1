# Local Environment Reconstruction Script - PHASE 20
# PowerShell version for Windows

Write-Host "=" * 60
Write-Host "Local Environment Reconstruction - PHASE 20"
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

# Step 2: Recreate .venv
Write-Host "`nStep 2: Recreating virtual environment..."
if (Test-Path ".venv") {
    Write-Host "  Removing existing .venv..."
    Remove-Item -Recurse -Force ".venv"
}

Write-Host "  Creating new .venv..."
python -m venv .venv
Write-Host "  ✓ Virtual environment created"

# Step 3: Activate virtual environment
Write-Host "`nStep 3: Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1
Write-Host "  ✓ Virtual environment activated"

# Step 4: Upgrade pip
Write-Host "`nStep 4: Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel
Write-Host "  ✓ pip upgraded"

# Step 5: Install core dependencies
Write-Host "`nStep 5: Installing core dependencies..."
pip install -r apps/api/requirements-core.txt -c apps/api/constraints.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Core dependencies installed"
} else {
    Write-Host "  ✗ Core dependencies installation failed"
    exit 1
}

# Step 6: Validate Python runtime
Write-Host "`nStep 6: Validating Python runtime..."
python scripts/verify_python_runtime.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Python runtime validation failed"
    exit 1
}

# Step 7: Validate imports
Write-Host "`nStep 7: Validating imports..."
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

# Step 8: Validate ML stack (optional)
Write-Host "`nStep 8: Validating ML stack (optional)..."
python scripts/validate_ml_stack.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ⚠ ML stack validation failed (ML features will be unavailable)"
    Write-Host "  To install ML dependencies: pip install -r apps/api/requirements-ml.txt"
}

Write-Host "`n" + "=" * 60
Write-Host "✓ Local environment reconstruction complete"
Write-Host "=" * 60
Write-Host "`nNext steps:"
Write-Host "1. Start infrastructure: docker compose up -d postgres redis qdrant minio mlflow"
Write-Host "2. Run migrations: cd apps/api && alembic upgrade head"
Write-Host "3. Start backend: cd apps/api && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload"
