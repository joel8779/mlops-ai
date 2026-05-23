from uuid import UUID

from pydantic import BaseModel, Field


class AISummaryRequest(BaseModel):
    candidate_id: UUID


class InterviewQuestionRequest(BaseModel):
    candidate_id: UUID
    job_description_id: UUID | None = None
    count: int = Field(default=8, ge=3, le=15)


class CandidateComparisonRequest(BaseModel):
    candidate_ids: list[UUID] = Field(min_length=2, max_length=5)
    job_description_id: UUID | None = None


class CopilotRequest(BaseModel):
    query: str = Field(min_length=3)
    top_k: int = Field(default=8, ge=1, le=20)
    context: dict = Field(default_factory=dict)


class AIResponse(BaseModel):
    answer: str
    citations: list[dict] = Field(default_factory=list)
    usage: dict = Field(default_factory=dict)


class Copilot2Response(BaseModel):
    answer: str
    confidence: float
    artifacts: dict = Field(default_factory=dict)
