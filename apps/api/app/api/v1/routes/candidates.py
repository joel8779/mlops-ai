from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth, require_roles
from app.core.security import UserRole
from app.db.session import get_db
from app.models.domain import CandidateMatch, CandidatePipelineStage, CandidateSkill, Resume
from app.repositories.candidates import CandidateRepository
from app.schemas.auth import AuthContext
from app.schemas.candidates import CandidateIdentityUpdate, CandidateListItem, CandidateRead
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
    items = [await _candidate_item(db, repository, candidate, auth.organization_id, None) for candidate in candidates]
    return sorted(items, key=lambda item: (item.best_match_score or 0, item.created_at), reverse=True)


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
    item = await _candidate_item(db, repository, candidate, auth.organization_id, None)
    resume = await repository.latest_resume(candidate.id, auth.organization_id)
    return CandidateRead(
        **item.model_dump(),
        raw_profile=candidate.raw_profile,
        resume_text_preview=(resume.extracted_text[:2000] if resume and resume.extracted_text else None),
    )


@router.patch("/{candidate_id}/identity", response_model=CandidateRead)
async def update_candidate_identity(
    candidate_id: UUID,
    payload: CandidateIdentityUpdate,
    auth: AuthContext = Depends(require_roles(UserRole.admin, UserRole.recruiter)),
    db: AsyncSession = Depends(get_db),
):
    repository = CandidateRepository(db)
    candidate = await repository.get_for_org(candidate_id, auth.organization_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if payload.full_name is not None:
        candidate.full_name = payload.full_name.strip()
    if payload.email is not None:
        candidate.email = str(payload.email).lower()
    candidate.raw_profile = {
        **(candidate.raw_profile or {}),
        "identity_source": "recruiter_manual",
        "identity_updated_by": str(auth.user_id),
    }
    await db.commit()
    await db.refresh(candidate)
    item = await _candidate_item(db, repository, candidate, auth.organization_id, None)
    resume = await repository.latest_resume(candidate.id, auth.organization_id)
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


async def _candidate_item(
    db: AsyncSession,
    repository: CandidateRepository,
    candidate,
    organization_id: UUID,
    owner_id: UUID | None,
) -> CandidateListItem:
    skills = await repository.skills_for_candidate(candidate.id, organization_id, owner_id)
    if not skills:
        skills = await _repair_candidate_skills(db, candidate)
    resume = await repository.latest_resume(candidate.id, organization_id, owner_id)
    stage_query = (
        select(CandidatePipelineStage.stage)
        .where(
            CandidatePipelineStage.organization_id == organization_id,
            CandidatePipelineStage.candidate_id == candidate.id,
        )
        .order_by(CandidatePipelineStage.updated_at.desc())
        .limit(1)
    )
    if owner_id is not None:
        stage_query = stage_query.where(CandidatePipelineStage.owner_id == owner_id)
    stage = await db.scalar(stage_query)
    match_query = select(func.max(CandidateMatch.overall_score)).where(
        CandidateMatch.organization_id == organization_id,
        CandidateMatch.candidate_id == candidate.id,
    )
    if owner_id is not None:
        match_query = match_query.where(CandidateMatch.owner_id == owner_id)
    best_match = await db.scalar(match_query)
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
    if candidate.full_name and candidate.full_name not in {"Candidate Profile", "Uploaded Candidate"} and candidate.headline:
        return
    resume = await repository.latest_resume(candidate.id, candidate.organization_id, candidate.owner_id)
    if resume is None or not resume.extracted_text:
        return
    extraction = await CandidateExtractionService().extract(
        resume.extracted_text,
        resume.original_filename,
        resume.metadata_json.get("parse") if resume.metadata_json else {},
        use_gemini=False,
    )
    candidate.email = candidate.email or extraction.email
    candidate.phone = candidate.phone or extraction.phone
    candidate.summary = candidate.summary or extraction.summary
    if not candidate.headline:
        candidate.headline = CandidateExtractionService.headline(extraction)
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
        "skills": (candidate.raw_profile or {}).get("skills") or extraction.skills,
    }


async def _repair_candidate_skills(db: AsyncSession, candidate) -> list[str]:
    raw_skills = (candidate.raw_profile or {}).get("skills")
    if not isinstance(raw_skills, list):
        return []
    resume = await db.scalar(
        select(Resume)
        .where(
            Resume.organization_id == candidate.organization_id,
            Resume.candidate_id == candidate.id,
            Resume.deleted_at.is_(None),
        )
        .order_by(Resume.created_at.desc())
        .limit(1)
    )
    evidence_text = resume.extracted_text if resume and resume.extracted_text else None
    skills = CandidateExtractionService.normalize_skills(raw_skills, evidence_text)
    if not skills:
        return []
    await db.execute(
        delete(CandidateSkill).where(
            CandidateSkill.organization_id == candidate.organization_id,
            CandidateSkill.candidate_id == candidate.id,
        )
    )
    for skill in skills:
        db.add(
            CandidateSkill(
                organization_id=candidate.organization_id,
                owner_id=candidate.owner_id,
                candidate_id=candidate.id,
                normalized_skill=skill,
                raw_skill=skill,
                confidence=0.80,
            )
        )
    await db.flush()
    return skills
