from uuid import UUID

from sqlalchemy import select

from app.models.domain import JobDescription
from app.repositories.base import BaseRepository


class JobDescriptionRepository(BaseRepository[JobDescription]):
    model = JobDescription

    async def get_for_owner(self, job_id: UUID, organization_id: UUID, owner_id: UUID) -> JobDescription | None:
        result = await self.db.execute(
            select(JobDescription).where(
                JobDescription.id == job_id,
                JobDescription.organization_id == organization_id,
                JobDescription.owner_id == owner_id,
                JobDescription.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_for_org(self, job_id: UUID, organization_id: UUID) -> JobDescription | None:
        result = await self.db.execute(
            select(JobDescription).where(
                JobDescription.id == job_id,
                JobDescription.organization_id == organization_id,
                JobDescription.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_active_for_owner(self, organization_id: UUID, owner_id: UUID, limit: int = 100) -> list[JobDescription]:
        result = await self.db.execute(
            select(JobDescription)
            .where(
                JobDescription.organization_id == organization_id,
                JobDescription.owner_id == owner_id,
                JobDescription.deleted_at.is_(None),
            )
            .order_by(JobDescription.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_active_for_org(self, organization_id: UUID, limit: int = 100) -> list[JobDescription]:
        result = await self.db.execute(
            select(JobDescription)
            .where(JobDescription.organization_id == organization_id, JobDescription.deleted_at.is_(None))
            .order_by(JobDescription.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
