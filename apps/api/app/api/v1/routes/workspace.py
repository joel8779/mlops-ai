from __future__ import annotations

from hashlib import sha256
from uuid import NAMESPACE_DNS, UUID, uuid5

from fastapi import APIRouter, Depends
from qdrant_client.http.models import PointStruct
from sqlalchemy import desc, func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.core.config import settings
from app.db.session import get_db
from app.models.domain import (
    ATSScore,
    Candidate,
    CandidateEmbedding,
    CandidateMatch,
    CandidatePipelineStage,
    CandidateSkill,
    JobDescription,
    JobStatus,
    PipelineStage,
    RecruiterActivity,
    Resume,
    ResumeProcessingEvent,
    ResumeStatus,
)
from app.schemas.auth import AuthContext
from app.schemas.workspace import (
    ActivityEvent,
    DemoWorkspaceResponse,
    MatchInsight,
    PipelineState,
    WorkspaceActivationResponse,
    WorkspaceCounts,
)
from app.services.embedding_service import EmbeddingService

router = APIRouter()


@router.get("/activation", response_model=WorkspaceActivationResponse)
async def activation(auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return await _workspace_activation(db, auth)


@router.post("/demo", response_model=DemoWorkspaceResponse)
async def load_demo_workspace(auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(
        select(func.count())
        .select_from(Candidate)
        .where(
            Candidate.organization_id == auth.organization_id,
            Candidate.owner_id == auth.user_id,
            Candidate.source == "demo_workspace",
        )
    )
    if existing:
        return DemoWorkspaceResponse(
            status="already_loaded",
            message="Demo workspace is already active for this organization.",
            activation=await _workspace_activation(db, auth),
        )

    jobs = _demo_jobs(auth)
    for job in jobs:
        db.add(job)
    await db.flush()

    candidates = _demo_candidates(auth)
    for candidate in candidates:
        db.add(candidate)
    await db.flush()

    resume_text_by_candidate = _demo_resume_text()
    for index, candidate in enumerate(candidates):
        text = resume_text_by_candidate[index]
        resume = Resume(
            organization_id=auth.organization_id,
            owner_id=auth.user_id,
            candidate_id=candidate.id,
            uploaded_by_user_id=auth.user_id,
            original_filename=f"{candidate.full_name.replace(' ', '_').lower()}_resume.pdf",
            content_type="application/pdf",
            storage_key=f"demo/{auth.organization_id}/{candidate.id}.pdf",
            checksum_sha256=sha256(text.encode("utf-8")).hexdigest(),
            status=ResumeStatus.embedded,
            extracted_text=text,
            parser_version="demo-ocr-parser-v1",
            metadata_json={
                "demo": True,
                "ocr_engine": "neural-ops-demo",
                "size_bytes": len(text.encode("utf-8")),
                "processing_ms": 1180 + index * 160,
            },
        )
        db.add(resume)
        await db.flush()

        skills = candidate.raw_profile.get("skills", [])
        for skill in skills:
            db.add(
                CandidateSkill(
                    organization_id=auth.organization_id,
                    owner_id=auth.user_id,
                    candidate_id=candidate.id,
                    normalized_skill=skill.lower(),
                    raw_skill=skill,
                    confidence=0.88,
                )
            )

        chunks = _chunks(text)
        point_ids = []
        for chunk_index, chunk_text in enumerate(chunks):
            point_id = str(uuid5(NAMESPACE_DNS, f"neural-ops-demo:{resume.id}:{chunk_index}"))
            point_ids.append(point_id)
            db.add(
                CandidateEmbedding(
                    organization_id=auth.organization_id,
                    owner_id=auth.user_id,
                    candidate_id=candidate.id,
                    resume_id=resume.id,
                    qdrant_point_id=point_id,
                    model_name=settings.embedding_model_name,
                    vector_size=settings.embedding_vector_size,
                    chunk_index=chunk_index,
                    chunk_text=chunk_text,
                )
            )

        for event_type, label in [
            ("resume.ocr_completed", "OCR completed"),
            ("resume.embedding_generated", "Embedding generated"),
            ("resume.semantic_indexed", "Semantic index ready"),
        ]:
            db.add(
                ResumeProcessingEvent(
                    organization_id=auth.organization_id,
                    owner_id=auth.user_id,
                    resume_id=resume.id,
                    event_type=event_type,
                    payload={"label": label, "candidate_name": candidate.full_name, "demo": True},
                )
            )

        stage = list(PipelineStage)[index % 5]
        db.add(
            CandidatePipelineStage(
                organization_id=auth.organization_id,
                owner_id=auth.user_id,
                candidate_id=candidate.id,
                job_description_id=jobs[index % len(jobs)].id,
                stage=stage,
                position=index,
                metadata_json={"demo": True, "reason": "Seeded to show active recruiting workflow"},
            )
        )

    for candidate_index, candidate in enumerate(candidates):
        for job_index, job in enumerate(jobs):
            score = max(58, 94 - abs(candidate_index - job_index) * 9 - job_index * 2)
            semantic = max(55, score - 3)
            skills = candidate.raw_profile.get("skills", [])
            required = job.required_skills or []
            matched = [skill for skill in skills if skill in required][:5]
            missing = [skill for skill in required if skill not in skills][:4]
            db.add(
                CandidateMatch(
                    organization_id=auth.organization_id,
                    owner_id=auth.user_id,
                    candidate_id=candidate.id,
                    job_description_id=job.id,
                    overall_score=score,
                    semantic_score=semantic,
                    skill_match=min(98, score + 2),
                    experience_match=max(60, score - 4),
                    education_match=82,
                    keyword_score=max(60, score - 8),
                    matched_skills=matched,
                    missing_skills=missing,
                    explanation=(
                        f"{candidate.full_name} aligns with {job.title} through "
                        f"{', '.join(matched) if matched else 'adjacent production experience'}."
                    ),
                    scoring_version="demo-hybrid-v1",
                )
            )
            if candidate_index == job_index:
                db.add(
                    ATSScore(
                        organization_id=auth.organization_id,
                        owner_id=auth.user_id,
                        candidate_id=candidate.id,
                        job_description_id=job.id,
                        resume_id=(await _latest_demo_resume_id(db, auth.organization_id, auth.user_id, candidate.id)),
                        ats_score=score,
                        components=[
                            {"name": "semantic_similarity", "score": semantic, "weight": 40, "evidence": ["Demo semantic alignment"]},
                            {"name": "skill_weighting", "score": min(98, score + 2), "weight": 25, "evidence": matched},
                            {"name": "experience_fit", "score": max(60, score - 4), "weight": 15, "evidence": ["Demo experience fit"]},
                        ],
                        issues=[f"Missing job skill: {skill}" for skill in missing],
                        recommendations=["Review match explanation before shortlist"],
                        explanation=f"{candidate.full_name} has a job-context ATS score for {job.title}.",
                        scoring_version="demo-ats-job-context-v1",
                    )
                )

    for activity_type, payload in _demo_activities(candidates, jobs):
        db.add(
            RecruiterActivity(
                organization_id=auth.organization_id,
                owner_id=auth.user_id,
                user_id=auth.user_id,
                candidate_id=UUID(payload["candidate_id"]) if payload.get("candidate_id") else None,
                job_description_id=UUID(payload["job_description_id"]) if payload.get("job_description_id") else None,
                activity_type=activity_type,
                payload=payload,
            )
        )

    qdrant_status = _upsert_demo_vectors(auth.organization_id, auth.user_id, candidates, resume_text_by_candidate)
    db.add(
        RecruiterActivity(
            organization_id=auth.organization_id,
            owner_id=auth.user_id,
            user_id=auth.user_id,
            activity_type="demo.workspace_loaded",
            payload={"qdrant_status": qdrant_status, "candidate_count": len(candidates), "job_count": len(jobs)},
        )
    )
    await db.commit()

    return DemoWorkspaceResponse(
        status="loaded",
        message="Demo recruiting workspace loaded with candidates, jobs, matches, ATS scores, processing events, and semantic artifacts.",
        activation=await _workspace_activation(db, auth),
    )


async def _workspace_activation(db: AsyncSession, auth: AuthContext) -> WorkspaceActivationResponse:
    counts = WorkspaceCounts(
        candidates=await _count(db, auth, Candidate),
        jobs=await _count(db, auth, JobDescription),
        resumes=await _count(db, auth, Resume),
        embedded_resumes=await _count_status(db, auth, ResumeStatus.embedded),
        ats_scores=await _count(db, auth, ATSScore),
        semantic_matches=await _count(db, auth, CandidateMatch),
        activities=await _count(db, auth, RecruiterActivity),
    )
    pipeline_rows = await db.execute(
        select(Resume.status, func.count())
        .where(Resume.organization_id == auth.organization_id, Resume.owner_id == auth.user_id)
        .group_by(Resume.status)
    )
    pipeline_values = {status.value: int(count) for status, count in pipeline_rows.all()}
    pipeline = PipelineState(**pipeline_values)
    activated = counts.candidates > 0 or counts.resumes > 0 or counts.jobs > 0
    recommendations = _recommendations(counts, pipeline)
    return WorkspaceActivationResponse(
        activated=activated,
        activation_reason="workspace_has_recruiting_intelligence" if activated else "workspace_empty",
        counts=counts,
        pipeline=pipeline,
        activity=await _activity(db, auth),
        match_insights=await _match_insights(db, auth),
        recommendations=recommendations,
    )


async def _count(db: AsyncSession, auth: AuthContext, model) -> int:
    value = await db.scalar(
        select(func.count()).select_from(model).where(
            model.organization_id == auth.organization_id,
            model.owner_id == auth.user_id,
            model.deleted_at.is_(None),
        )
    )
    return int(value or 0)


async def _count_status(db: AsyncSession, auth: AuthContext, status: ResumeStatus) -> int:
    value = await db.scalar(
        select(func.count()).select_from(Resume).where(
            Resume.organization_id == auth.organization_id,
            Resume.owner_id == auth.user_id,
            Resume.status == status,
            Resume.deleted_at.is_(None),
        )
    )
    return int(value or 0)


async def _activity(db: AsyncSession, auth: AuthContext) -> list[ActivityEvent]:
    resume_events = (
        select(
            ResumeProcessingEvent.id,
            ResumeProcessingEvent.event_type,
            literal("resume").label("source"),
            literal(None).label("candidate_id"),
            literal(None).label("job_description_id"),
            ResumeProcessingEvent.resume_id,
            ResumeProcessingEvent.payload,
            ResumeProcessingEvent.created_at,
        )
        .where(
            ResumeProcessingEvent.organization_id == auth.organization_id,
            ResumeProcessingEvent.owner_id == auth.user_id,
        )
        .order_by(desc(ResumeProcessingEvent.created_at))
        .limit(20)
    )
    recruiter_events = (
        select(
            RecruiterActivity.id,
            RecruiterActivity.activity_type.label("event_type"),
            literal("workflow").label("source"),
            RecruiterActivity.candidate_id,
            RecruiterActivity.job_description_id,
            literal(None).label("resume_id"),
            RecruiterActivity.payload,
            RecruiterActivity.created_at,
        )
        .where(RecruiterActivity.organization_id == auth.organization_id, RecruiterActivity.owner_id == auth.user_id)
        .order_by(desc(RecruiterActivity.created_at))
        .limit(20)
    )
    rows = list((await db.execute(resume_events)).mappings().all()) + list((await db.execute(recruiter_events)).mappings().all())
    rows.sort(key=lambda item: item["created_at"], reverse=True)
    return [
        ActivityEvent(
            id=row["id"],
            event_type=row["event_type"],
            label=_label(row["event_type"], row["payload"] or {}),
            source=row["source"],
            candidate_id=row["candidate_id"],
            job_description_id=row["job_description_id"],
            resume_id=row["resume_id"],
            payload=row["payload"] or {},
            created_at=row["created_at"],
        )
        for row in rows[:24]
    ]


async def _match_insights(db: AsyncSession, auth: AuthContext) -> list[MatchInsight]:
    rows = await db.execute(
        select(CandidateMatch, Candidate.full_name, JobDescription.title)
        .join(Candidate, Candidate.id == CandidateMatch.candidate_id)
        .join(JobDescription, JobDescription.id == CandidateMatch.job_description_id)
        .where(
            CandidateMatch.organization_id == auth.organization_id,
            CandidateMatch.owner_id == auth.user_id,
            Candidate.organization_id == auth.organization_id,
            Candidate.owner_id == auth.user_id,
            JobDescription.organization_id == auth.organization_id,
            JobDescription.owner_id == auth.user_id,
        )
        .order_by(desc(CandidateMatch.overall_score))
        .limit(6)
    )
    return [
        MatchInsight(
            candidate_id=match.candidate_id,
            job_description_id=match.job_description_id,
            candidate_name=name,
            job_title=title,
            overall_score=float(match.overall_score),
            semantic_score=float(match.semantic_score),
            matched_skills=match.matched_skills,
            explanation=match.explanation,
        )
        for match, name, title in rows.all()
    ]


async def _latest_demo_resume_id(db: AsyncSession, organization_id: UUID, owner_id: UUID, candidate_id: UUID) -> UUID:
    resume_id = await db.scalar(
        select(Resume.id)
        .where(
            Resume.organization_id == organization_id,
            Resume.owner_id == owner_id,
            Resume.candidate_id == candidate_id,
        )
        .order_by(desc(Resume.created_at))
        .limit(1)
    )
    if resume_id is None:
        raise RuntimeError("Demo candidate resume was not created")
    return resume_id


def _recommendations(counts: WorkspaceCounts, pipeline: PipelineState) -> list[str]:
    if counts.resumes == 0:
        return ["Upload resumes or load the demo workspace to activate candidate intelligence."]
    recommendations = []
    if pipeline.queued or pipeline.parsing:
        recommendations.append("Worker ingestion is active; wait for parsing and embedding to complete.")
    if counts.semantic_matches == 0 and counts.jobs > 0 and counts.candidates > 0:
        recommendations.append("Run candidate ranking to generate job-specific semantic matches.")
    if counts.activities == 0:
        recommendations.append("Shortlist, note, or move candidates to build workflow telemetry.")
    if not recommendations:
        recommendations.append("Workspace is active; use semantic search and copilot to inspect candidate fit.")
    return recommendations


def _label(event_type: str, payload: dict) -> str:
    return payload.get("label") or event_type.replace(".", " ").replace("_", " ").title()


def _demo_jobs(auth: AuthContext) -> list[JobDescription]:
    return [
        JobDescription(
            organization_id=auth.organization_id,
            owner_id=auth.user_id,
            created_by_user_id=auth.user_id,
            title="Staff Backend Platform Engineer",
            description="Own FastAPI services, PostgreSQL reliability, Redis queues, Docker runtime, and Kubernetes delivery for regulated AI workflows.",
            status=JobStatus.active,
            role_category="Backend Platform",
            years_experience_min=7,
            years_experience_max=12,
            education_requirements=["BS Computer Science or equivalent production experience"],
            keywords=["FastAPI", "PostgreSQL", "Redis", "Kubernetes", "observability"],
            required_skills=["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Kubernetes"],
            optional_skills=["Qdrant", "Celery", "OpenTelemetry"],
            metadata_json={"demo": True},
        ),
        JobDescription(
            organization_id=auth.organization_id,
            owner_id=auth.user_id,
            created_by_user_id=auth.user_id,
            title="Machine Learning Retrieval Engineer",
            description="Build embedding pipelines, semantic retrieval, reranking, and evaluation systems for recruiter intelligence workflows.",
            status=JobStatus.active,
            role_category="Machine Learning",
            years_experience_min=5,
            years_experience_max=10,
            education_requirements=["ML systems experience"],
            keywords=["embeddings", "semantic search", "reranking", "Qdrant", "evaluation"],
            required_skills=["Python", "NLP", "PyTorch", "Qdrant", "MLflow"],
            optional_skills=["FastAPI", "Kubernetes", "RAG"],
            metadata_json={"demo": True},
        ),
        JobDescription(
            organization_id=auth.organization_id,
            owner_id=auth.user_id,
            created_by_user_id=auth.user_id,
            title="Recruiting Intelligence Product Engineer",
            description="Ship recruiter command-center workflows with Next.js, TypeScript, AI-assisted search, analytics, and dense operational UX.",
            status=JobStatus.active,
            role_category="Product Engineering",
            years_experience_min=4,
            years_experience_max=8,
            education_requirements=["Strong frontend systems portfolio"],
            keywords=["Next.js", "TypeScript", "analytics", "workflow UX"],
            required_skills=["TypeScript", "Next.js", "React", "Analytics", "UX"],
            optional_skills=["Python", "FastAPI", "AI"],
            metadata_json={"demo": True},
        ),
    ]


def _demo_candidates(auth: AuthContext) -> list[Candidate]:
    profiles = [
        ("Avery Chen", "Staff Backend Engineer", "San Francisco, CA", ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Kubernetes"]),
        ("Mira Kapoor", "ML Retrieval Engineer", "Bengaluru, IN", ["Python", "NLP", "PyTorch", "Qdrant", "MLflow", "RAG"]),
        ("Jon Bell", "Product Platform Engineer", "Remote US", ["TypeScript", "Next.js", "React", "Analytics", "UX", "Python"]),
        ("Samira Okafor", "Infrastructure Engineer", "London, UK", ["Python", "Kubernetes", "Docker", "OpenTelemetry", "Redis", "Celery"]),
        ("Diego Ramos", "Applied AI Engineer", "Austin, TX", ["Python", "FastAPI", "NLP", "Qdrant", "PyTorch", "PostgreSQL"]),
    ]
    return [
        Candidate(
            organization_id=auth.organization_id,
            owner_id=auth.user_id,
            full_name=name,
            email=f"{name.lower().replace(' ', '.')}@demo.neuralops.ai",
            location=location,
            headline=headline,
            summary=f"{headline} with production experience across {', '.join(skills[:4])}.",
            source="demo_workspace",
            raw_profile={"demo": True, "skills": skills, "years_experience": 6 + index},
        )
        for index, (name, headline, location, skills) in enumerate(profiles)
    ]


def _demo_resume_text() -> list[str]:
    return [
        "Staff backend engineer leading Python FastAPI services with PostgreSQL, Redis, Docker, Kubernetes, Celery workers, reliability reviews, and observability.",
        "Machine learning retrieval engineer building NLP embeddings, Qdrant semantic search, PyTorch rerankers, MLflow evaluation, and production RAG systems.",
        "Product platform engineer shipping Next.js React TypeScript recruiter workflows, analytics dashboards, UX systems, and AI-assisted search experiences.",
        "Infrastructure engineer operating Kubernetes, Docker, Redis, Celery, OpenTelemetry traces, worker queues, and backend reliability programs.",
        "Applied AI engineer delivering FastAPI services, PostgreSQL data models, Qdrant vector search, NLP pipelines, PyTorch inference, and recruiter intelligence tooling.",
    ]


def _chunks(text: str) -> list[str]:
    words = text.split()
    return [" ".join(words[index : index + 48]) for index in range(0, len(words), 48)] or [text]


def _demo_activities(candidates: list[Candidate], jobs: list[JobDescription]) -> list[tuple[str, dict]]:
    return [
        ("candidate.matched", {"label": "Candidate matched", "candidate_id": str(candidates[0].id), "job_description_id": str(jobs[0].id), "score": 94}),
        ("ai.ranking_completed", {"label": "AI ranking completed", "job_description_id": str(jobs[1].id), "ranked_candidates": 5}),
        ("semantic.search_ready", {"label": "Semantic relationships mapped", "candidate_id": str(candidates[1].id), "job_description_id": str(jobs[1].id)}),
        ("recruiter.shortlist_recommended", {"label": "Shortlist recommendation generated", "candidate_id": str(candidates[2].id), "job_description_id": str(jobs[2].id)}),
    ]


def _upsert_demo_vectors(organization_id: UUID, owner_id: UUID, candidates: list[Candidate], texts: list[str]) -> str:
    try:
        service = EmbeddingService()
        service.ensure_collection()
        points = []
        for candidate, text in zip(candidates, texts, strict=True):
            point_id = str(uuid5(NAMESPACE_DNS, f"neural-ops-demo-qdrant:{candidate.id}"))
            points.append(
                PointStruct(
                    id=point_id,
                    vector=_deterministic_vector(text),
                    payload={
                        "organization_id": str(organization_id),
                        "owner_id": str(owner_id),
                        "candidate_id": str(candidate.id),
                        "resume_id": None,
                        "chunk_index": 0,
                        "text": text,
                        "full_name": candidate.full_name,
                        "headline": candidate.headline,
                        "location": candidate.location,
                        "skills": candidate.raw_profile.get("skills", []),
                        "demo": True,
                    },
                )
            )
        service.client.upsert(collection_name=settings.qdrant_collection, points=points)
        return "indexed"
    except Exception as exc:
        return f"deferred:{type(exc).__name__}"


def _deterministic_vector(text: str) -> list[float]:
    digest = sha256(text.encode("utf-8")).digest()
    values = []
    for index in range(settings.embedding_vector_size):
        byte = digest[index % len(digest)]
        values.append((byte / 255.0) * 2.0 - 1.0)
    return values
