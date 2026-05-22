from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.db.session import get_db
from app.models.domain import Resume
from app.schemas.auth import AuthContext
from app.schemas.resume import ResumeRead, ResumeUploadResponse
from app.services.resume_ingestion import ingest_resume
from app.services.storage import ObjectStorage, get_object_storage

router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_resume(
    file: UploadFile = File(...),
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
    storage: ObjectStorage = Depends(get_object_storage),
) -> Resume:
    return await ingest_resume(db=db, auth=auth, upload=file, storage=storage)


@router.get("/{resume_id}", response_model=ResumeRead)
async def get_resume(
    resume_id: UUID,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
) -> Resume:
    result = await db.execute(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.organization_id == auth.organization_id,
        )
    )
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume
