from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampedUUIDModel


class ResumeStatus(StrEnum):
    uploaded = "uploaded"
    parsing = "parsing"
    parsed = "parsed"
    failed = "failed"


class Organization(TimestampedUUIDModel):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255), unique=True)


class User(TimestampedUUIDModel):
    __tablename__ = "users"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Candidate(TimestampedUUIDModel):
    __tablename__ = "candidate_profiles"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), index=True)
    email: Mapped[str | None] = mapped_column(String(320), index=True)
    phone: Mapped[str | None] = mapped_column(String(64), index=True)
    location: Mapped[str | None] = mapped_column(String(255))
    headline: Mapped[str | None] = mapped_column(String(255))
    summary: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(100))
    raw_profile: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    __table_args__ = (
        Index("ix_candidate_profiles_org_email", "organization_id", "email"),
        Index("ix_candidate_profiles_org_phone", "organization_id", "phone"),
    )


class Resume(TimestampedUUIDModel):
    __tablename__ = "resumes"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    candidate_id: Mapped[UUID | None] = mapped_column(ForeignKey("candidate_profiles.id"), index=True)
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

    candidate: Mapped[Candidate | None] = relationship()

    __table_args__ = (Index("ix_resumes_org_checksum", "organization_id", "checksum_sha256"),)


class ResumeProcessingEvent(TimestampedUUIDModel):
    __tablename__ = "resume_processing_events"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    resume_id: Mapped[UUID] = mapped_column(ForeignKey("resumes.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)


class CandidateSkill(TimestampedUUIDModel):
    __tablename__ = "candidate_skills"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("candidate_profiles.id"), index=True)
    normalized_skill: Mapped[str] = mapped_column(String(150), index=True)
    raw_skill: Mapped[str | None] = mapped_column(String(150))
    confidence: Mapped[float] = mapped_column(Numeric(5, 4), default=0)

    __table_args__ = (
        UniqueConstraint("candidate_id", "normalized_skill", name="uq_candidate_skill_candidate_skill"),
    )


class CandidateFeature(TimestampedUUIDModel):
    __tablename__ = "candidate_features"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("candidate_profiles.id"), index=True)
    feature_set_version: Mapped[str] = mapped_column(String(64))
    features: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    __table_args__ = (
        UniqueConstraint("candidate_id", "feature_set_version", name="uq_candidate_feature_version"),
    )


class Job(TimestampedUUIDModel):
    __tablename__ = "jobs"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    created_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    required_skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    optional_skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)


class RankingRun(TimestampedUUIDModel):
    __tablename__ = "ranking_runs"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), index=True)
    model_name: Mapped[str] = mapped_column(String(255))
    model_version: Mapped[str] = mapped_column(String(64))
    candidates_ranked: Mapped[int] = mapped_column(Integer, default=0)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    explanation: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)


class RecruiterNote(TimestampedUUIDModel):
    __tablename__ = "recruiter_notes"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("candidate_profiles.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text)


class HiringPipelineStage(TimestampedUUIDModel):
    __tablename__ = "hiring_pipeline_stages"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("candidate_profiles.id"), index=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), index=True)
    stage: Mapped[str] = mapped_column(String(100), index=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
