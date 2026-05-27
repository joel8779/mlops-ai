from enum import StrEnum
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampedUUIDModel


class ResumeStatus(StrEnum):
    uploaded = "uploaded"
    queued = "queued"
    parsing = "parsing"
    parsed = "parsed"
    embedded = "embedded"
    failed = "failed"


class JobStatus(StrEnum):
    draft = "draft"
    active = "active"
    closed = "closed"


class PipelineStage(StrEnum):
    # Ingestion stages
    uploaded = "uploaded"
    queued = "queued"
    parsing = "parsing"
    parsed = "parsed"
    embedding = "embedding"
    summarizing = "summarizing"
    indexed = "indexed"
    completed = "completed"
    failed = "failed"
    # Recruiting workflow stages
    ranked = "ranked"
    shortlisted = "shortlisted"
    interviewing = "interviewing"
    rejected = "rejected"
    hired = "hired"


class FeedbackAction(StrEnum):
    shortlist = "shortlist"
    reject = "reject"
    interview = "interview"
    hire = "hire"


class SubscriptionTier(StrEnum):
    free = "free"
    growth = "growth"
    enterprise = "enterprise"


class Organization(TimestampedUUIDModel):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    external_id: Mapped[str | None] = mapped_column(String(255), unique=True)

    users: Mapped[list["User"]] = relationship(back_populates="organization")
    candidates: Mapped[list["Candidate"]] = relationship(back_populates="organization")


