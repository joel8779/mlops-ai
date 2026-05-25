#!/bin/bash
# Local Environment Reconstruction Script - PHASE 20
# Bash version for Linux/Mac

set -e

echo "============================================================"
echo "Local Environment Reconstruction - PHASE 20"
echo "============================================================"

# Step 1: Validate Python version
echo ""
echo "Step 1: Validating Python version..."
PYTHON_VERSION=$(python --version 2>&1)
echo "  Current Python: $PYTHON_VERSION"

if [[ $PYTHON_VERSION =~ "Python 3.1[12]" ]]; then
    echo "  ✓ Python version is compatible"
else
    echo "  ✗ Python version is not compatible (requires 3.11 or 3.12)"
    echo ""
    echo "Please install Python 3.11 or 3.12 from https://www.python.org/downloads/"
    exit 1
fi

# Step 2: Recreate .venv
echo ""
echo "Step 2: Recreating virtual environment..."
if [ -d ".venv" ]; then
    echo "  Removing existing .venv..."
    rm -rf .venv
fi

echo "  Creating new .venv..."
python -m venv .venv
echo "  ✓ Virtual environment created"

# Step 3: Activate virtual environment
echo ""
echo "Step 3: Activating virtual environment..."
source .venv/bin/activate
echo "  ✓ Virtual environment activated"

# Step 4: Upgrade pip
echo ""
echo "Step 4: Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel
echo "  ✓ pip upgraded"

# Step 5: Install core dependencies
echo ""
echo "Step 5: Installing core dependencies..."
pip install -r apps/api/requirements-core.txt -c apps/api/constraints.txt
echo "  ✓ Core dependencies installed"

# Step 6: Validate Python runtime
echo ""
echo "Step 6: Validating Python runtime..."
python scripts/verify_python_runtime.py

# Step 7: Validate imports
echo ""
echo "Step 7: Validating imports..."
cd apps/api
python -c "import app.main"
echo "  ✓ Imports validated"
cd ../..

# Step 8: Validate ML stack (optional)
echo ""
echo "Step 8: Validating ML stack (optional)..."
python scripts/validate_ml_stack.py || {
    echo "  ⚠ ML stack validation failed (ML features will be unavailable)"
    echo "  To install ML dependencies: pip install -r apps/api/requirements-ml.txt"
}

echo ""
echo "============================================================"
echo "✓ Local environment reconstruction complete"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Start infrastructure: docker compose up -d postgres redis qdrant minio mlflow"
echo "2. Run migrations: cd apps/api && alembic upgrade head"
echo "3. Start backend: cd apps/api && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload"
