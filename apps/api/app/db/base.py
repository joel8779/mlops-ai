from app.models.base import Base
from app.models.domain import (  # noqa: F401
    Candidate,
    CandidateEmbedding,
    CandidateBookmark,
    CandidateMatch,
    CandidatePipelineStage,
    CandidateSkill,
    ATSScore,
    APIKey,
    AnalyticsSnapshot,
    AuditLog,
    JobDescription,
    JobDescriptionEmbedding,
    LLMUsageLog,
    Organization,
    RecruiterNote,
    RecruiterActivity,
    RecruiterConversation,
    RecruiterMessage,
    RankingFeedback,
    Resume,
    ResumeProcessingEvent,
    TenantQuota,
    User,
)

__all__ = ["Base"]
