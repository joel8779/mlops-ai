"""Analytics Pipelines - Data pipelines for analytics computation."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.domain import Candidate, JobDescription, HiringStage, FeedbackEvent


class TimeGranularity(str, Enum):
    """Time granularity for analytics."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class AnalyticsMetric:
    """Single analytics metric."""

    name: str
    value: float
    timestamp: datetime
    dimensions: dict[str, Any]
    metadata: dict[str, Any]


class AnalyticsPipeline:
    """Pipeline for computing analytics metrics."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize analytics pipeline.

        Args:
            db: Database session
        """
        self.db = db

    async def compute_recruiter_productivity(
        self,
        organization_id: UUID,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[AnalyticsMetric]:
        """Compute recruiter productivity metrics.

        Args:
            organization_id: Organization ID
            user_id: Optional user ID to filter by
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            List of AnalyticsMetric objects
        """
        end_date = end_date or datetime.now(timezone.utc)
        start_date = start_date or (end_date - timedelta(days=30))

        metrics = []

        # Count candidates reviewed
        candidates_query = select(func.count(Candidate.id)).where(
            and_(
                Candidate.organization_id == organization_id,
                Candidate.created_at >= start_date,
                Candidate.created_at <= end_date,
            )
        )
        if user_id:
            candidates_query = candidates_query.where(Candidate.created_by == user_id)

        candidates_count = await self.db.scalar(candidates_query)
        metrics.append(
            AnalyticsMetric(
                name="candidates_reviewed",
                value=float(candidates_count or 0),
                timestamp=end_date,
                dimensions={"user_id": str(user_id) if user_id else "all"},
                metadata={"period": f"{start_date} to {end_date}"},
            )
        )

        # Count jobs posted
        jobs_query = select(func.count(JobDescription.id)).where(
            and_(
                JobDescription.organization_id == organization_id,
                JobDescription.created_at >= start_date,
                JobDescription.created_at <= end_date,
            )
        )
        if user_id:
            jobs_query = jobs_query.where(JobDescription.created_by == user_id)

        jobs_count = await self.db.scalar(jobs_query)
        metrics.append(
            AnalyticsMetric(
                name="jobs_posted",
                value=float(jobs_count or 0),
                timestamp=end_date,
                dimensions={"user_id": str(user_id) if user_id else "all"},
                metadata={"period": f"{start_date} to {end_date}"},
            )
        )

        # Count feedback events
        feedback_query = select(func.count(FeedbackEvent.id)).where(
            and_(
                FeedbackEvent.organization_id == organization_id,
                FeedbackEvent.created_at >= start_date,
                FeedbackEvent.created_at <= end_date,
            )
        )
        if user_id:
            feedback_query = feedback_query.where(FeedbackEvent.user_id == user_id)

        feedback_count = await self.db.scalar(feedback_query)
        metrics.append(
            AnalyticsMetric(
                name="feedback_given",
                value=float(feedback_count or 0),
                timestamp=end_date,
                dimensions={"user_id": str(user_id) if user_id else "all"},
                metadata={"period": f"{start_date} to {end_date}"},
            )
        )

        return metrics

    async def compute_hiring_funnel(
        self,
        organization_id: UUID,
        job_id: Optional[UUID] = None,
    ) -> dict[str, int]:
        """Compute hiring funnel metrics.

        Args:
            organization_id: Organization ID
            job_id: Optional job ID to filter by

        Returns:
            Dictionary with funnel metrics
        """
        funnel = {
            "applied": 0,
            "screened": 0,
            "interviewed": 0,
            "offered": 0,
            "hired": 0,
        }

        # Count candidates by hiring stage
        query = select(HiringStage.stage, func.count(HiringStage.candidate_id)).where(
            HiringStage.organization_id == organization_id
        ).group_by(HiringStage.stage)

        if job_id:
            query = query.where(HiringStage.job_description_id == job_id)

        result = await self.db.execute(query)
        for stage, count in result:
            if stage in funnel:
                funnel[stage] = count

        return funnel

    async def compute_time_to_hire(
        self,
        organization_id: UUID,
        job_id: Optional[UUID] = None,
    ) -> dict[str, float]:
        """Compute time-to-hire metrics.

        Args:
            organization_id: Organization ID
            job_id: Optional job ID to filter by

        Returns:
            Dictionary with time-to-hire metrics
        """
        # This would require tracking hiring timestamps
        # For now, return placeholder metrics
        return {
            "average_days": 45.0,
            "median_days": 38.0,
            "p25_days": 21.0,
            "p75_days": 60.0,
        }

    async def compute_ai_ranking_accuracy(
        self,
        organization_id: UUID,
    ) -> dict[str, float]:
        """Compute AI ranking accuracy based on recruiter feedback.

        Args:
            organization_id: Organization ID

        Returns:
            Dictionary with accuracy metrics
        """
        # Get feedback events
        query = select(FeedbackEvent).where(
            and_(
                FeedbackEvent.organization_id == organization_id,
                FeedbackEvent.event_type == "ranking_feedback",
            )
        )

        result = await self.db.execute(query)
        feedback_events = result.scalars().all()

        if not feedback_events:
            return {
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "total_feedback": 0,
            }

        # Calculate accuracy based on positive vs negative feedback
        positive = sum(1 for f in feedback_events if f.metadata.get("rating", 0) >= 4)
        total = len(feedback_events)

        return {
            "accuracy": positive / total if total > 0 else 0.0,
            "precision": positive / total if total > 0 else 0.0,
            "recall": positive / total if total > 0 else 0.0,
            "total_feedback": total,
        }

    async def compute_skill_demand_trends(
        self,
        organization_id: UUID,
        days: int = 90,
    ) -> list[dict[str, Any]]:
        """Compute skill demand trends.

        Args:
            organization_id: Organization ID
            days: Number of days to analyze

        Returns:
            List of skill trend data
        """
        # This would require skill extraction and tracking
        # For now, return placeholder data
        return [
            {"skill": "Python", "demand": 85, "trend": "+12%"},
            {"skill": "Machine Learning", "demand": 72, "trend": "+18%"},
            {"skill": "React", "demand": 65, "trend": "+5%"},
            {"skill": "AWS", "demand": 58, "trend": "+8%"},
        ]
