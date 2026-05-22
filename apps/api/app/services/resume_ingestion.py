from hashlib import sha256
from io import BytesIO
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Resume, ResumeProcessingEvent, ResumeStatus
from app.schemas.auth import AuthContext
from app.services.storage import ObjectStorage
from app.tasks.resume_tasks import parse_resume_task

ALLOWED_CONTENT_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "image/png": "png",
    "image/jpeg": "jpg",
}

MAX_UPLOAD_BYTES = 15 * 1024 * 1024


async def ingest_resume(
    *,
    db: AsyncSession,
    auth: AuthContext,
    upload: UploadFile,
    storage: ObjectStorage,
) -> Resume:
    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF, DOCX, PNG, and JPG resumes are supported",
        )

    payload = await upload.read()
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")

    checksum = sha256(payload).hexdigest()
    extension = ALLOWED_CONTENT_TYPES[upload.content_type]
    storage_key = f"organizations/{auth.organization_id}/resumes/{uuid4()}.{extension}"
    storage.upload_fileobj(BytesIO(payload), storage_key, upload.content_type)

    resume = Resume(
        organization_id=auth.organization_id,
        uploaded_by_user_id=auth.user_id,
        original_filename=upload.filename or f"resume.{extension}",
        content_type=upload.content_type,
        storage_key=storage_key,
        checksum_sha256=checksum,
        status=ResumeStatus.uploaded,
        metadata_json={"size_bytes": len(payload)},
    )
    db.add(resume)
    await db.flush()
    db.add(
        ResumeProcessingEvent(
            organization_id=auth.organization_id,
            resume_id=resume.id,
            event_type="resume.uploaded",
            payload={"storage_key": storage_key, "checksum_sha256": checksum},
        )
    )
    await db.commit()
    await db.refresh(resume)

    parse_resume_task.delay(str(resume.id))
    return resume
