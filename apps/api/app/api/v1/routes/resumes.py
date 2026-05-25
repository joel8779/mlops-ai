from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth, require_roles
from app.core.security import UserRole
from app.db.session import get_db
from app.models.domain import Resume
from app.repositories.resumes import ResumeRepository
from app.schemas.auth import AuthContext
from app.schemas.resume import ResumeRead, ResumeUploadResponse
from app.services.resume_ingestion import ingest_resume
from app.services.storage import ObjectStorage, get_object_storage

router = APIRouter()


@router.get("", response_model=list[ResumeRead])
async def list_resumes(
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
) -> list[Resume]:
    return await ResumeRepository(db).list_for_org(auth.organization_id)


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_resume(
    file: UploadFile = File(...),
    auth: AuthContext = Depends(require_roles(UserRole.admin, UserRole.recruiter)),
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
    resume = await ResumeRepository(db).get_for_org(resume_id, auth.organization_id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume
