from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from qdrant_client import QdrantClient
from sqlalchemy import desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.core.config import settings
from app.core.ocr_capabilities import check_binary
from app.db.session import get_db
from app.models.domain import (
    ATSScore,
    CandidateBookmark,
    CandidateEmbedding,
    CandidateMatch,
    CandidatePipelineStage,
    CandidateSkill,
    JobDescriptionEmbedding,
    RankingFeedback,
    RecruiterActivity,
    RecruiterNote,
    Resume,
    ResumeProcessingEvent,
    ResumeStatus,
)
from app.schemas.auth import AuthContext
from app.services.embedding_service import EmbeddingService
from app.workers.celery_app import celery_app
from uuid import UUID

router = APIRouter()


@router.get("/runtime")
async def runtime_diagnostics(auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "worker": await _worker_status(),
        "database": await _database_status(db),
        "ocr": _ocr_status(),
        "gemini": _gemini_status(),
        "embedding": _embedding_status(),
        "qdrant": _qdrant_status(),
        "resume_pipeline": await _resume_pipeline_status(auth, db),
        "ats": await _ats_status(auth, db),
    }


@router.get("/qdrant")
async def qdrant_validation(auth: AuthContext = Depends(get_current_auth)):
    try:
        client = QdrantClient(url=str(settings.qdrant_url), api_key=settings.qdrant_api_key, timeout=5)
        candidate_points, _ = client.scroll(
            collection_name=settings.qdrant_collection,
            scroll_filter=None,
            limit=25,
            with_payload=True,
            with_vectors=False,
        )
        job_points, _ = client.scroll(
            collection_name=settings.qdrant_job_collection,
            scroll_filter=None,
            limit=25,
            with_payload=True,
            with_vectors=False,
        )
        org_id = str(auth.organization_id)
        candidate_payloads = [point.payload or {} for point in candidate_points if (point.payload or {}).get("organization_id") == org_id]
        job_payloads = [point.payload or {} for point in job_points if (point.payload or {}).get("organization_id") == org_id]
        return {
            "status": "healthy",
            "candidate_collection": settings.qdrant_collection,
            "job_collection": settings.qdrant_job_collection,
            "candidate_payload_sample_count": len(candidate_payloads),
            "job_payload_sample_count": len(job_payloads),
            "candidate_payload_contract": _payload_contract(candidate_payloads, ["organization_id", "candidate_id", "resume_id", "chunk_index", "text", "model"]),
            "job_payload_contract": _payload_contract(job_payloads, ["organization_id", "job_description_id", "job_id", "chunk_index", "text", "model"]),
        }
    except Exception as exc:
        return {"status": "unavailable", "error": str(exc)}


@router.get("/candidates/{candidate_id}/relations")
async def candidate_relation_audit(
    candidate_id: UUID,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    filters = {"organization_id": auth.organization_id, "candidate_id": candidate_id}
    return {
        "candidate_id": str(candidate_id),
        "resumes": await _count_model(db, Resume, filters),
        "candidate_embeddings": await _count_model(db, CandidateEmbedding, filters),
        "candidate_skills": await _count_model(db, CandidateSkill, filters),
        "candidate_matches": await _count_model(db, CandidateMatch, filters),
        "ats_scores": await _count_model(db, ATSScore, filters),
        "pipeline_stages": await _count_model(db, CandidatePipelineStage, filters),
        "ranking_feedback": await _count_model(db, RankingFeedback, filters),
        "bookmarks": await _count_model(db, CandidateBookmark, filters),
        "notes": await _count_model(db, RecruiterNote, filters),
        "activities": await _count_model(db, RecruiterActivity, filters),
    }


async def _worker_status() -> dict:
    try:
        inspector = celery_app.control.inspect(timeout=1.0)
        active = inspector.active() or {}
        stats = inspector.stats() or {}
        return {"status": "healthy" if stats else "unavailable", "workers": list(stats.keys()), "active_tasks": active}
    except Exception as exc:
        return {"status": "unavailable", "error": str(exc)}


def _payload_contract(payloads: list[dict], required: list[str]) -> dict:
    missing = {field: 0 for field in required}
    for payload in payloads:
        for field in required:
            if payload.get(field) in (None, ""):
                missing[field] += 1
    return {
        "required_fields": required,
        "sample_count": len(payloads),
        "missing_counts": missing,
        "valid": bool(payloads) and all(count == 0 for count in missing.values()),
    }


async def _database_status(db: AsyncSession) -> dict:
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}


