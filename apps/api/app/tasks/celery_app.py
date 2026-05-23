from celery import Celery

from app.core.config import settings
from app.logging import configure_logging
from app.observability.tracing import instrument_celery

configure_logging()
instrument_celery()

celery_app = Celery(
    "resume_intelligence",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.resume_tasks"],
)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    task_time_limit=600,
    task_soft_time_limit=540,
    result_expires=3600,
)
