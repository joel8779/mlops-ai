import re
from collections import Counter
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.domain import JobDescription, JobDescriptionEmbedding
from app.schemas.auth import AuthContext
from app.schemas.jobs import JobDescriptionCreate, JobParseResult
from app.services.embedding_service import EmbeddingService
from app.services.extraction_service import ExtractionService
from app.utils.files import read_validated_upload
from app.workers.job_tasks import index_job_description_task

SKILL_TERMS = {
    "python", "fastapi", "django", "flask", "postgresql", "mysql", "redis", "docker",
    "kubernetes", "aws", "gcp", "azure", "terraform", "celery", "sqlalchemy", "mlflow",
    "prefect", "nlp", "machine learning", "pytorch", "tensorflow", "react", "next.js",
    "typescript", "javascript", "node.js", "java", "spring", "go", "microservices",
}
EDUCATION_TERMS = ["bachelor", "master", "phd", "computer science", "engineering", "mba"]


class JobIntelligenceService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_from_text(self, auth: AuthContext, payload: JobDescriptionCreate) -> JobDescription:
        parsed = self.parse(payload.description)
        job = JobDescription(
            organization_id=auth.organization_id,
            created_by_user_id=auth.user_id,
            title=payload.title,
            description=payload.description,
            status=payload.status,
            role_category=parsed.role_category,
            years_experience_min=parsed.years_experience_min,
            years_experience_max=parsed.years_experience_max,
            education_requirements=parsed.education_requirements,
            required_skills=parsed.skills[:10],
            optional_skills=parsed.skills[10:],
            keywords=parsed.keywords,
            metadata_json={"source": "raw_text"},
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        index_job_description_task.delay(str(job.id))
        return job

    async def create_from_upload(self, auth: AuthContext, title: str, upload: UploadFile) -> JobDescription:
        payload = await read_validated_upload(upload, settings.max_upload_bytes)
        if upload.content_type not in {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported JD file")
        parsed_doc = ExtractionService().parse(payload, upload.content_type or "")
        return await self.create_from_text(
            auth,
            JobDescriptionCreate(title=title, description=parsed_doc.text),
        )

    async def index_job(self, job_id: UUID) -> None:
        job = await self.db.get(JobDescription, job_id)
        if job is None:
            return
        embedding_service = EmbeddingService()
        chunks = embedding_service.chunk_text(job.description)
        vectors = embedding_service.embed(chunks)
        await self.db.execute(
            delete(JobDescriptionEmbedding).where(JobDescriptionEmbedding.job_description_id == job.id)
        )
        point_ids = embedding_service.upsert_job_description(
            job.organization_id,
            job.id,
            chunks,
            vectors,
        )
        for chunk, point_id in zip(chunks, point_ids, strict=True):
            self.db.add(
                JobDescriptionEmbedding(
                    organization_id=job.organization_id,
                    job_description_id=job.id,
                    qdrant_point_id=point_id,
                    model_name=settings.embedding_model_name,
                    vector_size=settings.embedding_vector_size,
                    chunk_index=chunk.index,
                    chunk_text=chunk.text,
                )
            )
        await self.db.commit()

    def parse(self, text: str) -> JobParseResult:
        normalized = text.lower()
        skills = sorted({skill for skill in SKILL_TERMS if skill in normalized})
        years = [int(match) for match in re.findall(r"(\d+)\+?\s*(?:years|yrs)", normalized)]
        education = sorted({term for term in EDUCATION_TERMS if term in normalized})
        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9\.\+#-]{2,}", normalized)
        keywords = [word for word, _ in Counter(tokens).most_common(30) if word not in {"and", "the", "with", "for"}]
        role_category = self._category(normalized)
        return JobParseResult(
            skills=skills,
            years_experience_min=min(years) if years else None,
            years_experience_max=max(years) if len(years) > 1 else None,
            education_requirements=education,
            keywords=keywords,
            role_category=role_category,
        )

    @staticmethod
    def _category(text: str) -> str | None:
        if any(term in text for term in ["machine learning", "nlp", "data scientist"]):
            return "machine_learning"
        if any(term in text for term in ["frontend", "react", "next.js"]):
            return "frontend_engineering"
        if any(term in text for term in ["backend", "api", "microservices"]):
            return "backend_engineering"
        if any(term in text for term in ["devops", "platform", "kubernetes"]):
            return "platform_engineering"
        return None