async def _count_model(db: AsyncSession, model, filters: dict) -> int:
    clauses = [getattr(model, key) == value for key, value in filters.items()]
    if hasattr(model, "deleted_at"):
        clauses.append(model.deleted_at.is_(None))
    return int(await db.scalar(select(func.count()).select_from(model).where(*clauses)) or 0)


def _ocr_status() -> dict:
    tesseract = check_binary("tesseract")
    return {"status": "healthy" if tesseract.available else "unavailable", "tesseract": vars(tesseract)}


def _gemini_status() -> dict:
    return {
        "status": "configured" if settings.gemini_api_key else "disabled",
        "model": settings.gemini_model,
        "provider": settings.llm_provider,
    }


def _embedding_status() -> dict:
    try:
        available = EmbeddingService.model_available()
        return {"status": "healthy" if available else "unavailable", "model": settings.embedding_model_name}
    except Exception as exc:
        return {"status": "unavailable", "model": settings.embedding_model_name, "error": str(exc)}


def _qdrant_status() -> dict:
    try:
        client = QdrantClient(url=str(settings.qdrant_url), api_key=settings.qdrant_api_key, timeout=3)
        collections = {collection.name for collection in client.get_collections().collections}
        counts = {}
        for collection in [settings.qdrant_collection, settings.qdrant_job_collection]:
            if collection in collections:
                counts[collection] = client.count(collection_name=collection, exact=True).count
        return {"status": "healthy", "collections": sorted(collections), "counts": counts}
    except Exception as exc:
        return {"status": "unavailable", "error": str(exc)}


async def _resume_pipeline_status(auth: AuthContext, db: AsyncSession) -> dict:
    status_rows = await db.execute(
        select(Resume.status, func.count())
        .where(Resume.organization_id == auth.organization_id, Resume.deleted_at.is_(None))
        .group_by(Resume.status)
    )
    events = await db.execute(
        select(ResumeProcessingEvent)
        .where(ResumeProcessingEvent.organization_id == auth.organization_id)
        .order_by(desc(ResumeProcessingEvent.created_at))
        .limit(20)
    )
    counts = {status.value: int(count) for status, count in status_rows.all()}
    return {
        "status_counts": {status.value: counts.get(status.value, 0) for status in ResumeStatus},
        "recent_events": [
            {
                "resume_id": str(event.resume_id),
                "event_type": event.event_type,
                "payload": event.payload,
                "created_at": event.created_at.isoformat() if event.created_at else None,
            }
            for event in events.scalars().all()
        ],
    }


async def _ats_status(auth: AuthContext, db: AsyncSession) -> dict:
    candidate_vectors = await db.scalar(
        select(func.count()).select_from(CandidateEmbedding).where(CandidateEmbedding.organization_id == auth.organization_id)
    )
    job_vectors = await db.scalar(
        select(func.count()).select_from(JobDescriptionEmbedding).where(JobDescriptionEmbedding.organization_id == auth.organization_id)
    )
    ats_scores = await db.scalar(select(func.count()).select_from(ATSScore).where(ATSScore.organization_id == auth.organization_id))
    return {
        "candidate_embedding_rows": int(candidate_vectors or 0),
        "job_embedding_rows": int(job_vectors or 0),
        "ats_scores": int(ats_scores or 0),
    }
