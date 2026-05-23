from uuid import UUID

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    candidate_ids: list[UUID] = Field(default_factory=list, max_length=100)
    skills: list[str] = Field(default_factory=list, max_length=30)
    limit: int = Field(default=10, ge=1, le=50)


class RecommendationItem(BaseModel):
    candidate_id: UUID
    score: float
    reasons: list[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem]
    diagnostics: dict = Field(default_factory=dict)


class SkillExpansionRequest(BaseModel):
    skills: list[str] = Field(min_length=1, max_length=30)


class SkillExpansionResponse(BaseModel):
    canonical_skills: list[str]
    expanded_skills: list[str]
    role_matches: list[str]
