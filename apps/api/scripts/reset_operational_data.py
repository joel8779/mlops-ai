"""Clear recruiter-generated operational data without deleting auth users.

This intentionally leaves organizations, users, tenant quotas, API keys, and
schema migrations intact. It also clears Qdrant collections used by recruiter
search so old global vector payloads cannot leak after owner isolation.
"""

from __future__ import annotations

import asyncio

from qdrant_client import QdrantClient
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine
from app.services.storage import ObjectStorage


OPERATIONAL_TABLES = [
    "resume_processing_events",
    "ats_scores",
    "ranking_feedback",
    "candidate_matches",
    "candidate_bookmarks",
    "candidate_pipeline_stages",
    "recruiter_notes",
    "candidate_skills",
    "candidate_embeddings",
    "job_description_embeddings",
    "recruiter_activities",
    "analytics_snapshots",
    "llm_usage_logs",
    "resumes",
    "job_descriptions",
    "candidates",
]


async def reset_postgres() -> None:
    async with engine.begin() as connection:
        for table_name in OPERATIONAL_TABLES:
            await connection.execute(text(f"DELETE FROM {table_name}"))


def reset_qdrant() -> None:
    client = QdrantClient(
        url=str(settings.qdrant_url),
        api_key=settings.qdrant_api_key,
        timeout=settings.qdrant_timeout_seconds,
    )
    existing = {collection.name for collection in client.get_collections().collections}
    for collection_name in [
        settings.qdrant_collection,
        settings.qdrant_job_collection,
        settings.qdrant_memory_collection,
        settings.qdrant_recommendation_collection,
    ]:
        if collection_name in existing:
            client.delete_collection(collection_name=collection_name)


def reset_uploaded_documents() -> None:
    storage = ObjectStorage()
    paginator = storage._client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=settings.s3_bucket, Prefix="organizations/"):
        objects = [{"Key": item["Key"]} for item in page.get("Contents", [])]
        if objects:
            storage._client.delete_objects(Bucket=settings.s3_bucket, Delete={"Objects": objects})


async def main() -> None:
    await reset_postgres()
    reset_qdrant()
    reset_uploaded_documents()
    print("Operational recruiter data, Qdrant collections, and uploaded documents cleared.")


if __name__ == "__main__":
    asyncio.run(main())
