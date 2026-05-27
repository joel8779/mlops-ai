from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import CandidatePipelineStage, FeedbackAction, PipelineStage, RankingFeedback, RecruiterActivity
from app.repositories.candidates import CandidateRepository
from app.repositories.jobs import JobDescriptionRepository
from app.schemas.auth import AuthContext
from app.schemas.feedback import RankingFeedbackCreate

ACTION_REWARDS = {
    "shortlist": 2.0,
    "reject": -1.0,
    "interview": 3.5,
    "hire": 5.0,
}

ACTION_STAGES = {
    FeedbackAction.shortlist: PipelineStage.shortlisted,
    FeedbackAction.reject: PipelineStage.rejected,
    FeedbackAction.interview: PipelineStage.interviewing,
    FeedbackAction.hire: PipelineStage.hired,
}


class FeedbackService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def record(self, auth: AuthContext, payload: RankingFeedbackCreate) -> RankingFeedback:
        candidate = await CandidateRepository(self.db).get_for_owner(payload.candidate_id, auth.organization_id, auth.user_id)
        if candidate is None:
            raise HTTPException(status_code=404, detail="Candidate not found")
        job = None
        if payload.job_description_id is not None:
            job = await JobDescriptionRepository(self.db).get_for_owner(payload.job_description_id, auth.organization_id, auth.user_id)
            if job is None:
                raise HTTPException(status_code=404, detail="Job description not found")
        reward = ACTION_REWARDS[payload.action.value]
        feature_snapshot = dict(payload.feature_snapshot)
        if payload.action == FeedbackAction.shortlist and job is not None:
            feature_snapshot["shortlist_email_draft"] = await self._shortlist_email_draft(candidate.full_name, job.title)
        feedback = RankingFeedback(
            organization_id=auth.organization_id,
            owner_id=auth.user_id,
            user_id=auth.user_id,
            candidate_id=payload.candidate_id,
            job_description_id=payload.job_description_id,
            action=payload.action,
            reward=reward,
            rank_position=payload.rank_position,
            model_version=payload.model_version,
            feature_snapshot=feature_snapshot,
        )
        self.db.add(feedback)
        self.db.add(
            RecruiterActivity(
                organization_id=auth.organization_id,
                owner_id=auth.user_id,
                user_id=auth.user_id,
                candidate_id=payload.candidate_id,
                job_description_id=payload.job_description_id,
                activity_type=f"feedback.{payload.action.value}",
                payload={
                    "reward": reward,
                    "rank_position": payload.rank_position,
                    "shortlist_email_draft": feature_snapshot.get("shortlist_email_draft"),
                },
            )
        )
        if payload.job_description_id is not None:
            await self._upsert_pipeline_stage(auth, payload)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def _upsert_pipeline_stage(self, auth: AuthContext, payload: RankingFeedbackCreate) -> None:
        target_stage = ACTION_STAGES.get(payload.action)
        if target_stage is None:
            return
        stage = await self.db.scalar(
            select(CandidatePipelineStage).where(
                CandidatePipelineStage.organization_id == auth.organization_id,
                CandidatePipelineStage.owner_id == auth.user_id,
                CandidatePipelineStage.candidate_id == payload.candidate_id,
                CandidatePipelineStage.job_description_id == payload.job_description_id,
                CandidatePipelineStage.deleted_at.is_(None),
            )
        )
        if stage is None:
            stage = CandidatePipelineStage(
                organization_id=auth.organization_id,
                owner_id=auth.user_id,
                candidate_id=payload.candidate_id,
                job_description_id=payload.job_description_id,
                position=payload.rank_position or 0,
                metadata_json={},
            )
        stage.stage = target_stage
        stage.position = payload.rank_position or stage.position
        stage.metadata_json = {
            **(stage.metadata_json or {}),
            "source": "feedback.ranking",
            "action": payload.action.value,
        }
        self.db.add(stage)

    async def _shortlist_email_draft(self, candidate_name: str | None, job_title: str) -> str:
        name = candidate_name or "Candidate"
        fallback = (
            f"Subject: Interview invitation for {job_title}\n\n"
            f"Hi {name},\n\n"
            f"Thanks for your interest in the {job_title} role. Your background looks relevant, "
            "and we would like to invite you to the next interview step.\n\n"
            "Please share a few time windows that work for you this week.\n\n"
            "Best,\nRecruiting Team"
        )
        try:
            from app.services.llm.providers.gemini_provider import GenerationOptions
            from app.services.llm_provider import get_llm_provider

            provider = get_llm_provider()
            result = await provider.complete(
                (
                    "Draft a concise recruiter-ready interview invitation email. "
                    f"Candidate: {name}. Job title: {job_title}. Tone: warm, professional, direct."
                ),
                "You write recruiter outreach emails. Do not invent compensation, dates, or interviewers.",
                GenerationOptions(temperature=0.3, max_output_tokens=450),
            )
            return result.text.strip() or fallback
        except Exception:
            return fallback

    @staticmethod
    def active_learning_priority(score: float, feedback_count: int) -> float:
        uncertainty = 1 - abs(score - 50) / 50
        scarcity = 1 / (feedback_count + 1)
        return round(uncertainty * 0.7 + scarcity * 0.3, 4)
