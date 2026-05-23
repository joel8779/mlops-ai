from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import RankingFeedback, RecruiterActivity
from app.schemas.auth import AuthContext
from app.schemas.feedback import RankingFeedbackCreate

ACTION_REWARDS = {
    "shortlist": 2.0,
    "reject": -1.0,
    "interview": 3.5,
    "hire": 5.0,
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
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    @staticmethod
    def active_learning_priority(score: float, feedback_count: int) -> float:
        uncertainty = 1 - abs(score - 50) / 50
        scarcity = 1 / (feedback_count + 1)
        return round(uncertainty * 0.7 + scarcity * 0.3, 4)
