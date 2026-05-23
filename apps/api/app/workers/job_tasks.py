import asyncio
from uuid import UUID

from app.db.session import AsyncSessionLocal
from app.services.job_intelligence_service import JobIntelligenceService
from app.workers.celery_app import celery_app


@celery_app.task(name="job_description.index", autoretry_for=(Exception,), retry_backoff=True)
def index_job_description_task(job_description_id: str) -> None:
    asyncio.run(_index_job(UUID(job_description_id)))


async def _index_job(job_description_id: UUID) -> None:
    async with AsyncSessionLocal() as db:
        await JobIntelligenceService(db).index_job(job_description_id)
