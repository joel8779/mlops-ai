from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.db.session import get_db
from app.models.domain import CandidateMatch, CandidatePipelineStage
from app.repositories.candidates import CandidateRepository
from app.schemas.auth import AuthContext
from app.schemas.candidates import CandidateListItem, CandidateRead

router = APIRouter()


@router.get("", response_model=list[CandidateListItem])
async def list_candidates(
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    repository = CandidateRepository(db)
    candidates = await repository.list_for_org(auth.organization_id)
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
    item = await _candidate_item(db, repository, candidate)
    resume = await repository.latest_resume(candidate.id)
    return CandidateRead(
        **item.model_dump(),
        raw_profile=candidate.raw_profile,
        resume_text_preview=(resume.extracted_text[:2000] if resume and resume.extracted_text else None),
    )


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
