from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class CandidateListItem(BaseModel):
    id: UUID
    full_name: str | None
    email: str | None
    headline: str | None
    location: str | None
    summary: str | None
    skills: list[str]
    latest_resume_id: UUID | None = None
    latest_resume_status: str | None = None
    current_stage: str | None = None
    best_match_score: float | None = None
    created_at: datetime


class CandidateRead(CandidateListItem):
    raw_profile: dict
    resume_text_preview: str | None = None


class CandidateIdentityUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
