from uuid import UUID

from pydantic import BaseModel, Field


class ATSScoreComponent(BaseModel):
    name: str
    score: float
    weight: float
    evidence: list[str]


class ATSScoreRead(BaseModel):
    candidate_id: UUID
    job_description_id: UUID
    resume_id: UUID
    ats_score: float
    components: list[ATSScoreComponent] = Field(default_factory=list)
    issues: list[str]
    recommendations: list[str]
    explanation: str | None = None
