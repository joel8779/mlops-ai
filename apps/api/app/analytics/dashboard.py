"""Dashboard Builder - Build analytics dashboards."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.aggregations import MetricsAggregator, AggregatedMetric
from app.analytics.pipelines import AnalyticsPipeline


@dataclass
class DashboardWidget:
    """Single dashboard widget."""

    widget_type: str  # "metric", "chart", "table", "funnel"
    title: str
    data: Any
    metadata: dict[str, Any]


@dataclass
class Dashboard:
    """Analytics dashboard."""

    name: str
    widgets: list[DashboardWidget]
    timestamp: datetime
    metadata: dict[str, Any]


class DashboardBuilder:
    """Build analytics dashboards."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize dashboard builder.

        Args:
            db: Database session
        """
        self.db = db
        self.pipeline = AnalyticsPipeline(db)
        self.aggregator = MetricsAggregator(db)

    async def build_recruiter_dashboard(
        self,
        organization_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> Dashboard:
        """Build recruiter productivity dashboard.

        Args:
            organization_id: Organization ID
            user_id: Optional user ID

        Returns:
            Dashboard object
        """
        widgets = []

        # Productivity metrics
        productivity = await self.pipeline.compute_recruiter_productivity(
            organization_id=organization_id,
            user_id=user_id,
        )

        for metric in productivity:
            widgets.append(
                DashboardWidget(
                    widget_type="metric",
                    title=metric.name.replace("_", " ").title(),
                    data={
                        "value": metric.value,
                        "timestamp": metric.timestamp.isoformat(),
                    },
                    metadata=metric.metadata,
                )
            )

        # Hiring funnel
        funnel = await self.pipeline.compute_hiring_funnel(organization_id=organization_id)

        widgets.append(
            DashboardWidget(
                widget_type="funnel",
                title="Hiring Funnel",
                data=funnel,
                metadata={},
            )
        )

        # AI ranking accuracy
        accuracy = await self.pipeline.compute_ai_ranking_accuracy(organization_id=organization_id)

        widgets.append(
            DashboardWidget(
                widget_type="metric",
                title="AI Ranking Accuracy",
                data=accuracy,
                metadata={},
            )
        )

        return Dashboard(
            name="Recruiter Dashboard",
            widgets=widgets,
            timestamp=datetime.now(timezone.utc),
            metadata={"organization_id": str(organization_id)},
        )

    async def build_executive_dashboard(
        self,
        organization_id: UUID,
    ) -> Dashboard:
        """Build executive-level dashboard.

        Args:
            organization_id: Organization ID

        Returns:
            Dashboard object
        """
        widgets = []

        # Aggregate metrics by user
        user_metrics = await self.aggregator.aggregate_by_user(organization_id=organization_id)

        widgets.append(
            DashboardWidget(
                widget_type="table",
                title="Recruiter Productivity",
                data={
                    "metrics": [
                        {
                            "user_id": m.dimensions.get("user_id"),
                            "metric": m.name,
                            "value": m.value,
                        }
                        for m in user_metrics
                    ]
                },
                metadata={},
            )
        )

        # Aggregate metrics by job
        job_metrics = await self.aggregator.aggregate_by_job(organization_id=organization_id)

        widgets.append(
            DashboardWidget(
                widget_type="table",
                title="Job Performance",
                data={
                    "metrics": [
                        {
                            "job_id": m.dimensions.get("job_id"),
                            "metric": m.name,
                            "value": m.value,
                        }
                        for m in job_metrics
                    ]
                },
                metadata={},
            )
        )

        # Skill demand trends
        trends = await self.pipeline.compute_skill_demand_trends(organization_id=organization_id)

        widgets.append(
            DashboardWidget(
                widget_type="chart",
                title="Skill Demand Trends",
                data=trends,
                metadata={"chart_type": "bar"},
            )
        )

        return Dashboard(
            name="Executive Dashboard",
            widgets=widgets,
            timestamp=datetime.now(timezone.utc),
            metadata={"organization_id": str(organization_id)},
        )
