from __future__ import annotations

import app.workers.job_tasks  # noqa: F401
import app.workers.resume_tasks  # noqa: F401
from app.workers.celery_app import celery_app


REQUIRED_TASKS = {"resume.parse"}


def main() -> int:
    task_names = set(celery_app.tasks.keys())
    missing = sorted(REQUIRED_TASKS - task_names)
    if missing:
        print("Missing Celery tasks:")
        for task in missing:
            print(f"  - {task}")
        return 1
    if not celery_app.conf.task_acks_late:
        print("Celery task_acks_late must be enabled")
        return 1
    print(f"Celery worker registration: OK ({len(task_names)} tasks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
