from uuid import uuid4

import pytest

from app.models.domain import Resume
from app.services.ats_scoring_service import ATSScoringService


@pytest.mark.asyncio
async def test_ats_scoring_detects_sections():
    resume = Resume(
        id=uuid4(),
        organization_id=uuid4(),
        uploaded_by_user_id=uuid4(),
        original_filename="resume.pdf",
        content_type="application/pdf",
        storage_key="x",
        checksum_sha256="y",
        extracted_text="email test@example.com\nExperience Python\nEducation BS\nSkills Docker\nProjects API",
    )

    class FakeDB:
        def add(self, value):
            self.value = value

        async def commit(self):
            return None

    result = await ATSScoringService(FakeDB()).score_resume(resume)
    assert result.ats_score >= 70
