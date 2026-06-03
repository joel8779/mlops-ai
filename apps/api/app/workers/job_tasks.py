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


@celery_app.task(name="workflow.send_shortlist_email", autoretry_for=(Exception,), retry_backoff=True)
def send_shortlist_email_task(
    stage_id: str,
    to_email: str,
    candidate_name: str,
    job_title: str,
    organization_name: str,
    recruiter_email: str,
) -> None:
    asyncio.run(_send_shortlist_email_async(
        UUID(stage_id),
        to_email,
        candidate_name,
        job_title,
        organization_name,
        recruiter_email,
    ))


async def _send_shortlist_email_async(
    stage_id: UUID,
    to_email: str,
    candidate_name: str,
    job_title: str,
    organization_name: str,
    recruiter_email: str,
) -> None:
    from datetime import datetime, timezone
    from app.services.email_service import EmailService
    from app.models.domain import CandidatePipelineStage

    email_service = EmailService()
    report = email_service.health_report()
    if not report["configured"]:
        async with AsyncSessionLocal() as db:
            stage = await db.get(CandidatePipelineStage, stage_id)
            if stage:
                stage.metadata_json = {
                    **(stage.metadata_json or {}),
                    "email_delivery": {
                        "status": "skipped",
                        "reason": report["reason"],
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }
                await db.commit()
        return

    try:
        await email_service.send_shortlist_email_async(
            to_email=to_email,
            candidate_name=candidate_name,
            job_title=job_title,
            organization_name=organization_name,
            recruiter_email=recruiter_email,
        )
        status = "sent"
        error_msg = None
    except Exception as exc:
        status = "failed"
        error_msg = str(exc)

    async with AsyncSessionLocal() as db:
        stage = await db.get(CandidatePipelineStage, stage_id)
        if stage:
            stage.metadata_json = {
                **(stage.metadata_json or {}),
                "email_delivery": {
                    "status": status,
                    "error": error_msg,
                    "recipient": to_email,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            await db.commit()

    if status == "failed":
        raise RuntimeError(f"Failed to send shortlist email: {error_msg}")

