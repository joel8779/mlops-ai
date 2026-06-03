from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth, require_roles
from app.core.security import UserRole
from app.db.session import get_db
from app.models.domain import ATSScore, Candidate, CandidateMatch, CandidatePipelineStage
from app.repositories.candidates import CandidateRepository
from app.repositories.jobs import JobDescriptionRepository
from app.schemas.auth import AuthContext
from app.schemas.jobs import (
    JobCandidateRankingItem,
    JobDescriptionCreate,
    JobDescriptionRead,
    JobExtractionPreview,
    JobIntelligenceRead,
)
from app.services.delete_service import DeleteWorkflowService
from app.services.ats_scoring_service import ATSScoringService
from app.services.job_intelligence_service import JobIntelligenceService
from app.services.matching_service import MatchingService

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
    title: str | None = Form(None),
    file: UploadFile = File(...),
    auth: AuthContext = Depends(require_roles(UserRole.admin, UserRole.recruiter)),
    db: AsyncSession = Depends(get_db),
):
    return await JobIntelligenceService(db).create_from_upload(auth, title, file)


@router.post("/extract", response_model=JobExtractionPreview)
async def extract_job_description(
    title: str | None = Form(None),
    file: UploadFile = File(...),
    auth: AuthContext = Depends(require_roles(UserRole.admin, UserRole.recruiter)),
    db: AsyncSession = Depends(get_db),
):
    del auth
    return await JobIntelligenceService(db).preview_upload(file, title)


@router.get("", response_model=list[JobDescriptionRead])
async def list_jobs(auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return await JobDescriptionRepository(db).list_active_for_org(auth.organization_id)


@router.get("/{job_id}", response_model=JobDescriptionRead)
async def get_job(job_id: UUID, auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    job = await JobDescriptionRepository(db).get_for_org(job_id, auth.organization_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job description not found")
    return job


@router.get("/{job_id}/intelligence", response_model=JobIntelligenceRead)
async def get_job_intelligence(
    job_id: UUID,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    repository = JobDescriptionRepository(db)
    job = await repository.get_for_org(job_id, auth.organization_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job description not found")

    existing_count = await db.scalar(
        select(CandidateMatch.id)
        .where(
            CandidateMatch.organization_id == auth.organization_id,
            CandidateMatch.job_description_id == job.id,
        )
        .limit(1)
    )
    if existing_count is None:
        await MatchingService(db).rank_candidates(auth.organization_id, auth.user_id, job, limit=100)
    await _ensure_ats_scores(db, auth.organization_id, auth.user_id, job.id)

    rows = await db.execute(
        select(CandidateMatch, Candidate, ATSScore.ats_score)
        .join(Candidate, Candidate.id == CandidateMatch.candidate_id)
        .outerjoin(
            ATSScore,
            (ATSScore.candidate_id == CandidateMatch.candidate_id)
            & (ATSScore.job_description_id == CandidateMatch.job_description_id)
            & (ATSScore.organization_id == auth.organization_id)
        )
        .where(
            CandidateMatch.organization_id == auth.organization_id,
            CandidateMatch.job_description_id == job.id,
            Candidate.organization_id == auth.organization_id,
            Candidate.deleted_at.is_(None),
        )
        .order_by(
            desc(func.coalesce(ATSScore.ats_score, CandidateMatch.overall_score)),
            desc(CandidateMatch.semantic_score),
            desc(CandidateMatch.experience_match),
        )
        .limit(100)
    )
    candidate_repository = CandidateRepository(db)
    ranked: list[JobCandidateRankingItem] = []
    all_missing: list[str] = []
    all_matched: list[str] = []
    for match, candidate, ats_score in rows.all():
        resume = await candidate_repository.latest_resume(candidate.id, auth.organization_id)
        stage = await db.scalar(
            select(CandidatePipelineStage.stage)
            .where(
                CandidatePipelineStage.organization_id == auth.organization_id,
                CandidatePipelineStage.candidate_id == candidate.id,
                CandidatePipelineStage.job_description_id == job.id,
            )
            .order_by(desc(CandidatePipelineStage.updated_at))
            .limit(1)
        )
        all_missing.extend(match.missing_skills or [])
        all_matched.extend(match.matched_skills or [])
        ranked.append(
            JobCandidateRankingItem(
                candidate_id=candidate.id,
                full_name=candidate.full_name,
                email=candidate.email,
                headline=candidate.headline,
                location=candidate.location,
                latest_resume_id=resume.id if resume else None,
                ats_score=float(ats_score) if ats_score is not None else None,
                overall_score=float(match.overall_score),
                semantic_score=float(match.semantic_score),
                skill_match=float(match.skill_match),
                experience_match=float(match.experience_match),
                education_match=float(match.education_match),
                keyword_score=float(match.keyword_score),
                matched_skills=match.matched_skills,
                missing_skills=match.missing_skills,
                explanation=match.explanation,
                current_stage=stage.value if stage else None,
            )
        )
    semantic_scores = [item.semantic_score for item in ranked]
    semantic_insights = {
        "candidate_count": len(ranked),
        "strongest_candidate": ranked[0].model_dump() if ranked else None,
        "average_semantic_alignment": round(sum(semantic_scores) / len(semantic_scores), 2) if semantic_scores else 0,
        "most_matched_skills": _top_terms(all_matched),
        "missing_skill_clusters": _top_terms(all_missing),
        "weakest_alignment_areas": _top_terms(all_missing)[:5],
    }
    return JobIntelligenceRead(job=job, ranked_candidates=ranked, semantic_insights=semantic_insights)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: UUID,
    auth: AuthContext = Depends(require_roles(UserRole.admin, UserRole.recruiter)),
    db: AsyncSession = Depends(get_db),
) -> None:
    job = await JobDescriptionRepository(db).get_for_org(job_id, auth.organization_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job description not found")
    await DeleteWorkflowService(db).delete_job(job)


def _top_terms(values: list[str]) -> list[dict]:
    counts: dict[str, int] = {}
    for value in values:
        key = value.lower()
        counts[key] = counts.get(key, 0) + 1
    return [{"name": key, "count": count} for key, count in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:10]]


async def _ensure_ats_scores(db: AsyncSession, organization_id: UUID, owner_id: UUID, job_id: UUID) -> None:
    candidate_repository = CandidateRepository(db)
    rows = await db.execute(
        select(CandidateMatch, Candidate)
        .join(Candidate, Candidate.id == CandidateMatch.candidate_id)
        .outerjoin(
            ATSScore,
            (ATSScore.candidate_id == CandidateMatch.candidate_id)
            & (ATSScore.job_description_id == CandidateMatch.job_description_id)
            & (ATSScore.organization_id == organization_id)
        )
        .where(
            CandidateMatch.organization_id == organization_id,
            CandidateMatch.job_description_id == job_id,
            ATSScore.id.is_(None),
            Candidate.organization_id == organization_id,
            Candidate.deleted_at.is_(None),
        )
        .order_by(desc(CandidateMatch.overall_score))
        .limit(25)
    )
    job = await JobDescriptionRepository(db).get_for_org(job_id, organization_id)
    if job is None:
        return
    for match, candidate in rows.all():
        resume = await candidate_repository.latest_resume(candidate.id, organization_id)
        if resume is None:
            continue
        skills = await candidate_repository.skills_for_candidate(candidate.id, organization_id)
        await ATSScoringService(db).score_candidate_for_job(
            job,
            candidate,
            resume,
            semantic_score=float(match.semantic_score),
            skills=skills,
        )
