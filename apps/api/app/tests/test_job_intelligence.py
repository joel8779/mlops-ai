import io

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.core.exceptions import AppError
from app.schemas.auth import AuthContext
from app.services.extraction_service import ParsedResume
from app.services.job_intelligence_service import JobIntelligenceService


@pytest.mark.asyncio
async def test_preview_upload_no_confident_title_returns_warning(monkeypatch):
    service = JobIntelligenceService(None)

    upload = UploadFile(
        file=io.BytesIO(b"%PDF-1.4\nGeneral internal document content without an explicit job title."),
        filename="document.pdf",
        headers=Headers({"content-type": "application/pdf"}),
    )

    fake_result = ParsedResume(
        text="A document generated for internal use only. No explicit title or role name is present in this content.",
        parser_version="test",
        metadata={},
    )

    monkeypatch.setattr("app.services.job_intelligence_service.ExtractionService.parse", lambda self, payload, content_type: fake_result)

    preview = await service.preview_upload(upload)

    assert preview.title is None
    assert preview.warnings == ["Could not confidently infer a job title."]
    assert preview.title != "Job Position"


@pytest.mark.asyncio
async def test_create_from_upload_requires_extracted_title(monkeypatch):
    service = JobIntelligenceService(None)
    upload = UploadFile(
        file=io.BytesIO(b"%PDF-1.4\nInternal document body"),
        filename="document.pdf",
        headers=Headers({"content-type": "application/pdf"}),
    )

    async def fake_preview(upload_file, title=None):
        return type("Preview", (), {"title": None, "description": "Internal document body"})()

    monkeypatch.setattr(service, "preview_upload", fake_preview)

    auth = AuthContext(
        user_id="11111111-1111-1111-1111-111111111111",
        organization_id="22222222-2222-2222-2222-222222222222",
        email="tester@example.com",
        full_name="Test User",
        roles=["recruiter"],
    )

    with pytest.raises(AppError, match="Could not extract a job title"):
        await service.create_from_upload(auth, None, upload)


def test_preprocess_strips_assessment_noise():
    service = JobIntelligenceService(None)

    text = """
    Assessment instructions:
    Please complete the coding challenge.
    Job Title: Senior Python Engineer
    Responsibilities:
    Build APIs and data pipelines.
    Requirements:
    Python, FastAPI, SQL.
    """

    cleaned = service._preprocess_jd(text)

    assert "coding challenge" not in cleaned.lower()
    assert "Senior Python Engineer" in cleaned
    assert "Responsibilities" in cleaned
