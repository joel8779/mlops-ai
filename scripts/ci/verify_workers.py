from __future__ import annotations

import sys

try:
    import app.workers.job_tasks  # noqa: F401
    import app.workers.resume_tasks  # noqa: F401
    from app.workers.celery_app import celery_app
except ImportError as exc:
    print(f"ERROR: Failed to import worker modules: {exc}")
    sys.exit(1)


REQUIRED_TASKS = {"resume.parse"}


def main() -> int:
    try:
        task_names = set(celery_app.tasks.keys())
    except Exception as exc:
        print(f"ERROR: Failed to get Celery tasks: {exc}")
        return 1
    
    missing = sorted(REQUIRED_TASKS - task_names)
    if missing:
        print("ERROR: Missing Celery tasks:")
        for task in missing:
            print(f"  - {task}")
        return 1
    
    if not celery_app.conf.task_acks_late:
        print("ERROR: Celery task_acks_late must be enabled")
        return 1
    
    print(f"Celery worker registration: OK ({len(task_names)} tasks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
