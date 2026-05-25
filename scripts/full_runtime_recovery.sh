#!/bin/bash
# Authoritative Runtime Recovery Script - PHASE 28
# Canonical installation process with layered requirements architecture

set -e

echo "============================================================"
echo "Authoritative Runtime Recovery - PHASE 28"
echo "============================================================"

# Step 1: Validate Python version
echo ""
echo "Step 1: Validating Python version..."
PYTHON_VERSION=$(python --version 2>&1)
echo "  Current Python: $PYTHON_VERSION"

if [[ $PYTHON_VERSION =~ "Python 3.11" ]]; then
    echo "  ✓ Python version is compatible"
else
    echo "  ✗ Python version is not compatible (requires 3.11)"
    echo ""
    echo "Please install Python 3.11 from https://www.python.org/downloads/"
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

# Step 7: Install Layer 1 - Core Runtime
echo ""
echo "Step 7: Installing Layer 1 - Core Runtime..."
python -m pip install --no-cache-dir -r apps/api/requirements-core.txt -c apps/api/constraints.txt
echo "  ✓ Core runtime installed"

# Step 8: Install Layer 2 - Observability
echo ""
echo "Step 8: Installing Layer 2 - Observability..."
python -m pip install --no-cache-dir -r apps/api/requirements-observability.txt -c apps/api/constraints.txt
echo "  ✓ Observability installed"

# Step 9: Install Layer 3 - AI (Google Gen AI SDK)
echo ""
echo "Step 9: Installing Layer 3 - AI (Google Gen AI SDK)..."
python -m pip install --no-cache-dir -r apps/api/requirements-ai.txt -c apps/api/constraints.txt
echo "  ✓ AI SDK installed"

# Step 10: Install Layer 4 - Embeddings (CPU-only)
echo ""
echo "Step 10: Installing Layer 4 - Embeddings (CPU-only)..."
python -m pip install --no-cache-dir -r apps/api/requirements-embeddings.txt -c apps/api/constraints.txt
echo "  ✓ Embeddings installed"

# Step 11: Install Layer 5 - Worker
echo ""
echo "Step 11: Installing Layer 5 - Worker..."
python -m pip install --no-cache-dir -r apps/api/requirements-worker.txt -c apps/api/constraints.txt
echo "  ✓ Worker installed"

# Step 12: Install Layer 6 - OCR
echo ""
echo "Step 12: Installing Layer 6 - OCR..."
python -m pip install --no-cache-dir -r apps/api/requirements-ocr.txt -c apps/api/constraints.txt
echo "  ✓ OCR installed"

# Step 13: Validate dependency guardrails
echo ""
echo "Step 13: Validating dependency guardrails..."
cd apps/api
python -c "from app.core.dependency_guard import assert_core_dependency_runtime; assert_core_dependency_runtime()"
echo "  ✓ Dependency guardrails validated"
cd ../..

# Step 14: Validate imports
echo ""
echo "Step 14: Validating imports..."
cd apps/api
python -c "import app.main"
echo "  ✓ Imports validated"
cd ../..

# Step 15: Validate FastAPI startup
echo ""
echo "Step 15: Validating FastAPI startup..."
cd apps/api
python -c "from app.main import create_app; app = create_app(); print('✓ FastAPI app created successfully')"
echo "  ✓ FastAPI startup validated"
cd ../..

# Step 16: Run pip check
echo ""
echo "Step 16: Running pip check..."
python -m pip check
echo "  ✓ No dependency conflicts"

echo ""
echo "============================================================"
echo "✓ Authoritative runtime recovery complete"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Start infrastructure: docker compose up -d postgres redis qdrant minio"
echo "2. Run migrations: cd apps/api && alembic upgrade head"
echo "3. Start backend: cd apps/api && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Optional: Install ML/training layer (NOT for runtime SaaS)"
echo "  pip install -r apps/api/requirements-ml.txt"