class User(TimestampedUUIDModel):
    __tablename__ = "users"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255))
    roles: Mapped[list[str]] = mapped_column(JSONB, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    organization: Mapped[Organization] = relationship(back_populates="users")
    resumes_uploaded: Mapped[list["Resume"]] = relationship(foreign_keys="[Resume.uploaded_by_user_id]", back_populates="uploaded_by")
    owned_resumes: Mapped[list["Resume"]] = relationship(foreign_keys="[Resume.owner_id]", back_populates="owner")
    owned_candidates: Mapped[list["Candidate"]] = relationship(foreign_keys="[Candidate.owner_id]", back_populates="owner")
    owned_job_descriptions: Mapped[list["JobDescription"]] = relationship(foreign_keys="[JobDescription.owner_id]", back_populates="owner")
    created_job_descriptions: Mapped[list["JobDescription"]] = relationship(foreign_keys="[JobDescription.created_by_user_id]", back_populates="created_by")
    owned_job_description_embeddings: Mapped[list["JobDescriptionEmbedding"]] = relationship(foreign_keys="[JobDescriptionEmbedding.owner_id]", back_populates="owner")
    owned_candidate_embeddings: Mapped[list["CandidateEmbedding"]] = relationship(foreign_keys="[CandidateEmbedding.owner_id]", back_populates="owner")
    owned_candidate_skills: Mapped[list["CandidateSkill"]] = relationship(foreign_keys="[CandidateSkill.owner_id]", back_populates="owner")
    owned_recruiter_notes: Mapped[list["RecruiterNote"]] = relationship(foreign_keys="[RecruiterNote.owner_id]", back_populates="owner")
    authored_recruiter_notes: Mapped[list["RecruiterNote"]] = relationship(foreign_keys="[RecruiterNote.user_id]", back_populates="user")
    owned_pipeline_stages: Mapped[list["CandidatePipelineStage"]] = relationship(foreign_keys="[CandidatePipelineStage.owner_id]", back_populates="owner")
    owned_candidate_bookmarks: Mapped[list["CandidateBookmark"]] = relationship(foreign_keys="[CandidateBookmark.owner_id]", back_populates="owner")
    candidate_bookmarks: Mapped[list["CandidateBookmark"]] = relationship(foreign_keys="[CandidateBookmark.user_id]", back_populates="user")
    owned_activities: Mapped[list["RecruiterActivity"]] = relationship(foreign_keys="[RecruiterActivity.owner_id]", back_populates="owner")
    activities: Mapped[list["RecruiterActivity"]] = relationship(foreign_keys="[RecruiterActivity.user_id]", back_populates="user")
    owned_matches: Mapped[list["CandidateMatch"]] = relationship(foreign_keys="[CandidateMatch.owner_id]", back_populates="owner")
    owned_feedback: Mapped[list["RankingFeedback"]] = relationship(foreign_keys="[RankingFeedback.owner_id]", back_populates="owner")
    submitted_feedback: Mapped[list["RankingFeedback"]] = relationship(foreign_keys="[RankingFeedback.user_id]", back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship(foreign_keys="[AuditLog.user_id]", back_populates="user")
    analytics_snapshots: Mapped[list["AnalyticsSnapshot"]] = relationship(foreign_keys="[AnalyticsSnapshot.owner_id]", back_populates="owner")
    owned_ats_scores: Mapped[list["ATSScore"]] = relationship(foreign_keys="[ATSScore.owner_id]", back_populates="owner")
    owned_llm_usage_logs: Mapped[list["LLMUsageLog"]] = relationship(foreign_keys="[LLMUsageLog.owner_id]", back_populates="owner")
    llm_usage_logs: Mapped[list["LLMUsageLog"]] = relationship(foreign_keys="[LLMUsageLog.user_id]", back_populates="user")
    owned_resume_processing_events: Mapped[list["ResumeProcessingEvent"]] = relationship(foreign_keys="[ResumeProcessingEvent.owner_id]", back_populates="owner")
    conversations: Mapped[list["RecruiterConversation"]] = relationship(foreign_keys="[RecruiterConversation.user_id]", back_populates="user")


class Candidate(TimestampedUUIDModel):
    __tablename__ = "candidates"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), index=True)
    email: Mapped[str | None] = mapped_column(String(320), index=True)
    phone: Mapped[str | None] = mapped_column(String(64), index=True)
    location: Mapped[str | None] = mapped_column(String(255))
    headline: Mapped[str | None] = mapped_column(String(255))
    summary: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(100))
    raw_profile: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    organization: Mapped[Organization] = relationship(back_populates="candidates")
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_candidates")
    resumes: Mapped[list["Resume"]] = relationship(back_populates="candidate")
    skills: Mapped[list["CandidateSkill"]] = relationship(back_populates="candidate")
    embeddings: Mapped[list["CandidateEmbedding"]] = relationship(back_populates="candidate")
    notes: Mapped[list["RecruiterNote"]] = relationship(back_populates="candidate")
    pipeline_stages: Mapped[list["CandidatePipelineStage"]] = relationship(back_populates="candidate")
    bookmarks: Mapped[list["CandidateBookmark"]] = relationship(back_populates="candidate")
    activities: Mapped[list["RecruiterActivity"]] = relationship(back_populates="candidate")
    matches: Mapped[list["CandidateMatch"]] = relationship(back_populates="candidate")
    feedback: Mapped[list["RankingFeedback"]] = relationship(back_populates="candidate")
    ats_scores: Mapped[list["ATSScore"]] = relationship(back_populates="candidate")

    __table_args__ = (
        Index("ix_candidates_owner_created", "owner_id", "created_at"),
        Index("ix_candidates_org_email", "organization_id", "email"),
        Index("ix_candidates_org_phone", "organization_id", "phone"),
    )


class Resume(TimestampedUUIDModel):
    __tablename__ = "resumes"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    candidate_id: Mapped[UUID | None] = mapped_column(ForeignKey("candidates.id"), index=True)
    uploaded_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    original_filename: Mapped[str] = mapped_column(String(512))
    content_type: Mapped[str] = mapped_column(String(128))
    storage_key: Mapped[str] = mapped_column(String(1024), unique=True)
    checksum_sha256: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[ResumeStatus] = mapped_column(Enum(ResumeStatus), default=ResumeStatus.uploaded)
    extracted_text: Mapped[str | None] = mapped_column(Text)
    parse_error: Mapped[str | None] = mapped_column(Text)
    parser_version: Mapped[str | None] = mapped_column(String(64))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    candidate: Mapped[Optional["Candidate"]] = relationship(back_populates="resumes")
    uploaded_by: Mapped["User"] = relationship(foreign_keys=[uploaded_by_user_id], back_populates="resumes_uploaded")
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_resumes")
    embeddings: Mapped[list["CandidateEmbedding"]] = relationship(back_populates="resume")
    ats_scores: Mapped[list["ATSScore"]] = relationship(back_populates="resume")
    processing_events: Mapped[list["ResumeProcessingEvent"]] = relationship(back_populates="resume")

    __table_args__ = (Index("ix_resumes_org_checksum", "organization_id", "checksum_sha256"),)


