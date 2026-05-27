import pytest
from datetime import datetime, timedelta

from app.models.domain import Candidate, CandidatePipelineStage, Organization, PipelineStage, User
from app.schemas.auth import AuthContext
from app.analytics.analytics_service import AnalyticsService


@pytest.mark.asyncio
async def test_pipeline_stage_counts_counts_only_latest_stage(test_db, mock_env_vars):
    organization = Organization(name="Test Org", slug="test-org")
    user = User(
        organization=organization,
        email="user@example.com",
        hashed_password="hashed",
        full_name="Test User",
        roles=["recruiter"],
        is_active=True,
    )
    candidate = Candidate(
        organization=organization,
        owner_id=user.id,
        full_name="Bob Candidate",
        email="bob@example.com",
    )

    now = datetime.utcnow()
    earlier = now - timedelta(minutes=5)

    stage_uploaded = CandidatePipelineStage(
        organization=organization,
        owner=user,
        candidate=candidate,
        stage=PipelineStage.uploaded,
        updated_at=earlier,
    )
    stage_parsed = CandidatePipelineStage(
        organization=organization,
        owner=user,
        candidate=candidate,
        stage=PipelineStage.parsed,
        updated_at=now,
    )

    test_db.add_all([organization, user, candidate, stage_uploaded, stage_parsed])
    await test_db.commit()

    auth = AuthContext(
        user_id=user.id,
        organization_id=organization.id,
        email=user.email,
        full_name=user.full_name,
        roles=user.roles,
    )

    service = AnalyticsService(test_db)
    counts = await service.pipeline_stage_counts(auth)
    funnel = await service.hiring_funnel(auth)

    assert counts == {"parsed": 1}
    assert funnel == {"parsed": 1}
