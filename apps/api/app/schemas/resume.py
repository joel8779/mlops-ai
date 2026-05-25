from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.domain import ResumeStatus


class ResumeUploadResponse(BaseModel):
    id: UUID
    status: ResumeStatus
    original_filename: str
    content_type: str

    model_config = {"from_attributes": True}


class ResumeRead(BaseModel):
    id: UUID
    candidate_id: UUID | None
    original_filename: str
    content_type: str
    status: ResumeStatus
    parse_error: str | None = None
    parser_version: str | None
    metadata_json: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