class JobDescription(TimestampedUUIDModel):
    __tablename__ = "job_descriptions"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    created_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.draft, index=True)
    role_category: Mapped[str | None] = mapped_column(String(150), index=True)
    years_experience_min: Mapped[int | None] = mapped_column(Integer)
    years_experience_max: Mapped[int | None] = mapped_column(Integer)
    education_requirements: Mapped[list[str]] = mapped_column(JSONB, default=list)
    keywords: Mapped[list[str]] = mapped_column(JSONB, default=list)
    required_skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    optional_skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_job_descriptions")
    created_by: Mapped["User"] = relationship(foreign_keys=[created_by_user_id], back_populates="created_job_descriptions")
    embeddings: Mapped[list["JobDescriptionEmbedding"]] = relationship(back_populates="job_description")
    pipeline_stages: Mapped[list["CandidatePipelineStage"]] = relationship(back_populates="job_description")
    activities: Mapped[list["RecruiterActivity"]] = relationship(back_populates="job_description")
    matches: Mapped[list["CandidateMatch"]] = relationship(back_populates="job_description")
    feedback: Mapped[list["RankingFeedback"]] = relationship(back_populates="job_description")
    ats_scores: Mapped[list["ATSScore"]] = relationship(back_populates="job_description")


class JobDescriptionEmbedding(TimestampedUUIDModel):
    __tablename__ = "job_description_embeddings"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    job_description_id: Mapped[UUID] = mapped_column(ForeignKey("job_descriptions.id"), index=True)
    qdrant_point_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    model_name: Mapped[str] = mapped_column(String(255), index=True)
    vector_size: Mapped[int] = mapped_column(Integer)
    chunk_index: Mapped[int] = mapped_column(Integer)
    chunk_text: Mapped[str] = mapped_column(Text)

    job_description: Mapped["JobDescription"] = relationship(back_populates="embeddings")
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_job_description_embeddings")

    __table_args__ = (
        UniqueConstraint("job_description_id", "chunk_index", name="uq_jd_embeddings_jd_chunk"),
    )


class CandidateEmbedding(TimestampedUUIDModel):
    __tablename__ = "candidate_embeddings"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("candidates.id"), index=True)
    resume_id: Mapped[UUID | None] = mapped_column(ForeignKey("resumes.id"), index=True)
    qdrant_point_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    model_name: Mapped[str] = mapped_column(String(255), index=True)
    vector_size: Mapped[int] = mapped_column(Integer)
    chunk_index: Mapped[int] = mapped_column(Integer)
    chunk_text: Mapped[str] = mapped_column(Text)

    candidate: Mapped["Candidate"] = relationship(back_populates="embeddings")
    resume: Mapped[Optional["Resume"]] = relationship(back_populates="embeddings")
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_candidate_embeddings")

    __table_args__ = (
        UniqueConstraint("resume_id", "chunk_index", name="uq_candidate_embeddings_resume_chunk"),
    )


class CandidateSkill(TimestampedUUIDModel):
    __tablename__ = "candidate_skills"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("candidates.id"), index=True)
    normalized_skill: Mapped[str] = mapped_column(String(150), index=True)
    raw_skill: Mapped[str | None] = mapped_column(String(150))
    confidence: Mapped[float] = mapped_column(Numeric(5, 4), default=0)

    candidate: Mapped["Candidate"] = relationship(back_populates="skills")
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_candidate_skills")

    __table_args__ = (
        UniqueConstraint("candidate_id", "normalized_skill", name="uq_candidate_skill_candidate_skill"),
    )


