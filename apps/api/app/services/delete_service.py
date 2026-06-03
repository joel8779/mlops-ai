import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import (
    ATSScore,
    Candidate,
    CandidateBookmark,
    CandidateEmbedding,
    CandidateMatch,
    CandidatePipelineStage,
    CandidateSkill,
    JobDescription,
    JobDescriptionEmbedding,
    RankingFeedback,
    RecruiterActivity,
    RecruiterNote,
    Resume,
    ResumeProcessingEvent,
)
from app.services.embedding_service import EmbeddingService
from app.services.storage import ObjectStorage

logger = logging.getLogger(__name__)


class DeleteWorkflowService:
    def __init__(
        self,
        db: AsyncSession,
        storage: ObjectStorage | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.db = db
        self.storage = storage or ObjectStorage()
        self.embedding_service = embedding_service or EmbeddingService()
        self._column_cache: dict[str, set[str]] = {}

    async def delete_resume(self, resume: Resume) -> None:
        now = datetime.now(timezone.utc)
        point_ids = await self._candidate_point_ids(resume.organization_id, resume_id=resume.id)
        self.embedding_service.delete_candidate_points(point_ids)
        await self.db.execute(
            delete(CandidateEmbedding).where(
                CandidateEmbedding.organization_id == resume.organization_id,
                CandidateEmbedding.resume_id == resume.id,
            )
        )
        if await self._table_has_column("ats_scores", "resume_id"):
            await self.db.execute(delete(ATSScore).where(ATSScore.organization_id == resume.organization_id, ATSScore.resume_id == resume.id))
        await self.db.execute(
            delete(ResumeProcessingEvent).where(
                ResumeProcessingEvent.organization_id == resume.organization_id,
                ResumeProcessingEvent.resume_id == resume.id,
            )
        )
        try:
            self.storage.delete_object(resume.storage_key)
        except Exception as exc:
            logger.exception(
                "storage_delete_failed",
                resume_id=str(resume.id),
                storage_key=resume.storage_key,
                error=str(exc),
            )
            resume.metadata_json = {**(resume.metadata_json or {}), "delete_file_warning": "storage_delete_failed", "delete_error": str(exc)}
        resume.deleted_at = now
        await self.db.commit()

    async def delete_candidate(self, candidate: Candidate) -> None:
        now = datetime.now(timezone.utc)
        point_ids = await self._candidate_point_ids(candidate.organization_id, candidate_id=candidate.id)
        resumes = list(
            await self.db.scalars(
                select(Resume).where(
                    Resume.organization_id == candidate.organization_id,
                    Resume.candidate_id == candidate.id,
                    Resume.deleted_at.is_(None),
                )
            )
        )
        storage_keys = [resume.storage_key for resume in resumes]
        resume_ids = [resume.id for resume in resumes]
        try:
            self.embedding_service.delete_candidate_points(point_ids)
            await self._delete_candidate_ats_scores(candidate.organization_id, candidate.id, resume_ids)
            await self.db.execute(
                delete(CandidateMatch).where(
                    CandidateMatch.organization_id == candidate.organization_id,
                    CandidateMatch.candidate_id == candidate.id,
                )
            )
            await self.db.execute(
                delete(CandidatePipelineStage).where(
                    CandidatePipelineStage.organization_id == candidate.organization_id,
                    CandidatePipelineStage.candidate_id == candidate.id,
                )
            )
            await self.db.execute(delete(CandidateBookmark).where(CandidateBookmark.organization_id == candidate.organization_id, CandidateBookmark.candidate_id == candidate.id))
            await self.db.execute(delete(RecruiterNote).where(RecruiterNote.organization_id == candidate.organization_id, RecruiterNote.candidate_id == candidate.id))
            await self.db.execute(delete(RankingFeedback).where(RankingFeedback.organization_id == candidate.organization_id, RankingFeedback.candidate_id == candidate.id))
            await self.db.execute(delete(CandidateSkill).where(CandidateSkill.organization_id == candidate.organization_id, CandidateSkill.candidate_id == candidate.id))
            await self.db.execute(delete(CandidateEmbedding).where(CandidateEmbedding.organization_id == candidate.organization_id, CandidateEmbedding.candidate_id == candidate.id))
            if resume_ids:
                await self.db.execute(
                    delete(ResumeProcessingEvent).where(
                        ResumeProcessingEvent.organization_id == candidate.organization_id,
                        ResumeProcessingEvent.resume_id.in_(resume_ids)
                    )
                )
            await self.db.execute(
                update(RecruiterActivity)
                .where(
                    RecruiterActivity.organization_id == candidate.organization_id,
                    RecruiterActivity.candidate_id == candidate.id,
                )
                .values(candidate_id=None)
            )
            for resume in resumes:
                resume.deleted_at = now
                resume.candidate_id = None
                resume.metadata_json = {
                    **(resume.metadata_json or {}),
                    "candidate_delete": {"candidate_id": str(candidate.id), "deleted_at": now.isoformat()},
                }
            candidate.deleted_at = now
            candidate.raw_profile = {
                **(candidate.raw_profile or {}),
                "delete_workflow": {
                    "status": "db_complete",
                    "resume_count": len(resumes),
                    "candidate_vector_count": len(point_ids),
                    "ats_relations_removed": True,
                    "semantic_index_removed": True,
                },
            }
            await self.db.flush()
            await self.db.commit()
        except Exception as exc:
            logger.exception(
                "candidate_delete_db_failed",
                candidate_id=str(candidate.id),
                resume_count=len(resumes),
                error=str(exc),
            )
            await self.db.rollback()
            raise

        self._delete_storage_best_effort(candidate, storage_keys)

    async def delete_job(self, job: JobDescription) -> None:
        point_ids = await self._job_point_ids(job.organization_id, job.id)
        self.embedding_service.delete_job_points(point_ids)
        await self.db.execute(
            delete(JobDescriptionEmbedding).where(
                JobDescriptionEmbedding.organization_id == job.organization_id,
                JobDescriptionEmbedding.job_description_id == job.id,
            )
        )
        if await self._table_has_column("ats_scores", "job_description_id"):
            await self.db.execute(delete(ATSScore).where(ATSScore.organization_id == job.organization_id, ATSScore.job_description_id == job.id))
        await self.db.execute(delete(CandidateMatch).where(CandidateMatch.organization_id == job.organization_id, CandidateMatch.job_description_id == job.id))
        await self.db.execute(delete(CandidatePipelineStage).where(CandidatePipelineStage.organization_id == job.organization_id, CandidatePipelineStage.job_description_id == job.id))
        await self.db.execute(delete(RankingFeedback).where(RankingFeedback.organization_id == job.organization_id, RankingFeedback.job_description_id == job.id))
        await self.db.execute(
            update(RecruiterActivity)
            .where(
                RecruiterActivity.organization_id == job.organization_id,
                RecruiterActivity.job_description_id == job.id,
            )
            .values(job_description_id=None)
        )
        job.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()

    async def _candidate_point_ids(
        self,
        organization_id: UUID,
        candidate_id: UUID | None = None,
        resume_id: UUID | None = None,
    ) -> list[str]:
        query = select(CandidateEmbedding.qdrant_point_id).where(CandidateEmbedding.organization_id == organization_id)
        if candidate_id:
            query = query.where(CandidateEmbedding.candidate_id == candidate_id)
        if resume_id:
            query = query.where(CandidateEmbedding.resume_id == resume_id)
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def _job_point_ids(self, organization_id: UUID, job_id: UUID) -> list[str]:
        result = await self.db.execute(
            select(JobDescriptionEmbedding.qdrant_point_id).where(
                JobDescriptionEmbedding.organization_id == organization_id,
                JobDescriptionEmbedding.job_description_id == job_id,
            )
        )
        return [row[0] for row in result.all()]

    async def _delete_candidate_ats_scores(self, organization_id: UUID, candidate_id: UUID, resume_ids: list[UUID]) -> None:
        if await self._table_has_column("ats_scores", "candidate_id"):
            await self.db.execute(delete(ATSScore).where(ATSScore.organization_id == organization_id, ATSScore.candidate_id == candidate_id))
        if resume_ids and await self._table_has_column("ats_scores", "resume_id"):
            await self.db.execute(delete(ATSScore).where(ATSScore.organization_id == organization_id, ATSScore.resume_id.in_(resume_ids)))

    async def _table_has_column(self, table_name: str, column_name: str) -> bool:
        bind = self.db.get_bind()
        if bind is not None and bind.dialect.name != "postgresql":
            table = Candidate.__table__.metadata.tables.get(table_name)
            return table is None or column_name in table.columns
        if table_name not in self._column_cache:
            result = await self.db.execute(
                text(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = :table_name
                    """
                ),
                {"table_name": table_name},
            )
            self._column_cache[table_name] = {str(row[0]) for row in result.all()}
        return column_name in self._column_cache[table_name]

    def _delete_storage_best_effort(self, candidate: Candidate, storage_keys: list[str]) -> None:
        failures: list[dict] = []
        for key in storage_keys:
            try:
                self.storage.delete_object(key)
            except Exception as exc:
                failures.append({"storage_key": key, "error": str(exc)})
        if failures:
            logger.warning(
                "Candidate storage cleanup failed",
                extra={"candidate_id": str(candidate.id), "failures": failures[:10]},
            )
