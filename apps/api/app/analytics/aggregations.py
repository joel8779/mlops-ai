"""Metrics Aggregator - Aggregate metrics across dimensions."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.pipelines import AnalyticsPipeline, AnalyticsMetric


@dataclass
class AggregatedMetric:
    """Aggregated metric across dimensions."""

    name: str
    value: float
    dimensions: dict[str, Any]
    timestamp: datetime
    comparison_value: Optional[float] = None
    comparison_period: Optional[str] = None


class MetricsAggregator:
    """Aggregate metrics across different dimensions."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize metrics aggregator.

        Args:
            db: Database session
        """
        self.db = db
        self.pipeline = AnalyticsPipeline(db)

    async def aggregate_by_user(
        self,
        organization_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[AggregatedMetric]:
        """Aggregate metrics by user.

        Args:
            organization_id: Organization ID
            start_date: Start date
            end_date: End date

        Returns:
            List of aggregated metrics by user
        """
        # Get all users in organization
        from app.models.domain import User
        from sqlalchemy import and_

        query = select(User.id).where(
            and_(
                User.organization_id == organization_id,
                User.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        user_ids = result.scalars().all()

        aggregated = []
        for user_id in user_ids:
            metrics = await self.pipeline.compute_recruiter_productivity(
                organization_id=organization_id,
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
            )

            for metric in metrics:
                aggregated.append(
                    AggregatedMetric(
                        name=metric.name,
                        value=metric.value,
                        dimensions={**metric.dimensions, "user_id": str(user_id)},
                        timestamp=metric.timestamp,
                    )
                )

        return aggregated

    async def aggregate_by_job(
        self,
        organization_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[AggregatedMetric]:
        """Aggregate metrics by job.

        Args:
            organization_id: Organization ID
            start_date: Start date
            end_date: End date

        Returns:
            List of aggregated metrics by job
        """
        # Get all jobs in organization
        from app.models.domain import JobDescription
        from sqlalchemy import and_

        query = select(JobDescription.id).where(
            and_(
                JobDescription.organization_id == organization_id,
                JobDescription.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        job_ids = result.scalars().all()

        aggregated = []
        for job_id in job_ids:
            funnel = await self.pipeline.compute_hiring_funnel(
                organization_id=organization_id,
                job_id=job_id,
            )

            for stage, count in funnel.items():
                aggregated.append(
                    AggregatedMetric(
                        name=f"funnel_{stage}",
                        value=float(count),
                        dimensions={"job_id": str(job_id)},
                        timestamp=datetime.now(timezone.utc),
                    )
                )

        return aggregated

    async def aggregate_with_comparison(
        self,
        organization_id: UUID,
        current_period_start: datetime,
        current_period_end: datetime,
        comparison_period_days: int = 30,
    ) -> list[AggregatedMetric]:
        """Aggregate metrics with period-over-period comparison.

        Args:
            organization_id: Organization ID
            current_period_start: Current period start
            current_period_end: Current period end
            comparison_period_days: Number of days for comparison period

        Returns:
            List of aggregated metrics with comparisons
        """
        # Compute current period metrics
        current_metrics = await self.pipeline.compute_recruiter_productivity(
            organization_id=organization_id,
            start_date=current_period_start,
            end_date=current_period_end,
        )

        # Compute comparison period metrics
        comparison_start = current_period_start - timedelta(days=comparison_period_days)
        comparison_end = current_period_end - timedelta(days=comparison_period_days)

        comparison_metrics = await self.pipeline.compute_recruiter_productivity(
            organization_id=organization_id,
            start_date=comparison_start,
            end_date=comparison_end,
        )

        # Create comparison map
        comparison_map = {m.name: m.value for m in comparison_metrics}

        # Build aggregated metrics with comparison
        aggregated = []
        for metric in current_metrics:
            comparison_value = comparison_map.get(metric.name)
            aggregated.append(
                AggregatedMetric(
                    name=metric.name,
                    value=metric.value,
                    dimensions=metric.dimensions,
                    timestamp=metric.timestamp,
                    comparison_value=comparison_value,
                    comparison_period=f"{comparison_start} to {comparison_end}",
                )
            )

        return aggregated