class RecruiterNote(TimestampedUUIDModel):
    __tablename__ = "recruiter_notes"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("candidates.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text)

    candidate: Mapped["Candidate"] = relationship(back_populates="notes")
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_recruiter_notes")
    user: Mapped["User"] = relationship(foreign_keys=[user_id], back_populates="authored_recruiter_notes")


class CandidatePipelineStage(TimestampedUUIDModel):
    __tablename__ = "candidate_pipeline_stages"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("candidates.id"), index=True)
    job_description_id: Mapped[UUID | None] = mapped_column(ForeignKey("job_descriptions.id"), index=True)
    stage: Mapped[PipelineStage] = mapped_column(
        Enum(PipelineStage, values_callable=lambda values: [item.value for item in values]),
        default=PipelineStage.uploaded,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    candidate: Mapped["Candidate"] = relationship(back_populates="pipeline_stages")
    job_description: Mapped[Optional["JobDescription"]] = relationship(back_populates="pipeline_stages")
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_pipeline_stages")


class CandidateBookmark(TimestampedUUIDModel):
    __tablename__ = "candidate_bookmarks"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("candidates.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)

    candidate: Mapped["Candidate"] = relationship(back_populates="bookmarks")
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_candidate_bookmarks")
    user: Mapped["User"] = relationship(foreign_keys=[user_id], back_populates="candidate_bookmarks")

    __table_args__ = (UniqueConstraint("candidate_id", "user_id", name="uq_candidate_bookmark_user"),)


class RecruiterActivity(TimestampedUUIDModel):
    __tablename__ = "recruiter_activities"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    candidate_id: Mapped[UUID | None] = mapped_column(ForeignKey("candidates.id"), index=True)
    job_description_id: Mapped[UUID | None] = mapped_column(ForeignKey("job_descriptions.id"), index=True)
    activity_type: Mapped[str] = mapped_column(String(100), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    candidate: Mapped[Optional["Candidate"]] = relationship(back_populates="activities")
    job_description: Mapped[Optional["JobDescription"]] = relationship(back_populates="activities")
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_activities")
    user: Mapped["User"] = relationship(foreign_keys=[user_id], back_populates="activities")


class CandidateMatch(TimestampedUUIDModel):
    __tablename__ = "candidate_matches"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("candidates.id"), index=True)
    job_description_id: Mapped[UUID] = mapped_column(ForeignKey("job_descriptions.id"), index=True)
    overall_score: Mapped[float] = mapped_column(Numeric(6, 2), index=True)
    semantic_score: Mapped[float] = mapped_column(Numeric(6, 2))
    skill_match: Mapped[float] = mapped_column(Numeric(6, 2))
    experience_match: Mapped[float] = mapped_column(Numeric(6, 2))
    education_match: Mapped[float] = mapped_column(Numeric(6, 2))
    keyword_score: Mapped[float] = mapped_column(Numeric(6, 2))
    matched_skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    missing_skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    explanation: Mapped[str] = mapped_column(Text)
    scoring_version: Mapped[str] = mapped_column(String(64), default="hybrid-v1")

    candidate: Mapped["Candidate"] = relationship(back_populates="matches")
    job_description: Mapped["JobDescription"] = relationship(back_populates="matches")
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_matches")

    __table_args__ = (
        UniqueConstraint("candidate_id", "job_description_id", name="uq_candidate_match_job"),
        Index("ix_candidate_matches_job_score", "job_description_id", "overall_score"),
    )


class RankingFeedback(TimestampedUUIDModel):
    __tablename__ = "ranking_feedback"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("candidates.id"), index=True)
    job_description_id: Mapped[UUID | None] = mapped_column(ForeignKey("job_descriptions.id"), index=True)
    action: Mapped[FeedbackAction] = mapped_column(Enum(FeedbackAction), index=True)
    reward: Mapped[float] = mapped_column(Numeric(5, 2), index=True)
    rank_position: Mapped[int | None] = mapped_column(Integer)
    model_version: Mapped[str | None] = mapped_column(String(120), index=True)
    feature_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    candidate: Mapped["Candidate"] = relationship(back_populates="feedback")
    job_description: Mapped[Optional["JobDescription"]] = relationship(back_populates="feedback")
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_feedback")
    user: Mapped["User"] = relationship(foreign_keys=[user_id], back_populates="submitted_feedback")


class AuditLog(TimestampedUUIDModel):
    __tablename__ = "audit_logs"

    organization_id: Mapped[UUID | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    resource_type: Mapped[str] = mapped_column(String(120), index=True)
    resource_id: Mapped[str | None] = mapped_column(String(120), index=True)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(512))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    user: Mapped[Optional["User"]] = relationship(foreign_keys=[user_id], back_populates="audit_logs")


class APIKey(TimestampedUUIDModel):
    __tablename__ = "api_keys"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    key_prefix: Mapped[str] = mapped_column(String(16), index=True)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True)
    scopes: Mapped[list[str]] = mapped_column(JSONB, default=list)
    last_used_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))

    organization: Mapped[Organization] = relationship()


