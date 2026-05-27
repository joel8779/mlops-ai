import re
from collections import Counter
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.config import settings
from app.models.domain import JobDescription, JobDescriptionEmbedding
from app.schemas.auth import AuthContext
from app.schemas.jobs import JobDescriptionCreate, JobExtractionPreview, JobParseResult
from app.services.embedding_service import EmbeddingService
from app.services.extraction_service import ExtractionService, ResumeParseError
from app.utils.files import read_validated_upload

SKILL_TERMS = {
    "python", "fastapi", "django", "flask", "postgresql", "mysql", "redis", "docker",
    "kubernetes", "aws", "gcp", "azure", "terraform", "celery", "sqlalchemy", "mlflow",
    "prefect", "nlp", "machine learning", "pytorch", "tensorflow", "react", "next.js",
    "typescript", "javascript", "node.js", "java", "spring", "go", "microservices",
    "spark", "airflow", "databricks", "snowflake", "pandas", "numpy", "scikit-learn",
    "langchain", "llm", "rag", "qdrant", "elasticsearch", "mongodb", "graphql",
    "rest", "ci/cd", "github actions", "jenkins", "linux", "bash", "prometheus",
    "grafana", "opencv", "ocr", "transformers", "huggingface",
}
EDUCATION_TERMS = ["bachelor", "master", "phd", "computer science", "engineering", "mba"]


