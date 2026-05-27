from uuid import UUID

from pydantic import BaseModel, Field

from app.models.domain import FeedbackAction


class RankingFeedbackCreate(BaseModel):
    candidate_id: UUID
    job_description_id: UUID | None = None
    action: FeedbackAction
    rank_position: int | None = Field(default=None, ge=0)
    model_version: str | None = None
    feature_snapshot: dict = Field(default_factory=dict)


class RankingFeedbackRead(BaseModel):
    candidate_id: UUID
    job_description_id: UUID | None
    action: FeedbackAction
    reward: float
    model_version: str | None
    feature_snapshot: dict = Field(default_factory=dict)

    model_config = {"from_attributes": True}