class TenantQuota(TimestampedUUIDModel):
    __tablename__ = "tenant_quotas"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), unique=True, index=True)
    tier: Mapped[SubscriptionTier] = mapped_column(Enum(SubscriptionTier), default=SubscriptionTier.free)
    monthly_resume_limit: Mapped[int] = mapped_column(Integer, default=500)
    monthly_llm_token_limit: Mapped[int] = mapped_column(Integer, default=250000)
    monthly_vector_query_limit: Mapped[int] = mapped_column(Integer, default=10000)
    usage_counters: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    organization: Mapped[Organization] = relationship()


class RecruiterConversation(TimestampedUUIDModel):
    __tablename__ = "recruiter_conversations"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    memory: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    user: Mapped["User"] = relationship(foreign_keys=[user_id], back_populates="conversations")
    messages: Mapped[list["RecruiterMessage"]] = relationship(back_populates="conversation")


class RecruiterMessage(TimestampedUUIDModel):
    __tablename__ = "recruiter_messages"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("recruiter_conversations.id"), index=True)
    role: Mapped[str] = mapped_column(String(30), index=True)
    content: Mapped[str] = mapped_column(Text)
    citations: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)

    conversation: Mapped[RecruiterConversation] = relationship(back_populates="messages")


class AnalyticsSnapshot(TimestampedUUIDModel):
    __tablename__ = "analytics_snapshots"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    snapshot_type: Mapped[str] = mapped_column(String(100), index=True)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="analytics_snapshots")


class ATSScore(TimestampedUUIDModel):
    __tablename__ = "ats_scores"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("candidates.id"), index=True)
    job_description_id: Mapped[UUID] = mapped_column(ForeignKey("job_descriptions.id"), index=True)
    resume_id: Mapped[UUID] = mapped_column(ForeignKey("resumes.id"), index=True)
    ats_score: Mapped[float] = mapped_column(Numeric(6, 2), index=True)
    components: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    issues: Mapped[list[str]] = mapped_column(JSONB, default=list)
    recommendations: Mapped[list[str]] = mapped_column(JSONB, default=list)
    explanation: Mapped[str | None] = mapped_column(Text)
    scoring_version: Mapped[str] = mapped_column(String(64), default="ats-job-context-v1")

    candidate: Mapped["Candidate"] = relationship(back_populates="ats_scores")
    job_description: Mapped["JobDescription"] = relationship(back_populates="ats_scores")
    resume: Mapped["Resume"] = relationship(back_populates="ats_scores")
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_ats_scores")

    __table_args__ = (
        UniqueConstraint("candidate_id", "job_description_id", name="uq_ats_score_candidate_job"),
        Index("ix_ats_scores_job_score", "job_description_id", "ats_score"),
    )


class LLMUsageLog(TimestampedUUIDModel):
    __tablename__ = "llm_usage_logs"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[str] = mapped_column(String(50), index=True)
    model: Mapped[str] = mapped_column(String(120), index=True)
    feature: Mapped[str] = mapped_column(String(100), index=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Numeric(10, 6), default=0)

    owner: Mapped[Optional["User"]] = relationship(foreign_keys=[owner_id], back_populates="owned_llm_usage_logs")
    user: Mapped[Optional["User"]] = relationship(foreign_keys=[user_id], back_populates="llm_usage_logs")


class ResumeProcessingEvent(TimestampedUUIDModel):
    __tablename__ = "resume_processing_events"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    resume_id: Mapped[UUID] = mapped_column(ForeignKey("resumes.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    resume: Mapped["Resume"] = relationship(back_populates="processing_events")
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_resume_processing_events")
