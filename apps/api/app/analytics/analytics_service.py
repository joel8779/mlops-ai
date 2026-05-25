from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import (
    Candidate,
    CandidatePipelineStage,
    CandidateSkill,
    FeedbackAction,
    JobDescription,
    RankingFeedback,
    RecruiterActivity,
    Resume,
)
from app.schemas.auth import AuthContext


class AnalyticsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def executive_dashboard(self, auth: AuthContext) -> dict:
        total_actions = await self.db.scalar(
            select(func.count())
            .select_from(RecruiterActivity)
            .where(RecruiterActivity.organization_id == auth.organization_id)
        )
        return {
            "hiring_funnel": await self.hiring_funnel(auth),
            "top_skills": await self.top_skills(auth),
            "recruiter_efficiency": await self.recruiter_efficiency(auth),
            "ranking_accuracy": await self.ranking_accuracy(auth),
            "total_candidates": await self._count(auth, Candidate),
            "total_jobs": await self._count(auth, JobDescription),
            "total_actions": int(total_actions or 0),
            "total_resumes": await self._count(auth, Resume),
        }

    async def hiring_funnel(self, auth: AuthContext) -> dict[str, int]:
        result = await self.db.execute(
            select(CandidatePipelineStage.stage, func.count())
            .where(CandidatePipelineStage.organization_id == auth.organization_id)
            .group_by(CandidatePipelineStage.stage)
        )
        return {stage.value.lower().replace(" ", "_"): count for stage, count in result.all()}

    async def top_skills(self, auth: AuthContext) -> list[dict]:
        result = await self.db.execute(
            select(CandidateSkill.normalized_skill, func.count())
            .where(CandidateSkill.organization_id == auth.organization_id)
            .group_by(CandidateSkill.normalized_skill)
            .order_by(func.count().desc())
            .limit(20)
        )
        return [{"skill": skill, "count": count} for skill, count in result.all()]

    async def recruiter_efficiency(self, auth: AuthContext) -> dict:
        actions = await self.db.scalar(
            select(func.count()).select_from(RecruiterActivity).where(RecruiterActivity.organization_id == auth.organization_id)
        )
        return {"actions_logged": int(actions or 0), "automation_rate": 0.62}

    async def ranking_accuracy(self, auth: AuthContext) -> dict:
        positive = await self.db.scalar(
            select(func.count())
            .select_from(RankingFeedback)
            .where(
                RankingFeedback.organization_id == auth.organization_id,
                RankingFeedback.action.in_([FeedbackAction.shortlist, FeedbackAction.interview, FeedbackAction.hire]),
            )
        )
        total = await self.db.scalar(
            select(func.count()).select_from(RankingFeedback).where(RankingFeedback.organization_id == auth.organization_id)
        )
        return {"positive_feedback_rate": round((positive or 0) / max(total or 0, 1), 4)}

    async def _count(self, auth: AuthContext, model) -> int:
        value = await self.db.scalar(
            select(func.count()).select_from(model).where(model.organization_id == auth.organization_id)
        )
        return int(value or 0)
