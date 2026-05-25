import asyncio
from time import perf_counter
from uuid import UUID

from sqlalchemy import delete, select

from app.core.config import settings
from app.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.models.domain import Candidate, CandidateEmbedding, CandidatePipelineStage, CandidateSkill, PipelineStage, Resume, ResumeProcessingEvent, ResumeStatus
from app.services.candidate_extraction_service import CandidateExtraction, CandidateExtractionService
from app.services.job_intelligence_service import SKILL_TERMS
from app.services.embedding_service import EmbeddingService
from app.services.pipeline_trace import PipelineTrace, classify_pipeline_error
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
        trace = PipelineTrace(db, resume.organization_id, resume.id)
        current_stage = "pipeline"
        started = perf_counter()

        try:
            from app.services.extraction_service import ExtractionService

            current_stage = "storage_download"
            started = perf_counter()
            payload = ObjectStorage().download_bytes(resume.storage_key)
            await trace.success("storage_download", started, {"bytes": len(payload), "storage_key": resume.storage_key})

            current_stage = "document_extraction"
            started = perf_counter()
            parsed = ExtractionService().parse(payload, resume.content_type)
            await trace.success(
                "document_extraction",
                started,
                {"text_length": len(parsed.text), "parser_version": parsed.parser_version, "metadata": parsed.metadata},
            )
            resume.status = ResumeStatus.parsed
            resume.parser_version = parsed.parser_version
            resume.extracted_text = parsed.text
            resume.metadata_json = {**resume.metadata_json, "parse": parsed.metadata}

            current_stage = "candidate_extraction"
            started = perf_counter()
            candidate = await _ensure_candidate(db, resume)
            extraction = await CandidateExtractionService().extract(parsed.text, resume.original_filename, parsed.metadata)
            _hydrate_candidate(candidate, resume, extraction)
            await trace.success(
                "candidate_extraction",
                started,
                {
                    "candidate_id": str(candidate.id),
                    "source": extraction.source,
                    "name": candidate.full_name,
                    "email_present": bool(candidate.email),
                    "skill_count": len(extraction.skills),
                    "education_count": len(extraction.education),
                    "experience_count": len(extraction.experience),
                    "project_count": len(extraction.projects),
                },
            )

            current_stage = "skill_persistence"
            started = perf_counter()
            skills = await _extract_candidate_skills(db, resume, candidate, extraction.skills)
            await trace.success("skill_persistence", started, {"candidate_id": str(candidate.id), "skill_count": len(skills)})

            current_stage = "embedding_indexing"
            started = perf_counter()
            indexed_count = await _embed_resume(db, resume, candidate, skills)
            await trace.success(
                "embedding_indexing",
                started,
                {"candidate_id": str(candidate.id), "resume_id": str(resume.id), "point_count": indexed_count},
            )
            await _ensure_uploaded_stage(db, resume, candidate)
            resume.status = ResumeStatus.embedded
            event_type = "resume.embedded"
            event_payload = {"text_length": len(parsed.text), "metadata": parsed.metadata}
        except Exception as exc:
            logger.exception("resume_parse_failed", resume_id=str(resume_id))
            await db.rollback()
            resume = await db.get(Resume, resume_id)
            if resume is None:
                return
            trace = PipelineTrace(db, resume.organization_id, resume.id)
            await trace.failure(current_stage, started, exc)
            resume.status = ResumeStatus.failed
            resume.parse_error = classify_pipeline_error(current_stage, exc)["message"]
            resume.metadata_json = {
                **(resume.metadata_json or {}),
                "last_failure": classify_pipeline_error(current_stage, exc),
                "exception_type": type(exc).__name__,
            }
            event_type = "resume.parse_failed"
            event_payload = {
                "error": classify_pipeline_error(current_stage, exc),
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            }

        try:
            current_stage = "db_persistence"
            started = perf_counter()
            db.add(
                ResumeProcessingEvent(
                    organization_id=resume.organization_id,
                    resume_id=resume.id,
                    event_type=event_type,
                    payload=event_payload,
                )
            )
            await trace.success("db_persistence", started, {"final_event_type": event_type, "resume_status": resume.status.value})
            await db.commit()
        except Exception as exc:
            logger.exception("resume_db_persistence_failed", resume_id=str(resume_id), stage=current_stage)
            await db.rollback()
            resume = await db.get(Resume, resume_id)
            if resume is not None:
                resume.status = ResumeStatus.failed
                resume.parse_error = classify_pipeline_error("db_persistence", exc)["message"]
                resume.metadata_json = {
                    **(resume.metadata_json or {}),
                    "last_failure": {
                        **classify_pipeline_error("db_persistence", exc),
                        "transaction_stage": current_stage,
                    },
                    "exception_type": type(exc).__name__,
                }
                db.add(
                    ResumeProcessingEvent(
                        organization_id=resume.organization_id,
                        resume_id=resume.id,
                        event_type="resume.db_persistence.failure",
                        payload={
                            "stage": "db_persistence",
                            "status": "failure",
                            "error": classify_pipeline_error("db_persistence", exc),
                            "exception_type": type(exc).__name__,
                            "exception_message": str(exc),
                        },
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


def _hydrate_candidate(candidate: Candidate, resume: Resume, extraction: CandidateExtraction) -> None:
    if not candidate.full_name or candidate.full_name == "Candidate Profile" or extraction.full_name != "Candidate Profile":
        candidate.full_name = extraction.full_name
    candidate.email = candidate.email or extraction.email
    candidate.phone = candidate.phone or extraction.phone
    candidate.summary = extraction.summary or candidate.summary
    candidate.headline = candidate.headline or _headline(extraction)
    candidate.raw_profile = {
        **(candidate.raw_profile or {}),
        "resume_id": str(resume.id),
        "extraction_source": extraction.source,
        "education": extraction.education,
        "experience": extraction.experience,
        "projects": extraction.projects,
        "inferred_seniority": extraction.inferred_seniority,
        "skills": extraction.skills,
        "warnings": extraction.warnings,
        "raw_extraction": extraction.raw,
    }


def _headline(extraction: CandidateExtraction) -> str | None:
    if extraction.inferred_seniority and extraction.skills:
        return f"{extraction.inferred_seniority.title()} candidate with {', '.join(extraction.skills[:3])}"
    if extraction.skills:
        return f"Candidate with {', '.join(extraction.skills[:3])}"
    return None


async def _embed_resume(db, resume: Resume, candidate: Candidate, skills: list[str]) -> int:
    if not resume.extracted_text:
        return 0
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
    return len(point_ids)


async def _extract_candidate_skills(db, resume: Resume, candidate: Candidate, extracted_skills: list[str] | None = None) -> list[str]:
    text = (resume.extracted_text or "").lower()
    skills = sorted({*(extracted_skills or []), *{skill for skill in SKILL_TERMS if skill in text}})
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


async def _ensure_uploaded_stage(db, resume: Resume, candidate: Candidate) -> None:
    existing = await db.scalar(
        select(CandidatePipelineStage).where(
            CandidatePipelineStage.organization_id == resume.organization_id,
            CandidatePipelineStage.candidate_id == candidate.id,
            CandidatePipelineStage.job_description_id.is_(None),
            CandidatePipelineStage.deleted_at.is_(None),
        )
    )
    if existing is None:
        db.add(
            CandidatePipelineStage(
                organization_id=resume.organization_id,
                candidate_id=candidate.id,
                job_description_id=None,
                stage=PipelineStage.uploaded,
                position=0,
                metadata_json={"source": "resume_ingestion", "resume_id": str(resume.id)},
            )
        )
