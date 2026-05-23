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
    created_at: datetime

    model_config = {"from_attributes": True}


class JobParseResult(BaseModel):
    skills: list[str]
    years_experience_min: int | None
    years_experience_max: int | None
    education_requirements: list[str]
    keywords: list[str]
    role_category: str | None
