from uuid import uuid4

from app.models.domain import Candidate, JobDescription, Resume
from app.schemas.matching import MatchingWeights
from app.services.matching_service import CandidateEvidence, MatchingService


def test_matching_score_explainability():
    job = JobDescription(
        id=uuid4(),
        organization_id=uuid4(),
        created_by_user_id=uuid4(),
        title="Backend Engineer",
        description="FastAPI PostgreSQL Docker",
        required_skills=["fastapi", "postgresql"],
        optional_skills=["docker"],
        education_requirements=[],
        keywords=["fastapi", "docker"],
    )
    candidate = Candidate(id=uuid4(), organization_id=job.organization_id)
    resume = Resume(
        id=uuid4(),
        organization_id=job.organization_id,
        uploaded_by_user_id=uuid4(),
        original_filename="resume.pdf",
        content_type="application/pdf",
        storage_key="x",
        checksum_sha256="y",
        extracted_text="5 years FastAPI Docker PostgreSQL",
    )
    result = MatchingService(db=None).score(
        job,
        CandidateEvidence(candidate=candidate, resume=resume, skills=["fastapi", "docker"], semantic_score=90),
        MatchingWeights(),
        {},
    )
    assert result.overall_score > 70
    assert "fastapi" in result.matched_skills
