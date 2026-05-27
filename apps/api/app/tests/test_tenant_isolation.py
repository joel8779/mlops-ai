from uuid import uuid4

import pytest

from app.models.domain import Candidate, CandidatePipelineStage, JobDescription, PipelineStage, Resume, User
from app.repositories.candidates import CandidateRepository
from app.schemas.auth import AuthContext
from app.schemas.workflow import RecruiterNoteCreate, StageUpdateRequest
from app.services.workflow_service import WorkflowService


@pytest.mark.asyncio
async def test_candidate_repository_helpers_respect_organization(test_db):
    org_a = uuid4()
    org_b = uuid4()
    user_id = uuid4()
    candidate_id = uuid4()
    candidate = Candidate(id=candidate_id, organization_id=org_a, owner_id=user_id, full_name="Tenant A Candidate")
    leaked_resume = Resume(
        organization_id=org_b,
        owner_id=uuid4(),
        candidate_id=candidate_id,
        uploaded_by_user_id=user_id,
        original_filename="other.pdf",
        content_type="application/pdf",
        storage_key="tenant-b/other.pdf",
        checksum_sha256="b" * 64,
        extracted_text="other tenant resume",
    )
    owned_resume = Resume(
        organization_id=org_a,
        owner_id=user_id,
        candidate_id=candidate_id,
        uploaded_by_user_id=user_id,
        original_filename="owned.pdf",
        content_type="application/pdf",
        storage_key="tenant-a/owned.pdf",
        checksum_sha256="a" * 64,
        extracted_text="owned resume",
    )
    test_db.add_all([candidate, leaked_resume, owned_resume])
    await test_db.commit()

    repository = CandidateRepository(test_db)

    resume = await repository.latest_resume(candidate_id, org_a, user_id)

    assert resume is not None
    assert resume.organization_id == org_a


@pytest.mark.asyncio
async def test_workflow_rejects_cross_tenant_candidate(test_db):
    org_a = uuid4()
    org_b = uuid4()
    auth = AuthContext(user_id=uuid4(), organization_id=org_a, email="recruiter@example.com", roles=["recruiter"])
    other_candidate = Candidate(id=uuid4(), organization_id=org_b, owner_id=uuid4(), full_name="Other Tenant")
    test_db.add(other_candidate)
    await test_db.commit()

    with pytest.raises(Exception) as exc_info:
        await WorkflowService(test_db).add_note(
            auth,
            RecruiterNoteCreate(candidate_id=other_candidate.id, body="Must not attach"),
        )

    assert getattr(exc_info.value, "status_code", None) == 404


@pytest.mark.asyncio
async def test_workflow_stage_lookup_is_organization_scoped(test_db):
    org_a = uuid4()
    org_b = uuid4()
    auth = AuthContext(user_id=uuid4(), organization_id=org_a, email="recruiter@example.com", roles=["recruiter"])
    candidate = Candidate(id=uuid4(), organization_id=org_a, owner_id=auth.user_id, full_name="Owned Candidate")
    user = User(
        id=auth.user_id,
        organization_id=org_a,
        email=auth.email,
        hashed_password="x",
        roles=auth.roles,
    )
    job = JobDescription(
        organization_id=org_a,
        owner_id=auth.user_id,
        created_by_user_id=auth.user_id,
        title="ML Engineer",
        description="Build retrieval systems",
    )
    test_db.add_all([user, candidate, job])
    await test_db.flush()
    test_db.add(
        CandidatePipelineStage(
            organization_id=org_b,
            owner_id=uuid4(),
            candidate_id=candidate.id,
            job_description_id=job.id,
            stage=PipelineStage.rejected,
        )
    )
    await test_db.commit()

    stage = await WorkflowService(test_db).update_stage(
        auth,
        StageUpdateRequest(candidate_id=candidate.id, job_description_id=job.id, stage=PipelineStage.shortlisted),
    )

    assert stage.organization_id == org_a
    assert stage.stage == PipelineStage.shortlisted
