from uuid import UUID

from sqlalchemy import select

from app.models.domain import Candidate, CandidateSkill, Resume
from app.repositories.base import BaseRepository


class CandidateRepository(BaseRepository[Candidate]):
    model = Candidate

    async def get_for_owner(self, candidate_id: UUID, organization_id: UUID, owner_id: UUID) -> Candidate | None:
        result = await self.db.execute(
            select(Candidate).where(
                Candidate.id == candidate_id,
                Candidate.organization_id == organization_id,
                Candidate.owner_id == owner_id,
                Candidate.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_for_org(self, candidate_id: UUID, organization_id: UUID) -> Candidate | None:
        result = await self.db.execute(
            select(Candidate).where(
                Candidate.id == candidate_id,
                Candidate.organization_id == organization_id,
                Candidate.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_for_owner(self, organization_id: UUID, owner_id: UUID, limit: int = 100) -> list[Candidate]:
        result = await self.db.execute(
            select(Candidate)
            .where(
                Candidate.organization_id == organization_id,
                Candidate.owner_id == owner_id,
                Candidate.deleted_at.is_(None),
            )
            .order_by(Candidate.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_for_org(self, organization_id: UUID, limit: int = 100) -> list[Candidate]:
        result = await self.db.execute(
            select(Candidate)
            .where(Candidate.organization_id == organization_id, Candidate.deleted_at.is_(None))
            .order_by(Candidate.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def skills_for_candidate(
        self,
        candidate_id: UUID,
        organization_id: UUID | None = None,
        owner_id: UUID | None = None,
    ) -> list[str]:
        query = select(CandidateSkill.normalized_skill).where(CandidateSkill.candidate_id == candidate_id)
        if organization_id is not None:
            query = query.where(CandidateSkill.organization_id == organization_id)
        if owner_id is not None:
            query = query.where(CandidateSkill.owner_id == owner_id)
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def latest_resume(
        self,
        candidate_id: UUID,
        organization_id: UUID | None = None,
        owner_id: UUID | None = None,
    ) -> Resume | None:
        query = select(Resume).where(Resume.candidate_id == candidate_id, Resume.deleted_at.is_(None))
        if organization_id is not None:
            query = query.where(Resume.organization_id == organization_id)
        if owner_id is not None:
            query = query.where(Resume.owner_id == owner_id)
        result = await self.db.execute(
            query
            .order_by(Resume.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
