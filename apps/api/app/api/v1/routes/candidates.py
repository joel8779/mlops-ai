from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth, require_roles
from app.core.security import UserRole
from app.db.session import get_db
from app.models.domain import CandidateMatch, CandidatePipelineStage
from app.repositories.candidates import CandidateRepository
from app.schemas.auth import AuthContext
from app.schemas.candidates import CandidateListItem, CandidateRead
from app.services.candidate_extraction_service import CandidateExtractionService
from app.services.delete_service import DeleteWorkflowService

router = APIRouter()


@router.get("", response_model=list[CandidateListItem])
async def list_candidates(
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    repository = CandidateRepository(db)
    candidates = await repository.list_for_org(auth.organization_id)
    for candidate in candidates:
        await _repair_candidate_identity(db, repository, candidate)
    await db.commit()
    return [await _candidate_item(db, repository, candidate) for candidate in candidates]


@router.get("/{candidate_id}", response_model=CandidateRead)
async def get_candidate(
    candidate_id: UUID,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    repository = CandidateRepository(db)
    candidate = await repository.get_for_org(candidate_id, auth.organization_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    await _repair_candidate_identity(db, repository, candidate)
    await db.commit()
    item = await _candidate_item(db, repository, candidate)
    resume = await repository.latest_resume(candidate.id)
    return CandidateRead(
        **item.model_dump(),
        raw_profile=candidate.raw_profile,
        resume_text_preview=(resume.extracted_text[:2000] if resume and resume.extracted_text else None),
    )


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: UUID,
    auth: AuthContext = Depends(require_roles(UserRole.admin, UserRole.recruiter)),
    db: AsyncSession = Depends(get_db),
) -> None:
    repository = CandidateRepository(db)
    candidate = await repository.get_for_org(candidate_id, auth.organization_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    await DeleteWorkflowService(db).delete_candidate(candidate)


async def _candidate_item(db: AsyncSession, repository: CandidateRepository, candidate) -> CandidateListItem:
    skills = await repository.skills_for_candidate(candidate.id)
    resume = await repository.latest_resume(candidate.id)
    stage = await db.scalar(
        select(CandidatePipelineStage.stage)
        .where(CandidatePipelineStage.candidate_id == candidate.id)
        .order_by(CandidatePipelineStage.updated_at.desc())
        .limit(1)
    )
    best_match = await db.scalar(
        select(func.max(CandidateMatch.overall_score)).where(CandidateMatch.candidate_id == candidate.id)
    )
    return CandidateListItem(
        id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        headline=candidate.headline,
        location=candidate.location,
        summary=candidate.summary,
        skills=skills,
        latest_resume_id=resume.id if resume else None,
        latest_resume_status=resume.status.value if resume else None,
        current_stage=stage.value if stage else None,
        best_match_score=float(best_match) if best_match is not None else None,
        created_at=candidate.created_at,
    )


async def _repair_candidate_identity(db: AsyncSession, repository: CandidateRepository, candidate) -> None:
    if candidate.full_name and candidate.full_name != "Candidate Profile" and candidate.headline:
        return
    resume = await repository.latest_resume(candidate.id)
    if resume is None or not resume.extracted_text:
        if candidate.email and (not candidate.full_name or candidate.full_name == "Candidate Profile"):
            candidate.full_name = _name_from_email(candidate.email)
        return
    extraction = await CandidateExtractionService().extract(
        resume.extracted_text,
        resume.original_filename,
        resume.metadata_json.get("parse") if resume.metadata_json else {},
        use_gemini=False,
    )
    if not candidate.full_name or candidate.full_name == "Candidate Profile":
        candidate.full_name = extraction.full_name
    candidate.email = candidate.email or extraction.email
    candidate.phone = candidate.phone or extraction.phone
    candidate.summary = candidate.summary or extraction.summary
    if not candidate.headline and extraction.skills:
        candidate.headline = f"{(extraction.inferred_seniority or 'qualified').title()} candidate with {', '.join(extraction.skills[:3])}"
    candidate.raw_profile = {
        **(candidate.raw_profile or {}),
        "identity_repair": {
            "source": extraction.source,
            "resume_id": str(resume.id),
        },
        "education": (candidate.raw_profile or {}).get("education") or extraction.education,
        "experience": (candidate.raw_profile or {}).get("experience") or extraction.experience,
        "projects": (candidate.raw_profile or {}).get("projects") or extraction.projects,
        "inferred_seniority": (candidate.raw_profile or {}).get("inferred_seniority") or extraction.inferred_seniority,
    }


def _name_from_email(email: str) -> str:
    local = email.split("@", 1)[0]
    parts = [part for part in local.replace(".", "_").replace("-", "_").split("_") if part]
    return " ".join(part.capitalize() for part in parts[:4]) or "Imported Candidate"
