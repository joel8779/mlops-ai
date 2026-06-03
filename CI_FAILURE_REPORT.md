# CI Failure Report

## 1. backend-ci Failures (Python 3.11 & 3.12)

- **Failing Command**: 
  ```bash
  python scripts/ci/verify_runtime.py
  ```
- **First Real Error**:
  ```
  ERROR: Failed to import app.main: No module named 'app'
  This usually indicates missing dependencies or import errors.
  ```
- **Root Cause**: 
  The GitHub Actions runner executes verification scripts from the repository root directory. Since the FastAPI application code is located under `apps/api/`, the `app` package is not in the default Python path. Because `PYTHONPATH` is not set in the environment of the workflow, Python fails to import `app.main`.
- **Cascading Failures**: 
  The subsequent verification steps (`verify_routes.py`, `verify_observability.py`, `verify_workers.py`) and pytest unit tests also failed or would fail due to the same missing Python path configuration.

---

## 2. docker-ci Failure

- **Failing Command**:
  ```bash
  docker run --rm resume-intelligence-api:${{ github.sha }} python -m compileall /app/app
  ```
- **First Real Error**:
  ```
  *** PermissionError: [Errno 13] Permission denied: '/app/app/benchmarking/__pycache__/metrics_calculator.cpython-311.pyc...'
  ```
- **Root Cause**: 
  The Dockerfile switches to a non-root user `appuser` (using `USER appuser`) at the end of the runtime stage. In the build, files are copied using `COPY app app` without setting `--chown=appuser:appuser`, making them owned by `root`. When the smoke test runs `python -m compileall /app/app`, it runs as the default container user `appuser`. Since `appuser` doesn't have write permissions to `/app/app/`, creating the compiled `__pycache__` files fails with a `PermissionError`.
