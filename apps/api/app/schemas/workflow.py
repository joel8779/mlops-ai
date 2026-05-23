from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.domain import PipelineStage


class StageUpdateRequest(BaseModel):
    candidate_id: UUID
    job_description_id: UUID | None = None
    stage: PipelineStage
    position: int = Field(default=0, ge=0)


class StageUpdateResponse(BaseModel):
    candidate_id: UUID
    job_description_id: UUID | None
    stage: PipelineStage
    position: int
    updated_at: datetime


class RecruiterNoteCreate(BaseModel):
    candidate_id: UUID
    body: str = Field(min_length=1, max_length=5000)


class RecruiterNoteResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    user_id: UUID
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}


class BookmarkResponse(BaseModel):
    candidate_id: UUID
    user_id: UUID
    bookmarked: bool
    created_at: datetime


class WorkflowActivityRead(BaseModel):
    id: UUID
    activity_type: str
    candidate_id: UUID | None
    job_description_id: UUID | None
    payload: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class HiringAnalytics(BaseModel):
    total_candidates: int
    by_stage: dict[str, int]
    bookmarked: int
    notes: int
