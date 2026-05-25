from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import CandidatePipelineStage, FeedbackAction, PipelineStage, RankingFeedback, RecruiterActivity
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
        reward = ACTION_REWARDS[payload.action.value]
        feedback = RankingFeedback(
            organization_id=auth.organization_id,
            user_id=auth.user_id,
            candidate_id=payload.candidate_id,
            job_description_id=payload.job_description_id,
            action=payload.action,
            reward=reward,
            rank_position=payload.rank_position,
            model_version=payload.model_version,
            feature_snapshot=payload.feature_snapshot,
        )
        self.db.add(feedback)
        self.db.add(
            RecruiterActivity(
                organization_id=auth.organization_id,
                user_id=auth.user_id,
                candidate_id=payload.candidate_id,
                job_description_id=payload.job_description_id,
                activity_type=f"feedback.{payload.action.value}",
                payload={"reward": reward, "rank_position": payload.rank_position},
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

    @staticmethod
    def active_learning_priority(score: float, feedback_count: int) -> float:
        uncertainty = 1 - abs(score - 50) / 50
        scarcity = 1 / (feedback_count + 1)
        return round(uncertainty * 0.7 + scarcity * 0.3, 4)
