from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
EXAMPLE_FILE = ROOT / ".env.example"

REQUIRED = {
    "APP_NAME",
    "ENVIRONMENT",
    "DATABASE_URL",
    "SYNC_DATABASE_URL",
    "REDIS_URL",
    "CELERY_BROKER_URL",
    "CELERY_RESULT_BACKEND",
    "QDRANT_URL",
    "S3_BUCKET",
    "JWT_SECRET_KEY",
    "GEMINI_API_KEY",
    "MLFLOW_TRACKING_URI",
    "NEO4J_URI",
}

SECRET_WARNINGS = {
    "JWT_SECRET_KEY": {"change-me", "change-me-use-a-32-byte-random-secret"},
    "GEMINI_API_KEY": {"replace-with-your-google-ai-studio-key", "your-gemini-api-key-here"},
    "STRIPE_SECRET_KEY": {"sk_test_replace_me"},
}


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def main() -> int:
    values = {**parse_env(EXAMPLE_FILE), **parse_env(ENV_FILE), **os.environ}
    missing = sorted(key for key in REQUIRED if not values.get(key))
    warnings = [
        f"{key} still uses an example value"
        for key, unsafe_values in SECRET_WARNINGS.items()
        if values.get(key) in unsafe_values
    ]

    if missing:
        print("Missing required environment variables:")
        for key in missing:
            print(f"  - {key}")
        return 1

    print("Environment contract: OK")
    if warnings:
        print("Security warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
