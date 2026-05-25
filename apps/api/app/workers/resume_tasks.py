import asyncio
from uuid import UUID

from sqlalchemy import delete, select

from app.core.config import settings
from app.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.models.domain import Candidate, CandidateEmbedding, CandidateSkill, Resume, ResumeProcessingEvent, ResumeStatus
from app.services.job_intelligence_service import SKILL_TERMS
from app.services.embedding_service import EmbeddingService
from app.services.storage import ObjectStorage
from app.workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    name="resume.parse",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def parse_resume_task(resume_id: str) -> None:
    asyncio.run(_parse_resume(UUID(resume_id)))


async def _parse_resume(resume_id: UUID) -> None:
    async with AsyncSessionLocal() as db:
        resume = await db.get(Resume, resume_id)
        if resume is None:
            logger.warning("resume_parse_missing", resume_id=str(resume_id))
            return

        resume.status = ResumeStatus.parsing
        db.add(
            ResumeProcessingEvent(
                organization_id=resume.organization_id,
                resume_id=resume.id,
                event_type="resume.parsing_started",
                payload={},
            )
        )
        await db.commit()

        try:
            from app.services.extraction_service import ExtractionService

            payload = ObjectStorage().download_bytes(resume.storage_key)
            parsed = ExtractionService().parse(payload, resume.content_type)
            resume.status = ResumeStatus.parsed
            resume.parser_version = parsed.parser_version
            resume.extracted_text = parsed.text
            resume.metadata_json = {**resume.metadata_json, "parse": parsed.metadata}

            candidate = await _ensure_candidate(db, resume)
            skills = await _extract_candidate_skills(db, resume, candidate)
            await _embed_resume(db, resume, candidate, skills)
            resume.status = ResumeStatus.embedded
            event_type = "resume.embedded"
            event_payload = {"text_length": len(parsed.text), "metadata": parsed.metadata}
        except Exception as exc:
            logger.exception("resume_parse_failed", resume_id=str(resume_id))
            resume.status = ResumeStatus.failed
            resume.parse_error = str(exc)
            event_type = "resume.parse_failed"
            event_payload = {"error": str(exc)}

        db.add(
            ResumeProcessingEvent(
                organization_id=resume.organization_id,
                resume_id=resume.id,
                event_type=event_type,
                payload=event_payload,
            )
        )
        await db.commit()


async def _ensure_candidate(db, resume: Resume) -> Candidate:
    if resume.candidate_id:
        candidate = await db.get(Candidate, resume.candidate_id)
        if candidate is not None:
            return candidate

    candidate = Candidate(
        organization_id=resume.organization_id,
        source="resume_upload",
        raw_profile={"resume_id": str(resume.id)},
    )
    db.add(candidate)
    await db.flush()
    resume.candidate_id = candidate.id
    return candidate


async def _embed_resume(db, resume: Resume, candidate: Candidate, skills: list[str]) -> None:
    if not resume.extracted_text:
        return
    embedding_service = EmbeddingService()
    chunks = embedding_service.chunk_text(resume.extracted_text)
    vectors = embedding_service.embed(chunks)
    await db.execute(delete(CandidateEmbedding).where(CandidateEmbedding.resume_id == resume.id))
    point_ids = embedding_service.upsert_candidate_resume(
        resume.organization_id,
        candidate.id,
        resume.id,
        chunks,
        vectors,
        metadata={
            "skills": skills,
            "full_name": candidate.full_name,
            "headline": candidate.headline,
            "location": candidate.location,
            "education": candidate.raw_profile.get("education"),
        },
    )
    for chunk, point_id in zip(chunks, point_ids, strict=True):
        db.add(
            CandidateEmbedding(
                organization_id=resume.organization_id,
                candidate_id=candidate.id,
                resume_id=resume.id,
                qdrant_point_id=point_id,
                model_name=settings.embedding_model_name,
                vector_size=settings.embedding_vector_size,
                chunk_index=chunk.index,
                chunk_text=chunk.text,
            )
        )


async def _extract_candidate_skills(db, resume: Resume, candidate: Candidate) -> list[str]:
    text = (resume.extracted_text or "").lower()
    skills = sorted({skill for skill in SKILL_TERMS if skill in text})
    await db.execute(delete(CandidateSkill).where(CandidateSkill.candidate_id == candidate.id))
    for skill in skills:
        db.add(
            CandidateSkill(
                organization_id=resume.organization_id,
                candidate_id=candidate.id,
                normalized_skill=skill,
                raw_skill=skill,
                confidence=0.85,
            )
        )
    return skills
