
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import CandidatePipelineStage, FeedbackAction, Organization, PipelineStage, RankingFeedback, RecruiterActivity
from app.repositories.candidates import CandidateRepository
from app.repositories.jobs import JobDescriptionRepository
from app.schemas.auth import AuthContext
from app.schemas.feedback import RankingFeedbackCreate
from app.services.email_service import EmailService

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
        candidate = await CandidateRepository(self.db).get_for_org(payload.candidate_id, auth.organization_id)
        if candidate is None:
            raise HTTPException(status_code=404, detail="Candidate not found")
        job = None
        if payload.job_description_id is not None:
            job = await JobDescriptionRepository(self.db).get_for_org(payload.job_description_id, auth.organization_id)
            if job is None:
                raise HTTPException(status_code=404, detail="Job description not found")
        reward = ACTION_REWARDS[payload.action.value]
        feature_snapshot = dict(payload.feature_snapshot)
        if payload.action == FeedbackAction.shortlist and job is not None:
            feature_snapshot["shortlist_email"] = await self._send_shortlist_email(auth, candidate, job)
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
                    "shortlist_email": feature_snapshot.get("shortlist_email"),
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

    async def _send_shortlist_email(self, auth: AuthContext, candidate, job) -> dict:
        if not candidate.email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot send shortlist email because candidate email is missing")
        organization = await self.db.get(Organization, auth.organization_id)
        if organization is None:
            raise HTTPException(status_code=404, detail="Organization not found")
        try:
            return await EmailService().send_shortlist_email_async(
                to_email=candidate.email,
                candidate_name=candidate.full_name or "Candidate",
                job_title=job.title,
                organization_name=organization.name,
                recruiter_email=str(auth.email),
            )
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Shortlist email delivery failed: {exc}") from exc

    @staticmethod
    def active_learning_priority(score: float, feedback_count: int) -> float:
        uncertainty = 1 - abs(score - 50) / 50
        scarcity = 1 / (feedback_count + 1)
        return round(uncertainty * 0.7 + scarcity * 0.3, 4)
