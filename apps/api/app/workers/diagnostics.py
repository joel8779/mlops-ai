"""Low-risk Celery tasks for worker runtime validation."""

from __future__ import annotations

import asyncio
from uuid import uuid4

from sqlalchemy import text

from app.db.session import AsyncSessionLocal
from app.core.config import settings
from app.services.embedding_service import EmbeddingService, TextChunk
from app.workers.celery_app import celery_app


@celery_app.task(name="worker.ping")
def ping_task(payload: dict | None = None) -> dict:
    """Return a small payload to prove broker, worker, and result backend work."""
    return {"ok": True, "payload": payload or {}}


@celery_app.task(name="worker.expected_failure")
def expected_failure_task() -> None:
    """Raise a predictable exception for failure-path validation."""
    raise RuntimeError("phase24_expected_worker_failure")


@celery_app.task(name="worker.db_probe")
def db_probe_task() -> dict:
    """Validate worker-side database update capability using a temp table."""
    return asyncio.run(_db_probe())


async def _db_probe() -> dict:
    probe_id = str(uuid4())
    async with AsyncSessionLocal() as db:
        await db.execute(
            text(
                "CREATE TEMP TABLE IF NOT EXISTS phase24_worker_probe "
                "(id text primary key, status text not null) ON COMMIT PRESERVE ROWS"
            )
        )
        await db.execute(
            text("INSERT INTO phase24_worker_probe (id, status) VALUES (:id, :status)"),
            {"id": probe_id, "status": "updated"},
        )
        result = await db.execute(
            text("SELECT status FROM phase24_worker_probe WHERE id = :id"),
            {"id": probe_id},
        )
        await db.commit()
    return {"ok": result.scalar_one() == "updated", "probe_id": probe_id}


@celery_app.task(name="worker.embedding_qdrant_probe")
def embedding_qdrant_probe_task() -> dict:
    """Validate worker-side embedding generation and Qdrant vector insertion."""
    service = EmbeddingService()
    chunks = [TextChunk(index=0, text="distributed worker semantic indexing validation")]
    vectors = service.embed(chunks)
    organization_id = uuid4()
    candidate_id = uuid4()
    resume_id = uuid4()
    point_ids = service.upsert_candidate_resume(
        organization_id=organization_id,
        candidate_id=candidate_id,
        resume_id=resume_id,
        chunks=chunks,
        vectors=vectors,
        metadata={"phase": "24.3", "skills": ["python", "celery"]},
    )
    hits = service.candidate_search(organization_id, "python celery worker", limit=1)
    return {
        "ok": bool(point_ids and hits),
        "vector_size": len(vectors[0]) if vectors else 0,
        "point_count": len(point_ids),
        "hit_count": len(hits),
        "collection": settings.qdrant_collection,
    }
