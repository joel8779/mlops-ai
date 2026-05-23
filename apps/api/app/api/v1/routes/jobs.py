from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth, require_roles
from app.core.security import UserRole
from app.db.session import get_db
from app.repositories.jobs import JobDescriptionRepository
from app.schemas.auth import AuthContext
from app.schemas.jobs import JobDescriptionCreate, JobDescriptionRead
from app.services.job_intelligence_service import JobIntelligenceService

router = APIRouter()


@router.post("", response_model=JobDescriptionRead, status_code=status.HTTP_201_CREATED)
async def create_job_description(
    payload: JobDescriptionCreate,
    auth: AuthContext = Depends(require_roles(UserRole.admin, UserRole.recruiter)),
    db: AsyncSession = Depends(get_db),
):
    return await JobIntelligenceService(db).create_from_text(auth, payload)


@router.post("/upload", response_model=JobDescriptionRead, status_code=status.HTTP_201_CREATED)
async def upload_job_description(
    title: str = Form(...),
    file: UploadFile = File(...),
    auth: AuthContext = Depends(require_roles(UserRole.admin, UserRole.recruiter)),
    db: AsyncSession = Depends(get_db),
):
    return await JobIntelligenceService(db).create_from_upload(auth, title, file)


@router.get("", response_model=list[JobDescriptionRead])
async def list_jobs(auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return await JobDescriptionRepository(db).list_active_for_org(auth.organization_id)


@router.get("/{job_id}", response_model=JobDescriptionRead)
async def get_job(job_id: UUID, auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    job = await JobDescriptionRepository(db).get_for_org(job_id, auth.organization_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job description not found")
    return job
