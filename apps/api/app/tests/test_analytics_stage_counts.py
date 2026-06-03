import pytest
from datetime import datetime, timedelta

from app.models.domain import (
    ATSScore,
    Candidate,
    CandidateMatch,
    CandidatePipelineStage,
    CandidateSkill,
    JobDescription,
    Organization,
    PipelineStage,
    Resume,
    ResumeStatus,
    User,
)
from app.schemas.auth import AuthContext
from app.analytics.analytics_service import AnalyticsService
from app.analytics.pipelines import AnalyticsPipeline


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
    test_db.add_all([organization, user])
    await test_db.flush()

    candidate = Candidate(
        organization=organization,
        owner_id=user.id,
        full_name="Bob Candidate",
        email="bob@example.com",
    )
    test_db.add(candidate)
    await test_db.flush()

    now = datetime.utcnow()
    earlier = now - timedelta(minutes=5)

    stage_uploaded = CandidatePipelineStage(
        organization_id=organization.id,
        owner_id=user.id,
        candidate_id=candidate.id,
        stage=PipelineStage.uploaded,
        updated_at=earlier,
    )
    stage_parsed = CandidatePipelineStage(
        organization_id=organization.id,
        owner_id=user.id,
        candidate_id=candidate.id,
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


@pytest.mark.asyncio
async def test_deleted_rows_are_excluded_from_analytics(test_db, mock_env_vars):
    organization = Organization(name="Test Org", slug="test-org")
    user = User(
        organization=organization,
        email="user@example.com",
        hashed_password="hashed",
        full_name="Test User",
        roles=["recruiter"],
        is_active=True,
    )
    test_db.add_all([organization, user])
    await test_db.flush()

    candidate = Candidate(
        organization=organization,
        owner_id=user.id,
        full_name="Bob Candidate",
        email="bob@example.com",
    )
    job = JobDescription(
        organization_id=organization.id,
        owner_id=user.id,
        created_by_user_id=user.id,
        title="Backend Engineer",
        description="Build Python APIs.",
        status="active",
    )
    deleted_job = JobDescription(
        organization_id=organization.id,
        owner_id=user.id,
        created_by_user_id=user.id,
        title="Data Engineer",
        description="Build analytics pipelines.",
        status="active",
    )
    resume = Resume(
        organization_id=organization.id,
        owner_id=user.id,
        candidate=candidate,
        uploaded_by_user_id=user.id,
        original_filename="resume.pdf",
        content_type="application/pdf",
        storage_key="resume-analytics",
        checksum_sha256="analytics-checksum",
        status=ResumeStatus.parsed,
        extracted_text="Senior Python engineer with 5 years of experience.",
    )
    test_db.add_all([candidate, job, deleted_job, resume])
    await test_db.flush()

    active_match = CandidateMatch(
        organization_id=organization.id,
        owner_id=user.id,
        candidate_id=candidate.id,
        job_description_id=job.id,
        overall_score=91.0,
        semantic_score=88.0,
        skill_match=80.0,
        experience_match=79.0,
        education_match=65.0,
        keyword_score=70.0,
        matched_skills=["python"],
        missing_skills=[],
        explanation="Active match",
        scoring_version="v1",
    )
    deleted_match = CandidateMatch(
        organization_id=organization.id,
        owner_id=user.id,
        candidate_id=candidate.id,
        job_description_id=deleted_job.id,
        overall_score=50.0,
        semantic_score=40.0,
        skill_match=30.0,
        experience_match=20.0,
        education_match=10.0,
        keyword_score=15.0,
        matched_skills=[],
        missing_skills=["python"],
        explanation="Deleted match",
        scoring_version="v1",
        deleted_at=datetime.utcnow(),
    )
    active_score = ATSScore(
        organization_id=organization.id,
        owner_id=user.id,
        candidate_id=candidate.id,
        job_description_id=job.id,
        resume_id=resume.id,
        ats_score=88.0,
        components=[],
        issues=[],
        recommendations=[],
        explanation="Active score",
        scoring_version="v1",
    )
    deleted_score = ATSScore(
        organization_id=organization.id,
        owner_id=user.id,
        candidate_id=candidate.id,
        job_description_id=deleted_job.id,
        resume_id=resume.id,
        ats_score=40.0,
        components=[],
        issues=[],
        recommendations=[],
        explanation="Deleted score",
        scoring_version="v1",
        deleted_at=datetime.utcnow(),
    )

    test_db.add_all([organization, user, candidate, job, resume, active_match, deleted_match, active_score, deleted_score])
    await test_db.flush()
    await test_db.commit()

    auth = AuthContext(
        user_id=user.id,
        organization_id=organization.id,
        email=user.email,
        full_name=user.full_name,
        roles=user.roles,
    )

    service = AnalyticsService(test_db)

    assert await service.semantic_match_averages(auth) == [
        {
            "job_id": str(job.id),
            "job_title": "Backend Engineer",
            "average_semantic_score": 88.0,
            "average_overall_score": 91.0,
        }
    ]
    assert (await service.ats_score_distribution(auth))["75_89"] == 1


@pytest.mark.asyncio
async def test_compute_time_to_hire_uses_stage_timestamps(test_db, mock_env_vars):
    organization = Organization(name="Time Org", slug="time-org")
    user = User(
        organization=organization,
        email="time@example.com",
        hashed_password="hashed",
        full_name="Time User",
        roles=["recruiter"],
        is_active=True,
    )
    test_db.add_all([organization, user])
    await test_db.flush()
    candidate = Candidate(
        organization=organization,
        owner_id=user.id,
        full_name="Time Candidate",
        email="timecandidate@example.com",
    )
    test_db.add(candidate)
    await test_db.flush()

    uploaded_at = datetime.utcnow() - timedelta(days=10)
    completed_at = uploaded_at + timedelta(days=5)

    test_db.add_all([
        CandidatePipelineStage(
            organization_id=organization.id,
            owner_id=user.id,
            candidate_id=candidate.id,
            stage=PipelineStage.uploaded,
            created_at=uploaded_at,
            updated_at=uploaded_at,
        ),
        CandidatePipelineStage(
            organization_id=organization.id,
            owner_id=user.id,
            candidate_id=candidate.id,
            stage=PipelineStage.completed,
            created_at=completed_at,
            updated_at=completed_at,
        ),
    ])
    await test_db.commit()

    pipeline = AnalyticsPipeline(test_db)
    metrics = await pipeline.compute_time_to_hire(organization_id=organization.id)

    assert metrics["average_days"] == pytest.approx(5.0)
    assert metrics["median_days"] == pytest.approx(5.0)
    assert metrics["p25_days"] == pytest.approx(5.0)
    assert metrics["p75_days"] == pytest.approx(5.0)


@pytest.mark.asyncio
async def test_compute_skill_demand_trends_aggregates_normalized_skills(test_db, mock_env_vars):
    organization = Organization(name="Skill Org", slug="skill-org")
    user = User(
        organization=organization,
        email="skill@example.com",
        hashed_password="hashed",
        full_name="Skill User",
        roles=["recruiter"],
        is_active=True,
    )
    test_db.add_all([organization, user])
    await test_db.flush()
    candidate = Candidate(
        organization=organization,
        owner_id=user.id,
        full_name="Skill Candidate",
        email="skillcandidate@example.com",
    )
    test_db.add(candidate)
    await test_db.flush()

    recent_skill = CandidateSkill(
        organization_id=organization.id,
        owner_id=user.id,
        candidate_id=candidate.id,
        normalized_skill="python",
        raw_skill="Python",
        confidence=0.99,
        created_at=datetime.utcnow() - timedelta(days=1),
    )
    older_skill = CandidateSkill(
        organization_id=organization.id,
        owner_id=user.id,
        candidate_id=candidate.id,
        normalized_skill="aws",
        raw_skill="AWS",
        confidence=0.96,
        created_at=datetime.utcnow() - timedelta(days=120),
    )
    test_db.add_all([recent_skill, older_skill])
    await test_db.commit()

    pipeline = AnalyticsPipeline(test_db)
    trends = await pipeline.compute_skill_demand_trends(organization_id=organization.id)

    assert trends[0]["skill"] == "python"
    assert trends[0]["demand"] == 1
    assert trends[0]["trend"] == "+100%"


@pytest.mark.asyncio
async def test_same_org_dashboard_metrics_are_shared_across_users(test_db, mock_env_vars):
    organization = Organization(name="Shared Org", slug="shared-org")
    first_user = User(
        organization=organization,
        email="first@example.com",
        hashed_password="hashed",
        full_name="First User",
        roles=["recruiter"],
        is_active=True,
    )
    second_user = User(
        organization=organization,
        email="second@example.com",
        hashed_password="hashed",
        full_name="Second User",
        roles=["recruiter"],
        is_active=True,
    )
    test_db.add_all([organization, first_user, second_user])
    await test_db.flush()

    job = JobDescription(
        organization_id=organization.id,
        owner_id=first_user.id,
        created_by_user_id=first_user.id,
        title="Backend Engineer",
        description="Build Python APIs.",
        status="active",
    )
    candidate = Candidate(
        organization=organization,
        owner_id=second_user.id,
        full_name="Shared Candidate",
        email="shared@example.com",
    )
    test_db.add_all([job, candidate])
    await test_db.commit()

    service = AnalyticsService(test_db)
    first_auth = AuthContext(
        user_id=first_user.id,
        organization_id=organization.id,
        email=first_user.email,
        full_name=first_user.full_name,
        roles=first_user.roles,
    )
    second_auth = AuthContext(
        user_id=second_user.id,
        organization_id=organization.id,
        email=second_user.email,
        full_name=second_user.full_name,
        roles=second_user.roles,
    )

    first_dashboard = await service.executive_dashboard(first_auth)
    second_dashboard = await service.executive_dashboard(second_auth)

    assert first_dashboard["total_jobs"] == 1
    assert second_dashboard["total_jobs"] == 1
    assert first_dashboard["total_candidates"] == 1
    assert second_dashboard["total_candidates"] == 1
