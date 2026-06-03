from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.domain import JobStatus


class JobDescriptionCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=20)
    status: JobStatus = JobStatus.active


class JobDescriptionRead(BaseModel):
    id: UUID
    title: str
    description: str
    status: JobStatus
    role_category: str | None
    years_experience_min: int | None
    years_experience_max: int | None
    education_requirements: list[str]
    required_skills: list[str]
    optional_skills: list[str]
    keywords: list[str]
    metadata_json: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class JobCandidateRankingItem(BaseModel):
    candidate_id: UUID
    full_name: str | None
    email: str | None
    headline: str | None
    location: str | None
    latest_resume_id: UUID | None
    ats_score: float | None = None
    overall_score: float
    semantic_score: float
    skill_match: float
    experience_match: float
    education_match: float
    keyword_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str
    current_stage: str | None = None


class JobIntelligenceRead(BaseModel):
    job: JobDescriptionRead
    ranked_candidates: list[JobCandidateRankingItem]
    semantic_insights: dict


class JobParseResult(BaseModel):
    skills: list[str]
    preferred_skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    years_experience_min: int | None
    years_experience_max: int | None
    education_requirements: list[str]
    keywords: list[str]
    role_category: str | None
    seniority: str | None = None
    summary: str | None = None


class JobExtractionPreview(BaseModel):
    title: str | None
    description: str
    role_category: str | None
    years_experience_min: int | None
    years_experience_max: int | None
    education_requirements: list[str]
    required_skills: list[str]
    optional_skills: list[str]
    keywords: list[str]
    semantic_requirements: list[str]
    extraction_metadata: dict
    warnings: list[str] = Field(default_factory=list)
