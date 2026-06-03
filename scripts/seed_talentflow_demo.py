"""Seed custom TalentFlow demo environment for screenshots.

Creates the TalentFlow organization, a single Recruiter A user, exactly 3 candidates,
and 2 jobs with realistic ATS scores. Purges existing data first to guarantee exact counts.
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


DEMO_PASSWORD = "demo123"
DEMO_ORGS = [
    {"name": "TalentFlow", "slug": "talentflow"},
]
DEMO_RECRUITERS = [
    {"email": "recruiter_a@talentflow.com", "full_name": "Recruiter A", "roles": ["admin"], "org": "talentflow"},
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
        "title": "Full Stack Developer",
        "description": "Own API reliability, Next.js/React frontend dashboards, PostgreSQL data models, Redis queues, and secure multi-tenant foundations.",
        "role_category": "full_stack",
        "required_skills": ["react", "typescript", "next.js", "fastapi", "postgresql"],
        "optional_skills": ["redis", "docker", "kubernetes", "aws"],
        "keywords": ["full stack", "frontend", "backend", "dashboard"],
    },
]
DEMO_CANDIDATES = [
    {
        "full_name": "James Rodriguez",
        "email": "james.rodriguez@example.com",
        "headline": "Senior ML Engineer | Ranking and NLP",
        "location": "San Francisco, CA",
        "stage": PipelineStage.interviewing,
        "skills": ["python", "pytorch", "mlops", "kubernetes", "docker", "redis"],
        "summary": "Built recommendation systems, document classifiers, and production MLOps pipelines for high-scale AI products.",
    },
    {
        "full_name": "Emily Zhang",
        "email": "emily.zhang@example.com",
        "headline": "Full Stack Developer | React & Node.js Expert",
        "location": "New York, NY",
        "stage": PipelineStage.shortlisted,
        "skills": ["react", "typescript", "next.js", "fastapi", "postgresql", "redis", "node.js"],
        "summary": "Ships polished SaaS dashboards backed by reliable APIs and strong product iteration habits.",
    },
    {
        "full_name": "David Kim",
        "email": "david.kim@example.com",
        "headline": "DevOps Engineer | Kubernetes and Cloud Specialist",
        "location": "Austin, TX",
        "stage": PipelineStage.ranked,
        "skills": ["kubernetes", "docker", "terraform", "prometheus", "grafana", "aws", "gcp"],
        "summary": "Runs production infrastructure with strong CI/CD, incident response, and cost-control experience.",
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

        # Create Organizations
        orgs = {}
        for org_data in DEMO_ORGS:
            org = Organization(name=org_data["name"], slug=org_data["slug"])
            db.add(org)
            await db.flush()
            orgs[org.slug] = org

        # Create Recruiters
        recruiters = {}
        for recruiter_data in DEMO_RECRUITERS:
            recruiter = User(
                organization_id=orgs[recruiter_data["org"]].id,
                email=recruiter_data["email"],
                full_name=recruiter_data["full_name"],
                hashed_password=hash_password(DEMO_PASSWORD),
                roles=recruiter_data["roles"],
                is_active=True,
                otp_verified=True,  # Bypass OTP verification
            )
            db.add(recruiter)
            await db.flush()
            recruiters[recruiter.email] = recruiter

        # Create Job Descriptions
        jobs = []
        owner = recruiters["recruiter_a@talentflow.com"]
        for job_data in DEMO_JOBS:
            job = JobDescription(
                organization_id=owner.organization_id,
                owner_id=owner.id,
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

        # Create Candidates & Resumes
        candidates = []
        resumes = []
        for index, candidate_data in enumerate(DEMO_CANDIDATES):
            text = resume_text(candidate_data)
            candidate = Candidate(
                organization_id=owner.organization_id,
                owner_id=owner.id,
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
                owner_id=owner.id,
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
                        owner_id=owner.id,
                        candidate_id=candidate.id,
                        normalized_skill=skill,
                        raw_skill=skill,
                        confidence=0.95,
                    )
                )

            # Assign stages to jobs.
            # Stage 1 for Job 1, Stage 2 for Job 2
            db.add(
                CandidatePipelineStage(
                    organization_id=owner.organization_id,
                    owner_id=owner.id,
                    candidate_id=candidate.id,
                    job_description_id=jobs[0].id,
                    stage=candidate_data["stage"].value,
                    position=index,
                )
            )
            db.add(
                CandidatePipelineStage(
                    organization_id=owner.organization_id,
                    owner_id=owner.id,
                    candidate_id=candidate.id,
                    job_description_id=jobs[1].id,
                    stage=PipelineStage.ranked.value,
                    position=index + 1,
                )
            )

        # Realistic ATS scores and Candidate Matches
        # Candidate 0 (James Rodriguez) - ML expert
        # Candidate 1 (Emily Zhang) - Full stack expert
        # Candidate 2 (David Kim) - DevOps expert
        
        # Matches matrix
        # [candidate_idx][job_idx] = (overall_score, semantic_score, skill_match, experience_match, explanation, matched_skills)
        matrix = {
            (0, 0): (92.50, 0.93, 0.90, 0.95, "Excellent fit for the ML role with strong Python, PyTorch, and MLOps credentials.", ["python", "pytorch", "mlops", "kubernetes"]),
            (0, 1): (53.00, 0.45, 0.40, 0.60, "Basic scripting experience but lacks modern frontend or backend framework context.", ["postgresql", "redis"]),
            
            (1, 0): (41.20, 0.35, 0.30, 0.50, "Full stack background; lacks deep ML, neural networks, or MLOps capabilities.", ["python"]),
            (1, 1): (94.10, 0.95, 0.92, 0.90, "Superb web development expert with FastAPI, Next.js, React, and SQL database skills.", ["react", "typescript", "next.js", "fastapi", "postgresql"]),
            
            (2, 0): (68.40, 0.70, 0.65, 0.70, "Strong infrastructure and containers skill; fits MLOps deployment context.", ["kubernetes", "docker"]),
            (2, 1): (79.50, 0.81, 0.78, 0.75, "Capable system architect; well-versed in databases, scaling, and Docker workflows.", ["postgresql", "redis", "docker"]),
        }

        for (cand_idx, job_idx), data in matrix.items():
            candidate = candidates[cand_idx]
            job = jobs[job_idx]
            resume = resumes[cand_idx]
            score, sem, skill, exp, expl, matched = data
            
            db.add(
                CandidateMatch(
                    organization_id=owner.organization_id,
                    owner_id=owner.id,
                    candidate_id=candidate.id,
                    job_description_id=job.id,
                    overall_score=score,
                    semantic_score=sem,
                    skill_match=skill,
                    experience_match=exp,
                    education_match=0.85,
                    keyword_score=score / 100,
                    matched_skills=matched,
                    missing_skills=[],
                    explanation=expl,
                    scoring_version="hybrid-v1",
                )
            )

            db.add(
                ATSScore(
                    organization_id=owner.organization_id,
                    owner_id=owner.id,
                    candidate_id=candidate.id,
                    job_description_id=job.id,
                    resume_id=resume.id,
                    ats_score=score,
                    components=[
                        {"name": "skills", "score": float(skill * 100)},
                        {"name": "experience", "score": float(exp * 100)},
                        {"name": "semantic", "score": float(sem * 100)},
                    ],
                    issues=[] if score > 70 else ["Lacks core required languages or environments listed in the JD"],
                    recommendations=["Proceed to technical interview"] if score > 80 else ["Assess general developer core competencies"],
                    explanation=expl,
                    scoring_version="ats-job-context-v1",
                )
            )

        # Create recruiter notes
        db.add(
            RecruiterNote(
                organization_id=owner.organization_id,
                owner_id=owner.id,
                candidate_id=candidates[0].id,
                user_id=owner.id,
                body="Demo Note: James shows outstanding knowledge of PyTorch and production model scaling. Highly recommended.",
            )
        )
        db.add(
            RecruiterNote(
                organization_id=owner.organization_id,
                owner_id=owner.id,
                candidate_id=candidates[1].id,
                user_id=owner.id,
                body="Demo Note: Emily built extremely polished dashboards. Code quality is great.",
            )
        )

        # Create recruiter activities
        for activity_type in ["search", "view_candidate", "feedback.shortlist", "copilot.ask", "resume.upload"]:
            db.add(
                RecruiterActivity(
                    organization_id=owner.organization_id,
                    owner_id=owner.id,
                    user_id=owner.id,
                    candidate_id=candidates[0].id,
                    job_description_id=jobs[0].id,
                    activity_type=activity_type,
                    payload={"source": "demo_seed"},
                )
            )

        # Create ranking feedback
        db.add(
            RankingFeedback(
                organization_id=owner.organization_id,
                owner_id=owner.id,
                user_id=owner.id,
                candidate_id=candidates[0].id,
                job_description_id=jobs[0].id,
                action=FeedbackAction.shortlist,
                reward=1.0,
                rank_position=1,
                model_version="demo-hybrid-v1",
                feature_snapshot={"source": "demo_seed"},
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
                        owner.id,
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
                                    owner_id=owner.id,
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
            "login": {"email": owner.email, "password": DEMO_PASSWORD},
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed TalentFlow recruiter SaaS demo data.")
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
