from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class WorkspaceCounts(BaseModel):
    candidates: int = 0
    jobs: int = 0
    resumes: int = 0
    embedded_resumes: int = 0
    ats_scores: int = 0
    semantic_matches: int = 0
    activities: int = 0


class PipelineState(BaseModel):
    uploaded: int = 0
    queued: int = 0
    parsing: int = 0
    parsed: int = 0
    embedded: int = 0
    failed: int = 0


class ActivityEvent(BaseModel):
    id: UUID
    event_type: str
    label: str
    source: str
    candidate_id: UUID | None = None
    job_description_id: UUID | None = None
    resume_id: UUID | None = None
    payload: dict
    created_at: datetime


class MatchInsight(BaseModel):
    candidate_id: UUID
    job_description_id: UUID
    candidate_name: str | None = None
    job_title: str | None = None
    overall_score: float
    semantic_score: float
    matched_skills: list[str]
    explanation: str


class WorkspaceActivationResponse(BaseModel):
    activated: bool
    activation_reason: str
    counts: WorkspaceCounts
    pipeline: PipelineState
    activity: list[ActivityEvent]
    match_insights: list[MatchInsight]
    recommendations: list[str]


class DemoWorkspaceResponse(BaseModel):
    status: str
    message: str
    activation: WorkspaceActivationResponse
