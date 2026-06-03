import pytest

from app.models.domain import Candidate, Organization, Resume, ResumeStatus, User
from app.repositories.candidates import CandidateRepository
from app.api.v1.routes.candidates import _candidate_item
from app.services.candidate_extraction_service import CandidateExtractionService


def test_candidate_extraction_detects_explicit_skills_and_student_level():
    text = """
    Priya Sharma
    B.Tech Computer Science, graduating 2026
    Technical Skills: React.js, Node.js, PostgreSQL, Docker, Git
    Projects
    Built a campus placement dashboard with React.js and PostgreSQL.
    Internship
    Frontend Intern at Acme Labs, June 2025 - August 2025.
    """

    extraction = CandidateExtractionService()._deterministic_extract(text, "priya_resume.pdf", {})

    assert {"react", "node.js", "postgresql", "docker", "git"}.issubset(set(extraction.skills))
    assert extraction.inferred_seniority in {"student", "fresher"}
    assert "Senior candidate" not in (CandidateExtractionService.headline(extraction) or "")


@pytest.mark.asyncio
async def test_candidate_item_repairs_structured_skills_into_api_response(test_db, mock_env_vars):
    organization = Organization(name="Skill Repair Org", slug="skill-repair-org")
    user = User(
        organization=organization,
        email="skill-repair@example.com",
        hashed_password="hashed",
        full_name="Skill Repair User",
        roles=["recruiter"],
        is_active=True,
    )
    test_db.add_all([organization, user])
    await test_db.flush()

    resume_text = "Technical Skills: React.js, Node.js, PostgreSQL, Docker, Git"
    candidate = Candidate(
        organization_id=organization.id,
        owner_id=user.id,
        full_name="Skill Candidate",
        raw_profile={"skills": ["React.js", "Node.js", "PostgreSQL", "Docker", "Git"]},
    )
    test_db.add(candidate)
    await test_db.flush()

    resume = Resume(
        organization_id=organization.id,
        owner_id=user.id,
        candidate_id=candidate.id,
        uploaded_by_user_id=user.id,
        original_filename="skill-candidate.pdf",
        content_type="application/pdf",
        storage_key="skill-candidate",
        checksum_sha256="skill-candidate-checksum",
        status=ResumeStatus.parsed,
        extracted_text=resume_text,
    )
    test_db.add(resume)
    await test_db.commit()

    item = await _candidate_item(test_db, CandidateRepository(test_db), candidate, organization.id, None)

    assert {"react", "node.js", "postgresql", "docker", "git"}.issubset(set(item.skills))
    assert await CandidateRepository(test_db).skills_for_candidate(candidate.id, organization.id) == item.skills