class JobIntelligenceService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_from_text(
        self,
        auth: AuthContext,
        payload: JobDescriptionCreate,
        source: str = "raw_text",
    ) -> JobDescription:
        if not payload.title or not payload.title.strip():
            raise AppError("Job title is required. Please provide a title for the job description.")
        parsed = self.parse(payload.description)
        semantic_requirements = self.semantic_requirements(payload.description, parsed)
        job = JobDescription(
            organization_id=auth.organization_id,
            owner_id=auth.user_id,
            created_by_user_id=auth.user_id,
            title=payload.title.strip(),
            description=payload.description,
            status=payload.status,
            role_category=parsed.role_category,
            years_experience_min=parsed.years_experience_min,
            years_experience_max=parsed.years_experience_max,
            education_requirements=parsed.education_requirements,
            required_skills=parsed.skills[:12],
            optional_skills=parsed.preferred_skills or parsed.technologies[12:],
            keywords=parsed.keywords,
            metadata_json={
                "source": source,
                "intelligence": {
                    "skill_count": len(parsed.skills),
                    "keyword_count": len(parsed.keywords),
                    "has_experience_requirement": parsed.years_experience_min is not None,
                    "has_education_requirement": bool(parsed.education_requirements),
                    "semantic_requirements": semantic_requirements,
                    "preferred_skills": parsed.preferred_skills,
                    "technologies": parsed.technologies,
                    "seniority": parsed.seniority,
                    "summary": parsed.summary,
                },
                "indexing": {"status": "queued"},
            },
        )
        try:
            self.db.add(job)
            await self.db.commit()
            await self.db.refresh(job)
        except IntegrityError as exc:
            await self.db.rollback()
            raise AppError("Could not create this job because it conflicts with existing recruiting data.") from exc
        except SQLAlchemyError as exc:
            await self.db.rollback()
            raise AppError(
                "Could not save the job description. Check required fields and try again.",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from exc
        # Lazy import to avoid circular dependency
        from app.workers.job_tasks import index_job_description_task
        try:
            index_job_description_task.delay(str(job.id))
        except Exception as exc:
            job.metadata_json = {
                **(job.metadata_json or {}),
                "indexing": {"status": "enqueue_failed", "error": str(exc)},
            }
            await self.db.commit()
        return job

    async def create_from_upload(self, auth: AuthContext, title: str | None, upload: UploadFile) -> JobDescription:
        preview = await self.preview_upload(upload, title)
        if not preview.title:
            raise AppError("Could not extract a job title from the uploaded file. Please provide a title manually.")
        return await self.create_from_text(
            auth,
            JobDescriptionCreate(title=preview.title, description=preview.description),
            source="upload",
        )

    async def preview_upload(self, upload: UploadFile, title: str | None = None) -> JobExtractionPreview:
        payload = await read_validated_upload(upload, settings.max_upload_bytes)
        if upload.content_type not in {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported JD file")
        try:
            parsed_doc = ExtractionService().parse(payload, upload.content_type or "")
        except ResumeParseError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "Job description extraction failed", "reason": str(exc)},
            ) from exc
        if len(parsed_doc.text.strip()) < 20:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Job description extraction produced too little text",
                    "reason": "The uploaded file may be scanned, encrypted, or image-only without OCR support.",
                    "metadata": parsed_doc.metadata,
                },
            )
        parsed = self.parse(parsed_doc.text)
        inferred_title = title.strip() if title and title.strip() else self.infer_title(parsed_doc.text, parsed_doc.metadata)
        return JobExtractionPreview(
            title=inferred_title,
            description=parsed_doc.text,
            role_category=parsed.role_category,
            years_experience_min=parsed.years_experience_min,
            years_experience_max=parsed.years_experience_max,
            education_requirements=parsed.education_requirements,
            required_skills=parsed.skills[:12],
            optional_skills=parsed.preferred_skills or parsed.technologies[12:],
            keywords=parsed.keywords,
            semantic_requirements=self.semantic_requirements(parsed_doc.text, parsed),
            extraction_metadata={
                **parsed_doc.metadata,
                "technologies": parsed.technologies,
                "seniority": parsed.seniority,
                "summary": parsed.summary,
                "preferred_skills": parsed.preferred_skills,
            },
            warnings=[] if inferred_title else ["Could not confidently infer a job title."],
        )

    async def index_job(self, job_id: UUID) -> None:
        job = await self.db.get(JobDescription, job_id)
        if job is None:
            return
        embedding_service = EmbeddingService()
        chunks = embedding_service.chunk_text(job.description)
        vectors = embedding_service.embed(chunks)
        await self.db.execute(
            delete(JobDescriptionEmbedding).where(
                JobDescriptionEmbedding.organization_id == job.organization_id,
                JobDescriptionEmbedding.owner_id == job.owner_id,
                JobDescriptionEmbedding.job_description_id == job.id,
            )
        )
        point_ids = embedding_service.upsert_job_description(
            job.organization_id,
            job.owner_id,
            job.id,
            chunks,
            vectors,
        )
        for chunk, point_id in zip(chunks, point_ids, strict=True):
            self.db.add(
                JobDescriptionEmbedding(
                    organization_id=job.organization_id,
                    owner_id=job.owner_id,
                    job_description_id=job.id,
                    qdrant_point_id=point_id,
                    model_name=settings.embedding_model_name,
                    vector_size=settings.embedding_vector_size,
                    chunk_index=chunk.index,
                    chunk_text=chunk.text,
                )
            )
        job.metadata_json = {
            **(job.metadata_json or {}),
            "indexing": {"status": "embedded", "chunk_count": len(chunks), "vector_size": settings.embedding_vector_size},
        }
        await self.db.commit()

    def parse(self, text: str) -> JobParseResult:
        # Preprocess text to remove noise
        cleaned_text = self._preprocess_jd(text)
        normalized = cleaned_text.lower()
        skills = sorted({skill for skill in SKILL_TERMS if skill in normalized})
        preferred_skills = self._skills_near(cleaned_text, ["preferred", "nice to have", "bonus", "plus"])
        required_skills = self._skills_near(cleaned_text, ["required", "must", "requirements", "need", "responsibilities"]) or skills
        years = [int(match) for match in re.findall(r"(\d+)\+?\s*(?:years|yrs)", normalized)]
        education = sorted({term for term in EDUCATION_TERMS if term in normalized})
        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9\.\+#-]{2,}", normalized)
        keywords = [word for word, _ in Counter(tokens).most_common(30) if word not in {"and", "the", "with", "for"}]
        role_category = self._category(normalized)
        seniority = self._seniority(max(years) if years else None, normalized)
        return JobParseResult(
            skills=required_skills,
            preferred_skills=preferred_skills,
            technologies=skills,
            years_experience_min=min(years) if years else None,
            years_experience_max=max(years) if len(years) > 1 else None,
            education_requirements=education,
            keywords=keywords,
            role_category=role_category,
            seniority=seniority,
            summary=self._summary(cleaned_text, required_skills, seniority),
        )

    def infer_title(self, text: str, metadata: dict | None = None) -> str:
        metadata = metadata or {}
        for key in ["title", "Title", "subject", "Subject"]:
            value = str(metadata.get(key) or "").strip()
            if self._looks_like_title(value):
                return value[:255]
        lines = [line.strip(" -:\t") for line in text.splitlines() if line.strip()]
        title_patterns = [
            r"(?i)(?:job\s*title|position|role)\s*[:\-]\s*(.+)",
            r"(?i)(.+?)\s+(?:job description|role description)$",
        ]
        for line in lines[:20]:
            for pattern in title_patterns:
                match = re.search(pattern, line)
                if match and self._looks_like_title(match.group(1)):
                    return match.group(1).strip()[:255]
        for line in lines[:10]:
            if self._looks_like_title(line):
                return line[:255]
        category = self._category(text.lower())
        if category:
            return category.replace("_", " ").title()
        # Derive from filename if available
        filename = str(metadata.get("filename", "")).strip()
        if filename:
            # Remove file extension and common suffixes
            clean_name = re.sub(r"\.(pdf|docx|doc|txt)$", "", filename, flags=re.IGNORECASE)
            clean_name = re.sub(r"(?i)\b(job|description|jd|position|role|posting)\b", "", clean_name)
            clean_name = clean_name.strip(" -_")
            if clean_name and len(clean_name) >= 3:
                return clean_name[:255]
        # Last resort: use first meaningful line
        for line in lines[:5]:
            if len(line) >= 5 and len(line) <= 100:
                return line[:255]
        # If no title can be inferred, return empty string to trigger explicit error
        return ""

    @staticmethod
    def semantic_requirements(text: str, parsed: JobParseResult) -> list[str]:
        requirements: list[str] = []
        for line in text.splitlines():
            normalized = line.strip(" -\t")
            lower = normalized.lower()
            if len(normalized) < 12:
                continue
            if any(term in lower for term in ["responsible", "requirements", "experience", "must", "build", "own", "design", "lead"]):
                requirements.append(normalized[:240])
            if len(requirements) >= 8:
                break
        if parsed.skills and not requirements:
            requirements.append(f"Role requires evidence across {', '.join(parsed.skills[:6])}.")
        return requirements

    @classmethod
    def _skills_near(cls, text: str, markers: list[str]) -> list[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        found: set[str] = set()
        active = False
        for line in lines:
            lower = line.lower()
            if any(marker in lower for marker in markers):
                active = True
            elif active and re.match(r"^[A-Z][A-Za-z\s]{2,}:$", line):
                active = False
            if active or any(marker in lower for marker in markers):
                found.update({skill for skill in SKILL_TERMS if skill in lower})
            if len(found) >= 12:
                break
        return sorted(found)

    @staticmethod
    def _seniority(years: int | None, text: str) -> str | None:
        if years is not None:
            if years >= 8:
                return "senior"
            if years >= 3:
                return "mid"
            return "junior"
        if any(term in text for term in ["principal", "staff", "lead", "architect"]):
            return "senior"
        if "intern" in text or "entry level" in text:
            return "junior"
        return None

    @staticmethod
    def _summary(text: str, skills: list[str], seniority: str | None) -> str:
        compact = " ".join(text.split())
        summary = compact[:280]
        if skills:
            summary += f" Key requirements: {', '.join(skills[:6])}."
        if seniority:
            summary += f" Seniority: {seniority}."
        return summary

    @staticmethod
    def _looks_like_title(value: str) -> bool:
        if not value or len(value) < 3 or len(value) > 120:
            return False
        blocked = {"job description", "about us", "requirements", "responsibilities", "qualifications"}
        if value.lower() in blocked:
            return False
        if value.endswith("."):
            return False
        words = value.split()
        return 1 <= len(words) <= 9

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

    @staticmethod
    def _preprocess_jd(text: str) -> str:
        """Remove noise from JD text before parsing and embedding."""
        lines = text.splitlines()
        cleaned_lines = []
        skip_section = False
        skip_patterns = [
            r"(?i)^(copyright|©|all rights reserved)",
            r"(?i)^(disclaimer|confidential|proprietary)",
            r"(?i)^(troubleshooting|support|help|faq)",
            r"(?i)^(instructions|guidance|guidelines)",
            r"(?i)^(do not|don't|please note)",
            r"(?i)^(assessment logistics|test instructions)",
            r"(?i)^(contact us|support contact|email us)",
            r"(?i)^(browser requirements|system requirements)",
            r"(?i)^(malpractice|legal|terms of service)",
        ]
        keep_patterns = [
            r"(?i)(job|role|position|title)",
            r"(?i)(responsibilities|duties|what you'll do)",
            r"(?i)(requirements|qualifications|what we're looking for)",
            r"(?i)(skills|technologies|stack)",
            r"(?i)(experience|years)",
            r"(?i)(education|degree)",
            r"(?i)(benefits|perks)",
        ]
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Check if we should skip this section
            if any(re.match(pattern, stripped) for pattern in skip_patterns):
                skip_section = True
                continue
            
            # Check if we should keep this line
            if skip_section:
                # Exit skip section if we hit a keep pattern
                if any(re.search(pattern, stripped) for pattern in keep_patterns):
                    skip_section = False
                    cleaned_lines.append(stripped)
                continue
            
            # Remove repeated boilerplate
            if len(stripped) < 10:
                continue
            
            # Remove lines that are mostly boilerplate
            if stripped.count(" ") > len(stripped) * 0.8:
                continue
            
            cleaned_lines.append(stripped)
        
        # Remove duplicate lines
        seen = set()
        unique_lines = []
        for line in cleaned_lines:
            if line.lower() not in seen:
                seen.add(line.lower())
                unique_lines.append(line)
        
        return "\n".join(unique_lines)
