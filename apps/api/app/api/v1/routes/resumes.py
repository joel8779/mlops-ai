from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth, require_roles
from app.core.security import UserRole
from app.db.session import get_db
from app.models.domain import Resume, ResumeProcessingEvent
from app.repositories.resumes import ResumeRepository
from app.schemas.auth import AuthContext
from app.schemas.resume import ResumeRead, ResumeUploadResponse
from app.services.delete_service import DeleteWorkflowService
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


@router.get("/{resume_id}/diagnostics")
async def get_resume_diagnostics(
    resume_id: UUID,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    resume = await ResumeRepository(db).get_for_org(resume_id, auth.organization_id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    event_rows = await db.execute(
        select(ResumeProcessingEvent)
        .where(
            ResumeProcessingEvent.organization_id == auth.organization_id,
            ResumeProcessingEvent.resume_id == resume.id,
        )
        .order_by(desc(ResumeProcessingEvent.created_at))
        .limit(50)
    )
    events = list(event_rows.scalars().all())
    latest_failure = next(
        (
            event.payload.get("error")
            for event in events
            if (event.payload and event.payload.get("status") == "failure") or event.event_type.endswith("failed")
        ),
        None,
    )
    return {
        "resume_id": str(resume.id),
        "status": resume.status.value,
        "candidate_id": str(resume.candidate_id) if resume.candidate_id else None,
        "parse_error": resume.parse_error,
        "latest_failure": latest_failure or (resume.metadata_json or {}).get("last_failure"),
        "events": [
            {
                "event_type": event.event_type,
                "payload": event.payload,
                "created_at": event.created_at.isoformat() if event.created_at else None,
            }
            for event in events
        ],
    }


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    auth: AuthContext = Depends(require_roles(UserRole.admin, UserRole.recruiter)),
    db: AsyncSession = Depends(get_db),
    storage: ObjectStorage = Depends(get_object_storage),
) -> None:
    resume = await ResumeRepository(db).get_for_org(resume_id, auth.organization_id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    await DeleteWorkflowService(db, storage).delete_resume(resume)
