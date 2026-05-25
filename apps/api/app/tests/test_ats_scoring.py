from uuid import uuid4

import pytest

from app.models.domain import Candidate, JobDescription, Resume
from app.services.ats_scoring_service import ATSScoringService


@pytest.mark.asyncio
async def test_ats_scoring_detects_sections():
    organization_id = uuid4()
    candidate = Candidate(id=uuid4(), organization_id=organization_id, full_name="Jane Doe")
    job = JobDescription(
        id=uuid4(),
        organization_id=organization_id,
        created_by_user_id=uuid4(),
        title="Backend Engineer",
        description="FastAPI PostgreSQL Docker",
        required_skills=["fastapi", "postgresql"],
        optional_skills=["docker"],
        education_requirements=["education"],
        keywords=["fastapi", "docker"],
    )
    resume = Resume(
        id=uuid4(),
        organization_id=organization_id,
        candidate_id=candidate.id,
        uploaded_by_user_id=uuid4(),
        original_filename="resume.pdf",
        content_type="application/pdf",
        storage_key="x",
        checksum_sha256="y",
        extracted_text="email test@example.com\nExperience Python\nEducation BS\nSkills Docker\nProjects API",
    )

    class FakeDB:
        async def execute(self, value):
            self.executed = value

        def add(self, value):
            self.value = value

        async def commit(self):
            return None

    result = await ATSScoringService(FakeDB()).score_candidate_for_job(
        job,
        candidate,
        resume,
        semantic_score=90,
        skills=["fastapi", "postgresql", "docker"],
    )
    assert result.ats_score >= 70
    assert result.job_description_id == job.id
    assert result.candidate_id == candidate.id
    assert result.components
