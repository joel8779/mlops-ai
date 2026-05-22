from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.domain import ResumeStatus


class ResumeUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: ResumeStatus
    original_filename: str
    checksum_sha256: str


class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID | None
    original_filename: str
    content_type: str
    status: ResumeStatus
    parse_error: str | None
    created_at: datetime
    updated_at: datetime
