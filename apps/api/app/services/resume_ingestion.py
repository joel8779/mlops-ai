from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.core.config import settings
from app.models.domain import Resume, ResumeStatus
from app.schemas.auth import AuthContext
from app.services.storage import ObjectStorage
from app.utils.files import checksum, read_validated_upload, safe_extension
from app.workers.resume_tasks import parse_resume_task

logger = get_logger(__name__)


async def ingest_resume(
    db: AsyncSession,
    auth: AuthContext,
    upload: UploadFile,
    storage: ObjectStorage,
) -> Resume:
    payload = await read_validated_upload(upload, settings.max_upload_bytes)
    content_type = upload.content_type or "application/octet-stream"
    digest = checksum(payload)
    extension = safe_extension(upload.filename, content_type)
    storage_key = f"organizations/{auth.organization_id}/resumes/{uuid4()}{extension}"
    storage.upload_bytes(payload, storage_key, content_type)

    resume = Resume(
        organization_id=auth.organization_id,
        uploaded_by_user_id=auth.user_id,
        original_filename=upload.filename or f"resume{extension}",
        content_type=content_type,
        storage_key=storage_key,
        checksum_sha256=digest,
        status=ResumeStatus.queued,
        metadata_json={"size_bytes": len(payload)},
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    # Celery keeps expensive parsing/OCR/embedding work out of the request path.
    try:
        parse_resume_task.apply_async(args=[str(resume.id)], retry=False, ignore_result=True)
    except Exception as exc:
        logger.error("resume_enqueue_failed", resume_id=str(resume.id), error=str(exc))
        resume.status = ResumeStatus.failed
        resume.parse_error = "Resume processing queue is unavailable"
        resume.metadata_json = {**(resume.metadata_json or {}), "enqueue_error": str(exc)}
        await db.commit()
        await db.refresh(resume)
    return resume
