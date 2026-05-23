from uuid import UUID

from pydantic import BaseModel


class ATSScoreRead(BaseModel):
    resume_id: UUID
    ats_score: float
    issues: list[str]
    recommendations: list[str]
