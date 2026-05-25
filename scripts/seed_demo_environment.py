"""Seed a recruiter-ready SaaS demo environment.

This script is intentionally isolated from API startup. It creates deterministic
demo organizations, recruiters, jobs, candidates, resumes, ranking feedback, and
pipeline state. Vector indexing is attempted by default and degrades gracefully.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from hashlib import sha256
from pathlib import Path

from sqlalchemy import delete, select


ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "apps" / "api"
sys.path.insert(0, str(API_DIR))
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("OTEL_ENABLED", "false")
os.environ.setdefault("EMBEDDING_LOCAL_FILES_ONLY", "true")

from app.core.security import hash_password  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402
from app.models.domain import (  # noqa: E402
    ATSScore,
    Candidate,
    CandidateBookmark,
    CandidateEmbedding,
    CandidateMatch,
    CandidatePipelineStage,
    CandidateSkill,
    FeedbackAction,
    JobDescription,
    JobDescriptionEmbedding,
    Organization,
    PipelineStage,
    RankingFeedback,
    RecruiterActivity,
    RecruiterNote,
    Resume,
    ResumeProcessingEvent,
    ResumeStatus,
    User,
)
from app.core.config import settings  # noqa: E402


DEMO_PASSWORD = "demo12345"
DEMO_ORGS = [
    {"name": "Northstar Talent Labs", "slug": "northstar-talent-labs"},
    {"name": "HelioCloud Systems", "slug": "heliocloud-systems"},
]
DEMO_RECRUITERS = [
    {"email": "sarah@northstar.demo", "full_name": "Sarah Chen", "roles": ["admin"], "org": "northstar-talent-labs"},
    {"email": "mike@northstar.demo", "full_name": "Mike Johnson", "roles": ["recruiter"], "org": "northstar-talent-labs"},
    {"email": "priya@heliocloud.demo", "full_name": "Priya Raman", "roles": ["admin"], "org": "heliocloud-systems"},
]
DEMO_JOBS = [
    {
        "title": "Senior Machine Learning Engineer",
        "description": "Build production ML systems for matching, ranking, and recommendation workflows. Requires Python, PyTorch, MLOps, Kubernetes, and strong product judgment.",
        "role_category": "machine_learning",
        "required_skills": ["python", "pytorch", "mlops", "kubernetes"],
        "optional_skills": ["qdrant", "prefect", "redis"],
        "keywords": ["ranking", "recommendations", "embeddings"],
    },
    {
        "title": "Staff Backend Platform Engineer",
        "description": "Own API reliability, async workers, PostgreSQL data models, Redis queues, observability, and secure multi-tenant backend foundations.",
        "role_category": "backend",
        "required_skills": ["fastapi", "postgresql", "redis", "docker"],
        "optional_skills": ["celery", "prometheus", "grafana"],
        "keywords": ["platform", "reliability", "multi-tenant"],
    },
    {
        "title": "Frontend Product Engineer",
        "description": "Create a polished recruiter workflow in Next.js with fast dashboards, resilient loading states, and accessible SaaS interaction patterns.",
        "role_category": "frontend",
        "required_skills": ["react", "typescript", "next.js", "tailwind"],
        "optional_skills": ["design systems", "analytics"],
        "keywords": ["recruiter workflow", "dashboard", "ux"],
    },
]
DEMO_CANDIDATES = [
    {
        "full_name": "James Rodriguez",
        "email": "james.rodriguez@example.com",
        "headline": "Senior ML Engineer | Ranking and NLP",
        "location": "San Francisco, CA",
        "stage": PipelineStage.technical_round,
        "skills": ["python", "pytorch", "mlops", "kubernetes", "docker", "redis"],
        "summary": "Built recommendation systems, document classifiers, and production MLOps pipelines for high-scale AI products.",
    },
    {
        "full_name": "Emily Zhang",
        "email": "emily.zhang@example.com",
        "headline": "Full Stack Engineer | React and Platform APIs",
        "location": "New York, NY",
        "stage": PipelineStage.interview,
        "skills": ["react", "typescript", "next.js", "fastapi", "postgresql", "redis"],
        "summary": "Ships polished SaaS dashboards backed by reliable APIs and strong product iteration habits.",
    },
    {
        "full_name": "David Kim",
        "email": "david.kim@example.com",
        "headline": "DevOps Engineer | Kubernetes and Observability",
        "location": "Austin, TX",
        "stage": PipelineStage.screening,
        "skills": ["kubernetes", "docker", "terraform", "prometheus", "grafana", "aws"],
        "summary": "Runs production infrastructure with strong CI/CD, incident response, and cost-control experience.",
    },
    {
        "full_name": "Sophia Martinez",
        "email": "sophia.martinez@example.com",
        "headline": "ML Engineer | Computer Vision and NLP",
        "location": "Seattle, WA",
        "stage": PipelineStage.final_round,
        "skills": ["python", "tensorflow", "pytorch", "nlp", "computer vision", "aws"],
        "summary": "Turns research prototypes into observable batch and online inference services.",
    },
    {
        "full_name": "Aarav Sharma",
        "email": "aarav.sharma@example.com",
        "headline": "Backend Engineer | FastAPI, Postgres, Celery",
        "location": "Bengaluru, India",
        "stage": PipelineStage.applied,
        "skills": ["fastapi", "postgresql", "celery", "redis", "docker", "qdrant"],
        "summary": "Builds resilient Python services, async workers, and vector-backed retrieval systems.",
    },
]


async def reset_demo_data(db) -> None:
    slugs = [org["slug"] for org in DEMO_ORGS]
    org_ids = list((await db.execute(select(Organization.id).where(Organization.slug.in_(slugs)))).scalars())
    if not org_ids:
        return
    for model in [
        CandidateEmbedding,
        JobDescriptionEmbedding,
        CandidateSkill,
        CandidateMatch,
        CandidatePipelineStage,
        CandidateBookmark,
        RankingFeedback,
        RecruiterNote,
        RecruiterActivity,
        ATSScore,
        ResumeProcessingEvent,
        Resume,
        JobDescription,
        Candidate,
        User,
    ]:
        await db.execute(delete(model).where(model.organization_id.in_(org_ids)))
    await db.execute(delete(Organization).where(Organization.id.in_(org_ids)))
    await db.commit()


def resume_text(candidate: dict) -> str:
    skills = ", ".join(candidate["skills"])
    return f"""{candidate['full_name']}
{candidate['headline']}
{candidate['location']} | {candidate['email']}

