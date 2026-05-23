#!/bin/bash
# Full Runtime Recovery Script - PHASE 21
# Bash version for Linux/Mac

set -e

echo "============================================================"
echo "Full Runtime Recovery - PHASE 21"
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

# Step 2: Remove corrupted venv
echo ""
echo "Step 2: Removing corrupted virtual environment..."
if [ -d ".venv" ]; then
    echo "  Removing existing .venv..."
    rm -rf .venv
    echo "  ✓ Virtual environment removed"
else
    echo "  ✓ No existing .venv found"
fi

# Step 3: Purge pip cache
echo ""
echo "Step 3: Purging pip cache..."
pip cache purge
echo "  ✓ Pip cache purged"

# Step 4: Recreate venv
echo ""
echo "Step 4: Recreating virtual environment..."
python -m venv .venv
echo "  ✓ Virtual environment created"

# Step 5: Activate virtual environment
echo ""
echo "Step 5: Activating virtual environment..."
source .venv/bin/activate
echo "  ✓ Virtual environment activated"

# Step 6: Upgrade pip/setuptools/wheel
echo ""
echo "Step 6: Upgrading pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel
echo "  ✓ pip, setuptools, wheel upgraded"

# Step 7: Install GRPC ecosystem first (for Windows compatibility)
echo ""
echo "Step 7: Installing GRPC ecosystem..."
pip install --no-cache-dir grpcio==1.60.0 grpcio-tools==1.60.0 grpcio-status==1.60.0 protobuf==4.25.1
echo "  ✓ GRPC ecosystem installed"

# Step 8: Validate GRPC installation
echo ""
echo "Step 8: Validating GRPC installation..."
python scripts/validate_grpc.py

# Step 9: Install core dependencies
echo ""
echo "Step 9: Installing core dependencies..."
pip install --no-cache-dir -r apps/api/requirements-core.txt
echo "  ✓ Core dependencies installed"

# Step 10: Validate compiled packages
echo ""
echo "Step 10: Validating compiled packages..."
python -c "import grpc; from grpc._cython import cygrpc; print('✓ GRPC cygrpc validated')"

# Step 11: Validate imports
echo ""
echo "Step 11: Validating imports..."
cd apps/api
python -c "import app.main"
echo "  ✓ Imports validated"
cd ../..

# Step 12: Validate FastAPI startup
echo ""
echo "Step 12: Validating FastAPI startup..."
cd apps/api
python -c "from app.main import create_app; app = create_app(); print('✓ FastAPI app created successfully')"
echo "  ✓ FastAPI startup validated"
cd ../..

echo ""
echo "============================================================"
echo "✓ Full runtime recovery complete"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Start infrastructure: docker compose up -d postgres redis qdrant minio mlflow"
echo "2. Run migrations: cd apps/api && alembic upgrade head"
echo "3. Start backend: cd apps/api && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Optional: Install ML dependencies"
echo "  pip install -r apps/api/requirements-ml.txt"
