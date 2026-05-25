#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

resolve_python() {
  for candidate in python3.11 python3.12 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] < (3, 13) else 1)'; then
      echo "$candidate"
      return 0
    fi
  done
  echo "Python 3.11 or 3.12 is required. Install Python 3.11/3.12, then rerun scripts/bootstrap.sh." >&2
  return 1
}

if [ ! -f ".env" ]; then
  cp ".env.example" ".env"
  echo "Created .env from .env.example. Update secrets before production use."
fi

PROJECT_PYTHON="$(resolve_python)"
"$PROJECT_PYTHON" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r apps/api/requirements-dev.txt -c apps/api/constraints.txt

if [ -f "apps/web/package.json" ]; then
  (cd apps/web && npm install)
fi

python scripts/verify_env.py
echo "Bootstrap complete. Activate with: source .venv/bin/activate"
