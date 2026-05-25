import asyncio
from uuid import UUID

from app.db.session import AsyncSessionLocal
from app.models.domain import JobDescription
from app.services.job_intelligence_service import JobIntelligenceService
from app.workers.celery_app import celery_app


@celery_app.task(name="job_description.index", autoretry_for=(Exception,), retry_backoff=True)
def index_job_description_task(job_description_id: str) -> None:
    asyncio.run(_index_job(UUID(job_description_id)))


async def _index_job(job_description_id: UUID) -> None:
    async with AsyncSessionLocal() as db:
        try:
            await JobIntelligenceService(db).index_job(job_description_id)
        except Exception as exc:
            await db.rollback()
            job = await db.get(JobDescription, job_description_id)
            if job is not None:
                job.metadata_json = {
                    **(job.metadata_json or {}),
                    "indexing": {
                        "status": "failed",
                        "error_code": "job_embedding_or_qdrant_failed",
                        "message": "Job embedding or Qdrant indexing failed.",
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                    },
                }
                await db.commit()
            raise
