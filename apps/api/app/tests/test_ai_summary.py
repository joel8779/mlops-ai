import pytest
from uuid import uuid4

from app.models.domain import Candidate, Organization, Resume, ResumeStatus, User
from app.schemas.auth import AuthContext
from app.services.llm.providers.gemini_provider import LLMResult
from app.services.llm_recruiter_service import LLMRecruiterService


class DummyProvider:
    def __init__(self, result_text: str):
        self.result_text = result_text

    async def complete(self, prompt: str, system: str | None = None, options=None):
        return LLMResult(
            text=self.result_text,
            provider="test",
            model="test-model",
            prompt_tokens=0,
            completion_tokens=0,
            estimated_cost_usd=0.0,
        )


@pytest.mark.asyncio
async def test_blank_llm_summary_preserves_existing_candidate_summary(test_db, monkeypatch, mock_env_vars):
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
    await test_db.commit()

    candidate = Candidate(
        organization_id=organization.id,
        owner_id=user.id,
        full_name="Jane Doe",
        email="jane.doe@example.com",
        summary="Existing summary",
    )
    resume = Resume(
        organization_id=organization.id,
        owner_id=user.id,
        candidate=candidate,
        uploaded_by_user_id=user.id,
        original_filename="resume.pdf",
        content_type="application/pdf",
        storage_key="resume-1",
        checksum_sha256="abc123",
        status=ResumeStatus.parsed,
        extracted_text="Experienced backend engineer with 6 years of Python development.",
    )
    test_db.add_all([candidate, resume])
    await test_db.commit()

    monkeypatch.setattr("app.services.llm_recruiter_service.get_llm_provider", lambda: DummyProvider(result_text="   \n  "))

    auth = AuthContext(
        user_id=user.id,
        organization_id=organization.id,
        email=user.email,
        full_name=user.full_name,
        roles=user.roles,
    )

    service = LLMRecruiterService(test_db)
    response = await service.summarize_candidate(auth, candidate.id)

    await test_db.refresh(candidate)

    assert response.answer == "Existing summary"
    assert candidate.summary == "Existing summary"


@pytest.mark.asyncio
async def test_non_empty_llm_summary_updates_candidate_summary(test_db, monkeypatch, mock_env_vars):
    organization = Organization(name="Test Org", slug="test-org")
    user = User(
        organization=organization,
        email="user2@example.com",
        hashed_password="hashed",
        full_name="Test User 2",
        roles=["recruiter"],
        is_active=True,
    )
    test_db.add_all([organization, user])
    await test_db.commit()

    candidate = Candidate(
        organization_id=organization.id,
        owner_id=user.id,
        full_name="John Smith",
        email="john.smith@example.com",
        summary="Old summary",
    )
    resume = Resume(
        organization_id=organization.id,
        owner_id=user.id,
        candidate=candidate,
        uploaded_by_user_id=user.id,
        original_filename="resume.pdf",
        content_type="application/pdf",
        storage_key="resume-2",
        checksum_sha256="def456",
        status=ResumeStatus.parsed,
        extracted_text="Seasoned machine learning engineer with 8 years of experience.",
    )
    test_db.add_all([candidate, resume])
    await test_db.commit()

    monkeypatch.setattr("app.services.llm_recruiter_service.get_llm_provider", lambda: DummyProvider(result_text="Updated AI-generated summary."))

    auth = AuthContext(
        user_id=user.id,
        organization_id=organization.id,
        email=user.email,
        full_name=user.full_name,
        roles=user.roles,
    )

    service = LLMRecruiterService(test_db)
    response = await service.summarize_candidate(auth, candidate.id)

    await test_db.refresh(candidate)

    assert response.answer == "Updated AI-generated summary."
    assert candidate.summary == "Updated AI-generated summary."
