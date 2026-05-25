from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.db.session import get_db
from app.models.domain import CandidateMatch
from app.repositories.candidates import CandidateRepository
from app.repositories.jobs import JobDescriptionRepository
from app.repositories.resumes import ResumeRepository
from app.schemas.ats import ATSScoreRead
from app.schemas.auth import AuthContext
from app.services.ats_scoring_service import ATSScoringService

router = APIRouter()


@router.post("/jobs/{job_id}/candidates/{candidate_id}/score", response_model=ATSScoreRead)
async def score_candidate_for_job(
    job_id: UUID,
    candidate_id: UUID,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    job = await JobDescriptionRepository(db).get_for_org(job_id, auth.organization_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job description not found")
    candidate_repository = CandidateRepository(db)
    candidate = await candidate_repository.get_for_org(candidate_id, auth.organization_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    resume = await candidate_repository.latest_resume(candidate.id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    skills = await candidate_repository.skills_for_candidate(candidate.id)
    existing_match = await db.scalar(
        select(CandidateMatch).where(
            CandidateMatch.candidate_id == candidate.id,
            CandidateMatch.job_description_id == job.id,
            CandidateMatch.organization_id == auth.organization_id,
        )
    )
    semantic_score = float(existing_match.semantic_score) if existing_match else 0.0
    return await ATSScoringService(db).score_candidate_for_job(job, candidate, resume, semantic_score=semantic_score, skills=skills)


@router.post("/resumes/{resume_id}/score", status_code=status.HTTP_400_BAD_REQUEST)
async def reject_global_resume_score(
    resume_id: UUID,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    resume = await ResumeRepository(db).get_for_org(resume_id, auth.organization_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="ATS scoring requires a job context. Use /ats/jobs/{job_id}/candidates/{candidate_id}/score.",
    )
