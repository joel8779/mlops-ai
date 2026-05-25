from uuid import UUID

from pydantic import BaseModel, Field


class MatchingWeights(BaseModel):
    semantic: float = Field(default=0.40, ge=0, le=1)
    skill: float = Field(default=0.25, ge=0, le=1)
    experience: float = Field(default=0.15, ge=0, le=1)
    education: float = Field(default=0.10, ge=0, le=1)
    keyword: float = Field(default=0.10, ge=0, le=1)


class MatchRequest(BaseModel):
    job_description_id: UUID
    limit: int = Field(default=25, ge=1, le=100)
    weights: MatchingWeights | None = None
    recruiter_preferences: dict = Field(default_factory=dict)


class CandidateMatchRead(BaseModel):
    candidate_id: UUID
    overall_score: float
    semantic_score: float
    skill_match: float
    experience_match: float
    education_match: float
    keyword_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str


class SemanticSearchRequest(BaseModel):
    query: str = Field(min_length=2)
    job_description_id: UUID | None = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    min_years_experience: int | None = None
    skills: list[str] = Field(default_factory=list)
    location: str | None = None
    education: str | None = None
    uploaded_after: str | None = None


class SemanticSearchResult(BaseModel):
    candidate_id: UUID
    resume_id: UUID | None
    score: float
    snippet: str
    payload: dict


class CandidateSearchResult(BaseModel):
    candidate_id: UUID
    full_name: str | None
    headline: str | None
    location: str | None
    latest_resume_id: UUID | None
    semantic_score: float
    ats_alignment: float | None = None
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    experience_fit: float | None = None
    summary: str | None = None
    overlap_reasoning: str
