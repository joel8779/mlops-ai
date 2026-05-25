from celery import Celery

from app.core.config import settings
from app.core.dependency_guard import validate_worker_dependency_layer
from app.logging import configure_logging
from app.observability.tracing import instrument_celery

configure_logging()
instrument_celery()
validate_worker_dependency_layer()

celery_app = Celery(
    "resume_intelligence",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.workers.diagnostics",
        "app.workers.resume_tasks",
        "app.workers.job_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    task_time_limit=600,
    task_soft_time_limit=540,
    result_expires=3600,
    broker_transport_options={
        "socket_connect_timeout": 5,
        "socket_timeout": 10,
        "retry_on_timeout": True,
    },
    result_backend_transport_options={
        "socket_connect_timeout": 5,
        "socket_timeout": 10,
        "retry_on_timeout": True,
    },
)
