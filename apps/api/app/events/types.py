from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class EventType(StrEnum):
    resume_uploaded = "resume_uploaded"
    resume_parsed = "resume_parsed"
    embedding_generated = "embedding_generated"
    candidate_ranked = "candidate_ranked"
    recruiter_action = "recruiter_action"
    drift_detected = "drift_detected"


class DomainEvent(BaseModel):
    type: EventType
    organization_id: UUID
    aggregate_id: UUID | None = None
    payload: dict = Field(default_factory=dict)
    correlation_id: str | None = None
