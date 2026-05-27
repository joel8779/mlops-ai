from uuid import UUID

from sqlalchemy import func, select

from app.models.domain import CandidateBookmark, CandidatePipelineStage, RecruiterActivity, RecruiterNote
from app.repositories.base import BaseRepository


class WorkflowRepository(BaseRepository[CandidatePipelineStage]):
    model = CandidatePipelineStage

    async def current_stage(
        self,
        organization_id: UUID,
        owner_id: UUID,
        candidate_id: UUID,
        job_description_id: UUID | None,
    ) -> CandidatePipelineStage | None:
        result = await self.db.execute(
            select(CandidatePipelineStage).where(
                CandidatePipelineStage.organization_id == organization_id,
                CandidatePipelineStage.owner_id == owner_id,
                CandidatePipelineStage.candidate_id == candidate_id,
                CandidatePipelineStage.job_description_id == job_description_id,
                CandidatePipelineStage.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def stage_counts(self, organization_id: UUID, owner_id: UUID) -> dict[str, int]:
        result = await self.db.execute(
            select(CandidatePipelineStage.stage, func.count())
            .where(
                CandidatePipelineStage.organization_id == organization_id,
                CandidatePipelineStage.owner_id == owner_id,
            )
            .group_by(CandidatePipelineStage.stage)
        )
        return {str(stage.value): count for stage, count in result.all()}


class RecruiterActivityRepository(BaseRepository[RecruiterActivity]):
    model = RecruiterActivity

    async def timeline(self, organization_id: UUID, owner_id: UUID, limit: int = 50) -> list[RecruiterActivity]:
        result = await self.db.execute(
            select(RecruiterActivity)
            .where(RecruiterActivity.organization_id == organization_id, RecruiterActivity.owner_id == owner_id)
            .order_by(RecruiterActivity.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
