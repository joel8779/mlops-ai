"""Validate Celery/Redis worker runtime without starting the API."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from importlib import metadata
from pathlib import Path
from typing import Any

from packaging import version


ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "apps" / "api"
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
VALIDATION_QUEUE = "phase24_worker_validation"


def configure_environment() -> None:
    os.environ["DEBUG"] = "false"
    os.environ["OTEL_ENABLED"] = "false"
    os.environ["EMBEDDING_LOCAL_FILES_ONLY"] = "true"
    os.environ["PREFECT_HOME"] = str(ROOT / "runtime" / "prefect-home")
    os.environ["PREFECT_API_URL"] = ""
    Path(os.environ["PREFECT_HOME"]).mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(API_DIR))


def assert_dependency(name: str, requirement: str) -> str:
    installed = metadata.version(name)
    parsed = version.parse(installed)
    for part in requirement.split(","):
        part = part.strip()
        if part.startswith(">=") and parsed < version.parse(part[2:]):
            raise RuntimeError(f"{name}=={installed} violates {requirement}")
        if part.startswith("<") and parsed >= version.parse(part[1:]):
            raise RuntimeError(f"{name}=={installed} violates {requirement}")
    return installed


def validate_dependencies() -> dict[str, str | None]:
    versions: dict[str, str | None] = {
        "celery": assert_dependency("celery", ">=5.4.0,<5.5.0"),
        "redis": assert_dependency("redis", ">=5.2.1,<6.0.0"),
        "kombu": assert_dependency("kombu", ">=5.3.4,<6.0.0"),
        "billiard": assert_dependency("billiard", ">=4.2.0,<5.0.0"),
        "vine": assert_dependency("vine", ">=5.1.0,<6.0.0"),
        "protobuf": assert_dependency("protobuf", ">=6.31.1,<7.0.0"),
        "grpcio": assert_dependency("grpcio", ">=1.76.0,<2.0.0"),
    }
    try:
        versions["prefect"] = metadata.version("prefect")
    except metadata.PackageNotFoundError:
        versions["prefect"] = None
    return versions


def validate_redis() -> dict[str, Any]:
    import redis
    from app.core.config import settings

    client = redis.Redis.from_url(settings.celery_broker_url, socket_connect_timeout=5, socket_timeout=5)
    pong = client.ping()
    client.close()
    return {"broker_url": settings.celery_broker_url, "ping": bool(pong)}


def validate_registration() -> dict[str, Any]:
    import app.workers.diagnostics  # noqa: F401
    import app.workers.job_tasks  # noqa: F401
    import app.workers.resume_tasks  # noqa: F401
    from app.workers.celery_app import celery_app

    expected = {
        "worker.ping",
        "worker.expected_failure",
        "worker.db_probe",
        "worker.embedding_qdrant_probe",
        "resume.parse",
        "job_description.index",
    }
    registered = set(celery_app.tasks.keys())
    missing = sorted(expected - registered)
    if missing:
        raise RuntimeError(f"Missing Celery tasks: {missing}")
    return {
        "task_count": len(registered),
        "expected_tasks": sorted(expected),
        "task_acks_late": bool(celery_app.conf.task_acks_late),
        "prefetch_multiplier": celery_app.conf.worker_prefetch_multiplier,
    }


def start_worker() -> subprocess.Popen:
    env = os.environ.copy()
    env.setdefault("DEBUG", "false")
    env.setdefault("OTEL_ENABLED", "false")
    env.setdefault("EMBEDDING_LOCAL_FILES_ONLY", "true")
    command = [
        str(PYTHON),
        "-m",
        "celery",
        "-A",
        "app.workers.celery_app.celery_app",
        "worker",
        "--loglevel=INFO",
        "--pool=solo",
        "--concurrency=1",
        "-Q",
        VALIDATION_QUEUE,
        "--hostname=phase24-worker@%h",
    ]
    return subprocess.Popen(
        command,
        cwd=str(API_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def stop_worker(process: subprocess.Popen) -> list[str]:
    output: list[str] = []
    if process.poll() is None:
        if os.name == "nt":
            process.send_signal(signal.CTRL_BREAK_EVENT) if False else process.terminate()
        else:
            process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
    if process.stdout:
        try:
            output = process.stdout.read().splitlines()[-80:]
        except Exception:
            output = []
    return output


def wait_for_worker(timeout_seconds: int = 45) -> None:
    from app.workers.celery_app import celery_app

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        replies = celery_app.control.ping(timeout=1.0)
        if replies:
            return
        time.sleep(1)
    raise TimeoutError("Celery worker did not respond to ping")


def dispatch_task(name: str, *, args: list[Any] | None = None, timeout_seconds: int = 60) -> dict[str, Any]:
    from app.workers.celery_app import celery_app

    result = celery_app.send_task(name, args=args or [], queue=VALIDATION_QUEUE)
    value = result.get(timeout=timeout_seconds, propagate=False)
    return {
        "task": name,
        "id": result.id,
        "state": result.state,
        "successful": result.successful(),
        "result": value if isinstance(value, (dict, list, str, int, float, bool, type(None))) else str(value),
    }


def validate_prefect() -> dict[str, Any]:
    from app.pipelines import prefect_flows

    results = {
        "available": prefect_flows.PREFECT_AVAILABLE,
        "resume_ingestion": prefect_flows.run_resume_ingestion_local("phase24"),
        "embedding_refresh": prefect_flows.run_embedding_refresh_local("active-candidates"),
        "nightly_ranking": prefect_flows.run_nightly_candidate_ranking_local(),
    }
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate worker and pipeline runtime.")
    parser.add_argument("--dependency-only", action="store_true", help="Only validate dependencies, Redis, and task registration.")
    parser.add_argument("--start-worker", action="store_true", help="Start a local solo Celery worker for task execution.")
    parser.add_argument("--with-db", action="store_true", help="Run worker-side database probe task.")
    parser.add_argument("--with-embeddings", action="store_true", help="Run worker-side embedding/Qdrant probe task.")
    parser.add_argument("--with-prefect", action="store_true", help="Run local Prefect flow validation.")
    args = parser.parse_args()

    configure_environment()
    result: dict[str, Any] = {
        "dependencies": validate_dependencies(),
        "redis": validate_redis(),
        "registration": validate_registration(),
    }

    if args.with_prefect:
        result["prefect"] = validate_prefect()

    worker: subprocess.Popen | None = None
    try:
        if args.start_worker:
            worker = start_worker()
            wait_for_worker()
            result["worker_ping"] = dispatch_task("worker.ping", args=[{"phase": "24.3"}])
            result["expected_failure"] = dispatch_task("worker.expected_failure", timeout_seconds=30)
            if args.with_db:
                result["db_probe"] = dispatch_task("worker.db_probe")
            if args.with_embeddings:
                result["embedding_qdrant_probe"] = dispatch_task("worker.embedding_qdrant_probe", timeout_seconds=120)
    finally:
        if worker is not None:
            result["worker_log_tail"] = stop_worker(worker)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
