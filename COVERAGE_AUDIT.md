# Coverage Configuration Audit

This document details the audit of all coverage-related configurations in the repository to resolve the `coverage.exceptions.DataError` ("Can't combine statement coverage data with branch data") error.

## 1. Audit Findings

- **pyproject.toml** (`apps/api/pyproject.toml`):
  - Contains `branch = true` under `[tool.coverage.run]`.
- **.coveragerc**: Does not exist in the repository.
- **pytest.ini**: Does not exist in the repository.
- **tox.ini**: Does not exist in the repository.
- **GitHub Workflows**:
  - `backend-ci.yml` runs:
    ```bash
    python -m pytest -q --cov=app --cov-report=xml --cov-report=term-missing
    ```
    This does not explicitly pass `--cov-branch` but automatically reads `pyproject.toml` which had `branch = true` enabled.
  - No workflow files run `coverage combine` or configure parallel coverage explicitly.

## 2. Root Cause of Merge Failure

The `DataError` occurs because of inconsistency in branch coverage collection, or because stale coverage files collected with different configurations (e.g., statement-only locally vs. branch-enabled in CI) were being combined or reused, causing `coverage` to crash when attempting to parse or merge the files.

## 3. Unification Choice

We have chosen **Option A: Statement Coverage Only** for maximum simplicity and stability across Python versions.

To enforce this consistently:
- Set `branch = false` in `apps/api/pyproject.toml`.
- Ensure no `--cov-branch` or `branch=True` is used.
- Add a step to clean any stale `.coverage`, `coverage.xml`, or `.pytest_cache` files before running tests in CI.
