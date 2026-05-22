import asyncio
from uuid import UUID

import structlog
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.domain import Resume, ResumeProcessingEvent, ResumeStatus
from app.services.resume_parser import ResumeParser
from app.services.storage import ObjectStorage
from app.tasks.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(
    name="resume.parse",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def parse_resume_task(resume_id: str) -> None:
    asyncio.run(_parse_resume(UUID(resume_id)))


async def _parse_resume(resume_id: UUID) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Resume).where(Resume.id == resume_id))
        resume = result.scalar_one_or_none()
        if resume is None:
            logger.warning("resume_parse_missing", resume_id=str(resume_id))
            return

        resume.status = ResumeStatus.parsing
        db.add(
            ResumeProcessingEvent(
                organization_id=resume.organization_id,
                resume_id=resume.id,
                event_type="resume.parsing_started",
                payload={},
            )
        )
        await db.commit()

        try:
            payload = ObjectStorage().download_bytes(resume.storage_key)
            parsed = ResumeParser().parse(payload, resume.content_type)
            resume.status = ResumeStatus.parsed
            resume.parser_version = parsed.parser_version
            resume.extracted_text = parsed.text
            resume.metadata_json = {**resume.metadata_json, "parse": parsed.metadata}
            event_type = "resume.parsed"
            event_payload = {
                "parser_version": parsed.parser_version,
                "text_length": len(parsed.text),
                "metadata": parsed.metadata,
            }
        except Exception as exc:
            resume.status = ResumeStatus.failed
            resume.parse_error = str(exc)
            event_type = "resume.parse_failed"
            event_payload = {"error": str(exc)}

        db.add(
            ResumeProcessingEvent(
                organization_id=resume.organization_id,
                resume_id=resume.id,
                event_type=event_type,
                payload=event_payload,
            )
        )
        await db.commit()
