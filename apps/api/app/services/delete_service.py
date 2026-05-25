from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select, update
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


class DeleteWorkflowService:
    def __init__(self, db: AsyncSession, storage: ObjectStorage | None = None) -> None:
        self.db = db
        self.storage = storage or ObjectStorage()

    async def delete_resume(self, resume: Resume) -> None:
        now = datetime.now(timezone.utc)
        point_ids = await self._candidate_point_ids(resume_id=resume.id)
        EmbeddingService().delete_candidate_points(point_ids)
        await self.db.execute(delete(CandidateEmbedding).where(CandidateEmbedding.resume_id == resume.id))
        await self.db.execute(delete(ATSScore).where(ATSScore.resume_id == resume.id))
        await self.db.execute(delete(ResumeProcessingEvent).where(ResumeProcessingEvent.resume_id == resume.id))
        try:
            self.storage.delete_object(resume.storage_key)
        except Exception:
            resume.metadata_json = {**(resume.metadata_json or {}), "delete_file_warning": "storage_delete_failed"}
        resume.deleted_at = now
        await self.db.commit()

    async def delete_candidate(self, candidate: Candidate) -> None:
        now = datetime.now(timezone.utc)
        point_ids = await self._candidate_point_ids(candidate_id=candidate.id)
        resumes = list(
            await self.db.scalars(select(Resume).where(Resume.candidate_id == candidate.id, Resume.deleted_at.is_(None)))
        )
        storage_keys = [resume.storage_key for resume in resumes]
        try:
            await self.db.execute(delete(ATSScore).where(ATSScore.candidate_id == candidate.id))
            await self.db.execute(delete(CandidateMatch).where(CandidateMatch.candidate_id == candidate.id))
            await self.db.execute(delete(CandidatePipelineStage).where(CandidatePipelineStage.candidate_id == candidate.id))
            await self.db.execute(delete(CandidateBookmark).where(CandidateBookmark.candidate_id == candidate.id))
            await self.db.execute(delete(RecruiterNote).where(RecruiterNote.candidate_id == candidate.id))
            await self.db.execute(delete(RankingFeedback).where(RankingFeedback.candidate_id == candidate.id))
            await self.db.execute(delete(CandidateSkill).where(CandidateSkill.candidate_id == candidate.id))
            await self.db.execute(delete(CandidateEmbedding).where(CandidateEmbedding.candidate_id == candidate.id))
            await self.db.execute(
                delete(ResumeProcessingEvent).where(
                    ResumeProcessingEvent.resume_id.in_([resume.id for resume in resumes])
                )
            )
            await self.db.execute(
                update(RecruiterActivity)
                .where(RecruiterActivity.candidate_id == candidate.id)
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
                },
            }
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

        self._delete_candidate_vectors_best_effort(candidate, point_ids)
        self._delete_storage_best_effort(candidate, storage_keys)

    async def delete_job(self, job: JobDescription) -> None:
        point_ids = await self._job_point_ids(job.id)
        EmbeddingService().delete_job_points(point_ids)
        await self.db.execute(delete(JobDescriptionEmbedding).where(JobDescriptionEmbedding.job_description_id == job.id))
        await self.db.execute(delete(ATSScore).where(ATSScore.job_description_id == job.id))
        await self.db.execute(delete(CandidateMatch).where(CandidateMatch.job_description_id == job.id))
        await self.db.execute(delete(CandidatePipelineStage).where(CandidatePipelineStage.job_description_id == job.id))
        await self.db.execute(delete(RankingFeedback).where(RankingFeedback.job_description_id == job.id))
        await self.db.execute(
            update(RecruiterActivity)
            .where(RecruiterActivity.job_description_id == job.id)
            .values(job_description_id=None)
        )
        job.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()

    async def _candidate_point_ids(self, candidate_id: UUID | None = None, resume_id: UUID | None = None) -> list[str]:
        query = select(CandidateEmbedding.qdrant_point_id)
        if candidate_id:
            query = query.where(CandidateEmbedding.candidate_id == candidate_id)
        if resume_id:
            query = query.where(CandidateEmbedding.resume_id == resume_id)
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def _job_point_ids(self, job_id: UUID) -> list[str]:
        result = await self.db.execute(
            select(JobDescriptionEmbedding.qdrant_point_id).where(JobDescriptionEmbedding.job_description_id == job_id)
        )
        return [row[0] for row in result.all()]

    def _delete_candidate_vectors_best_effort(self, candidate: Candidate, point_ids: list[str]) -> None:
        try:
            EmbeddingService().delete_candidate_points(point_ids)
        except Exception as exc:
            candidate.raw_profile = {
                **(candidate.raw_profile or {}),
                "delete_vector_warning": {
                    "status": "qdrant_delete_failed",
                    "point_count": len(point_ids),
                    "error": str(exc),
                },
            }

    def _delete_storage_best_effort(self, candidate: Candidate, storage_keys: list[str]) -> None:
        failures: list[dict] = []
        for key in storage_keys:
            try:
                self.storage.delete_object(key)
            except Exception as exc:
                failures.append({"storage_key": key, "error": str(exc)})
        if failures:
            candidate.raw_profile = {
                **(candidate.raw_profile or {}),
                "delete_storage_warning": failures[:10],
            }