SUMMARY
{candidate['summary']}

EXPERIENCE
Lead contributor on production hiring, search, analytics, and AI workflow systems.
Improved latency, reliability, and recruiter decision quality using measurable product metrics.

SKILLS
{skills}
"""


async def seed(vector_index: bool, require_vector_index: bool) -> dict:
    async with AsyncSessionLocal() as db:
        await reset_demo_data(db)

        orgs = {}
        for org_data in DEMO_ORGS:
            org = Organization(name=org_data["name"], slug=org_data["slug"])
            db.add(org)
            await db.flush()
            orgs[org.slug] = org

        recruiters = {}
        for recruiter_data in DEMO_RECRUITERS:
            recruiter = User(
                organization_id=orgs[recruiter_data["org"]].id,
                email=recruiter_data["email"],
                full_name=recruiter_data["full_name"],
                hashed_password=hash_password(DEMO_PASSWORD),
                roles=recruiter_data["roles"],
                is_active=True,
            )
            db.add(recruiter)
            await db.flush()
            recruiters[recruiter.email] = recruiter

        jobs = []
        owner = recruiters["sarah@northstar.demo"]
        for job_data in DEMO_JOBS:
            job = JobDescription(
                organization_id=owner.organization_id,
                created_by_user_id=owner.id,
                title=job_data["title"],
                description=job_data["description"],
                status="active",
                role_category=job_data["role_category"],
                required_skills=job_data["required_skills"],
                optional_skills=job_data["optional_skills"],
                keywords=job_data["keywords"],
                education_requirements=[],
            )
            db.add(job)
            await db.flush()
            jobs.append(job)

        candidates = []
        resumes = []
        for index, candidate_data in enumerate(DEMO_CANDIDATES):
            text = resume_text(candidate_data)
            candidate = Candidate(
                organization_id=owner.organization_id,
                full_name=candidate_data["full_name"],
                email=candidate_data["email"],
                headline=candidate_data["headline"],
                location=candidate_data["location"],
                summary=candidate_data["summary"],
                source="demo_seed",
                raw_profile=candidate_data,
            )
            db.add(candidate)
            await db.flush()
            candidates.append(candidate)

            resume = Resume(
                organization_id=owner.organization_id,
                candidate_id=candidate.id,
                uploaded_by_user_id=owner.id,
                original_filename=f"{candidate.full_name.replace(' ', '_')}_resume.pdf",
                content_type="application/pdf",
                storage_key=f"demo/{candidate.id}.pdf",
                checksum_sha256=sha256(text.encode("utf-8")).hexdigest(),
                status=ResumeStatus.embedded,
                extracted_text=text,
                parser_version="demo-seed-1.0",
                metadata_json={"source": "demo_seed", "size_bytes": len(text.encode("utf-8"))},
            )
            db.add(resume)
            await db.flush()
            resumes.append(resume)

            for skill in candidate_data["skills"]:
                db.add(
                    CandidateSkill(
                        organization_id=owner.organization_id,
                        candidate_id=candidate.id,
                        normalized_skill=skill,
                        raw_skill=skill,
                        confidence=0.92,
                    )
                )

            db.add(
                CandidatePipelineStage(
                    organization_id=owner.organization_id,
                    candidate_id=candidate.id,
                    job_description_id=jobs[index % len(jobs)].id,
                    stage=candidate_data["stage"].value,
                    position=index,
                )
            )

        for rank, candidate in enumerate(candidates, start=1):
            for job in jobs:
                score = max(68, 96 - rank * 4)
                db.add(
                    CandidateMatch(
                        organization_id=owner.organization_id,
                        candidate_id=candidate.id,
                        job_description_id=job.id,
                        overall_score=score,
                        semantic_score=score / 100,
                        skill_match=max(0.55, (score - 5) / 100),
                        experience_match=max(0.50, (score - 10) / 100),
                        education_match=0.82,
                        keyword_score=max(0.50, (score - 8) / 100),
                        matched_skills=DEMO_CANDIDATES[rank - 1]["skills"][:4],
                        missing_skills=[],
                        explanation=f"Demo ranking evidence for {job.title}.",
                        scoring_version="demo-hybrid-v1",
                    )
                )

        for candidate in candidates[:3]:
            db.add(
                RecruiterNote(
                    organization_id=owner.organization_id,
                    candidate_id=candidate.id,
                    user_id=owner.id,
                    body="Demo note: strong evidence for next-step recruiter review.",
                )
            )
            db.add(
                RankingFeedback(
                    organization_id=owner.organization_id,
                    user_id=owner.id,
                    candidate_id=candidate.id,
                    job_description_id=jobs[0].id,
                    action=FeedbackAction.shortlist,
                    reward=2.0,
                    rank_position=1,
                    model_version="demo-hybrid-v1",
                    feature_snapshot={"source": "demo_seed"},
                )
            )

        for activity in ["search", "view_candidate", "feedback.shortlist", "copilot.ask", "resume.upload"]:
            db.add(
                RecruiterActivity(
                    organization_id=owner.organization_id,
                    user_id=owner.id,
                    candidate_id=candidates[0].id,
                    job_description_id=jobs[0].id,
                    activity_type=activity,
                    payload={"source": "demo_seed"},
                )
            )

        await db.commit()

        vector_status = "skipped"
        if vector_index:
            try:
                from app.services.embedding_service import EmbeddingService

                service = EmbeddingService()
                for candidate, resume in zip(candidates, resumes, strict=True):
                    chunks = service.chunk_text(resume.extracted_text or "")
                    vectors = service.embed(chunks)
                    point_ids = service.upsert_candidate_resume(
                        owner.organization_id,
                        candidate.id,
                        resume.id,
                        chunks,
                        vectors,
                        metadata={
                            "source": "demo_seed",
                            "skills": candidate.raw_profile.get("skills", []),
                            "full_name": candidate.full_name,
                            "headline": candidate.headline,
                            "location": candidate.location,
                        },
                    )
                    async with AsyncSessionLocal() as embed_db:
                        for chunk, point_id in zip(chunks, point_ids, strict=True):
                            embed_db.add(
                                CandidateEmbedding(
                                    organization_id=owner.organization_id,
                                    candidate_id=candidate.id,
                                    resume_id=resume.id,
                                    qdrant_point_id=point_id,
                                    model_name=settings.embedding_model_name,
                                    vector_size=settings.embedding_vector_size,
                                    chunk_index=chunk.index,
                                    chunk_text=chunk.text,
                                )
                            )
                        await embed_db.commit()
                vector_status = "indexed"
            except Exception as exc:
                if require_vector_index:
                    raise
                vector_status = f"degraded: {exc}"

        return {
            "organizations": len(orgs),
            "recruiters": len(recruiters),
            "jobs": len(jobs),
            "candidates": len(candidates),
            "vector_index": vector_status,
            "login": {"email": "sarah@northstar.demo", "password": DEMO_PASSWORD},
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed recruiter SaaS demo data.")
    parser.add_argument("--skip-vector-index", action="store_true")
    parser.add_argument("--require-vector-index", action="store_true")
    args = parser.parse_args()

    result = asyncio.run(
        seed(vector_index=not args.skip_vector_index, require_vector_index=args.require_vector_index)
    )
    for key, value in result.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
