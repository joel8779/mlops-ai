from uuid import UUID

from sqlalchemy import select

from app.models.domain import Resume
from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository[Resume]):
    model = Resume

    async def get_for_org(self, resume_id: UUID, organization_id: UUID) -> Resume | None:
        result = await self.db.execute(
            select(Resume).where(
                Resume.id == resume_id,
                Resume.organization_id == organization_id,
                Resume.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()
