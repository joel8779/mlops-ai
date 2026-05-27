from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import (
    Candidate,
    CandidateMatch,
    CandidatePipelineStage,
    CandidateSkill,
    FeedbackAction,
    JobDescription,
    RankingFeedback,
    RecruiterActivity,
    Resume,
    ResumeStatus,
    ATSScore,
)
from app.schemas.auth import AuthContext


class AnalyticsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def executive_dashboard(self, auth: AuthContext) -> dict:
        total_actions = await self.db.scalar(
            select(func.count())
            .select_from(RecruiterActivity)
            .where(RecruiterActivity.organization_id == auth.organization_id, RecruiterActivity.owner_id == auth.user_id)
        )
        return {
            "hiring_funnel": await self.hiring_funnel(auth),
            "top_skills": await self.top_skills(auth),
            "recruiter_efficiency": await self.recruiter_efficiency(auth),
            "ranking_accuracy": await self.ranking_accuracy(auth),
            "candidates_per_job": await self.candidates_per_job(auth),
            "ats_score_distribution": await self.ats_score_distribution(auth),
            "shortlist_counts": await self.shortlist_counts(auth),
            "resume_processing_counts": await self.resume_processing_counts(auth),
            "semantic_match_averages": await self.semantic_match_averages(auth),
            "pipeline_stage_counts": await self.hiring_funnel(auth),
            "total_candidates": await self._count(auth, Candidate),
            "total_jobs": await self._count(auth, JobDescription),
            "total_actions": int(total_actions or 0),
            "total_resumes": await self._count(auth, Resume),
        }

    async def hiring_funnel(self, auth: AuthContext) -> dict[str, int]:
        result = await self.db.execute(
            select(CandidatePipelineStage.stage, func.count())
            .where(CandidatePipelineStage.organization_id == auth.organization_id, CandidatePipelineStage.owner_id == auth.user_id)
            .group_by(CandidatePipelineStage.stage)
        )
        return {stage.value.lower().replace(" ", "_"): count for stage, count in result.all()}

    async def top_skills(self, auth: AuthContext) -> list[dict]:
        result = await self.db.execute(
            select(CandidateSkill.normalized_skill, func.count())
            .where(CandidateSkill.organization_id == auth.organization_id, CandidateSkill.owner_id == auth.user_id)
            .group_by(CandidateSkill.normalized_skill)
            .order_by(func.count().desc())
            .limit(20)
        )
        return [{"skill": skill, "count": count} for skill, count in result.all()]

    async def recruiter_efficiency(self, auth: AuthContext) -> dict:
        actions = await self.db.scalar(
            select(func.count()).select_from(RecruiterActivity).where(
                RecruiterActivity.organization_id == auth.organization_id,
                RecruiterActivity.owner_id == auth.user_id,
            )
        )
        ranked_jobs = await self.db.scalar(
            select(func.count(func.distinct(CandidateMatch.job_description_id))).where(
                CandidateMatch.organization_id == auth.organization_id,
                CandidateMatch.owner_id == auth.user_id,
            )
        )
        total_jobs = await self._count(auth, JobDescription)
        return {
            "actions_logged": int(actions or 0),
            "ranked_jobs": int(ranked_jobs or 0),
            "ranking_coverage": round((ranked_jobs or 0) / max(total_jobs, 1), 4),
        }

    async def ranking_accuracy(self, auth: AuthContext) -> dict:
        positive = await self.db.scalar(
            select(func.count())
            .select_from(RankingFeedback)
            .where(
                RankingFeedback.organization_id == auth.organization_id,
                RankingFeedback.owner_id == auth.user_id,
                RankingFeedback.action.in_([FeedbackAction.shortlist, FeedbackAction.interview, FeedbackAction.hire]),
            )
        )
        total = await self.db.scalar(
            select(func.count()).select_from(RankingFeedback).where(
                RankingFeedback.organization_id == auth.organization_id,
                RankingFeedback.owner_id == auth.user_id,
            )
        )
        return {"positive_feedback_rate": round((positive or 0) / max(total or 0, 1), 4)}

    async def candidates_per_job(self, auth: AuthContext) -> list[dict]:
        rows = await self.db.execute(
            select(JobDescription.id, JobDescription.title, func.count(CandidateMatch.candidate_id))
            .join(
                CandidateMatch,
                and_(
                    CandidateMatch.job_description_id == JobDescription.id,
                    CandidateMatch.organization_id == auth.organization_id,
                    CandidateMatch.owner_id == auth.user_id,
                ),
                isouter=True,
            )
            .where(
                JobDescription.organization_id == auth.organization_id,
                JobDescription.owner_id == auth.user_id,
                JobDescription.deleted_at.is_(None),
            )
            .group_by(JobDescription.id, JobDescription.title)
            .order_by(func.count(CandidateMatch.candidate_id).desc())
        )
        return [{"job_id": str(job_id), "job_title": title, "candidate_count": int(count)} for job_id, title, count in rows.all()]

    async def ats_score_distribution(self, auth: AuthContext) -> dict[str, int]:
        scores = await self.db.scalars(
            select(ATSScore.ats_score).where(ATSScore.organization_id == auth.organization_id, ATSScore.owner_id == auth.user_id)
        )
        buckets = {"90_100": 0, "75_89": 0, "60_74": 0, "0_59": 0}
        for value in scores:
            score = float(value)
            if score >= 90:
                buckets["90_100"] += 1
            elif score >= 75:
                buckets["75_89"] += 1
            elif score >= 60:
                buckets["60_74"] += 1
            else:
                buckets["0_59"] += 1
        return buckets

    async def shortlist_counts(self, auth: AuthContext) -> dict[str, int]:
        rows = await self.db.execute(
            select(RankingFeedback.action, func.count())
            .where(RankingFeedback.organization_id == auth.organization_id, RankingFeedback.owner_id == auth.user_id)
            .group_by(RankingFeedback.action)
        )
        return {action.value: int(count) for action, count in rows.all()}

    async def resume_processing_counts(self, auth: AuthContext) -> dict[str, int]:
        rows = await self.db.execute(
            select(Resume.status, func.count())
            .where(Resume.organization_id == auth.organization_id, Resume.owner_id == auth.user_id, Resume.deleted_at.is_(None))
            .group_by(Resume.status)
        )
        counts = {status.value: int(count) for status, count in rows.all()}
        return {status.value: counts.get(status.value, 0) for status in ResumeStatus}

    async def semantic_match_averages(self, auth: AuthContext) -> list[dict]:
        rows = await self.db.execute(
            select(
                JobDescription.id,
                JobDescription.title,
                func.avg(CandidateMatch.semantic_score),
                func.avg(CandidateMatch.overall_score),
            )
            .join(CandidateMatch, CandidateMatch.job_description_id == JobDescription.id)
            .where(
                CandidateMatch.organization_id == auth.organization_id,
                CandidateMatch.owner_id == auth.user_id,
                JobDescription.owner_id == auth.user_id,
            )
            .group_by(JobDescription.id, JobDescription.title)
            .order_by(func.avg(CandidateMatch.semantic_score).desc())
        )
        return [
            {
                "job_id": str(job_id),
                "job_title": title,
                "average_semantic_score": round(float(semantic or 0), 2),
                "average_overall_score": round(float(overall or 0), 2),
            }
            for job_id, title, semantic, overall in rows.all()
        ]

    async def _count(self, auth: AuthContext, model) -> int:
        value = await self.db.scalar(
            select(func.count()).select_from(model).where(model.organization_id == auth.organization_id, model.owner_id == auth.user_id)
        )
        return int(value or 0)
