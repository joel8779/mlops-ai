from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import (
    Candidate,
    CandidateBookmark,
    CandidatePipelineStage,
    RecruiterActivity,
    RecruiterNote,
)
from app.repositories.candidates import CandidateRepository
from app.repositories.jobs import JobDescriptionRepository
from app.repositories.workflow import RecruiterActivityRepository, WorkflowRepository
from app.schemas.auth import AuthContext
from app.schemas.workflow import HiringAnalytics, RecruiterNoteCreate, StageUpdateRequest, WorkflowActivityRead


class WorkflowService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.workflow = WorkflowRepository(db)
        self.activities = RecruiterActivityRepository(db)

    async def update_stage(self, auth: AuthContext, payload: StageUpdateRequest) -> CandidatePipelineStage:
        await self._ensure_candidate_in_org(auth, payload.candidate_id)
        if payload.job_description_id is not None:
            await self._ensure_job_in_org(auth, payload.job_description_id)
        stage = await self.workflow.current_stage(
            auth.organization_id,
            auth.user_id,
            payload.candidate_id,
            payload.job_description_id,
        )
        if stage is None:
            stage = CandidatePipelineStage(
                organization_id=auth.organization_id,
                owner_id=auth.user_id,
                candidate_id=payload.candidate_id,
                job_description_id=payload.job_description_id,
            )
        stage.stage = payload.stage
        stage.position = payload.position
        self.db.add(stage)
        await self._activity(auth, "pipeline.stage_updated", payload.model_dump(mode="json"))
        await self.db.commit()
        await self.db.refresh(stage)
        return stage

    async def add_note(self, auth: AuthContext, payload: RecruiterNoteCreate) -> RecruiterNote:
        await self._ensure_candidate_in_org(auth, payload.candidate_id)
        note = RecruiterNote(
            organization_id=auth.organization_id,
            owner_id=auth.user_id,
            candidate_id=payload.candidate_id,
            user_id=auth.user_id,
            body=payload.body,
        )
        self.db.add(note)
        await self._activity(auth, "candidate.note_added", payload.model_dump(mode="json"))
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def bookmark(self, auth: AuthContext, candidate_id) -> CandidateBookmark:
        await self._ensure_candidate_in_org(auth, candidate_id)
        bookmark = CandidateBookmark(
            organization_id=auth.organization_id,
            owner_id=auth.user_id,
            candidate_id=candidate_id,
            user_id=auth.user_id,
        )
        self.db.add(bookmark)
        await self._activity(auth, "candidate.bookmarked", {"candidate_id": str(candidate_id)})
        await self.db.commit()
        await self.db.refresh(bookmark)
        return bookmark

    async def timeline(self, auth: AuthContext) -> list[WorkflowActivityRead]:
        return [WorkflowActivityRead.model_validate(item) for item in await self.activities.timeline(auth.organization_id, auth.user_id)]

    async def analytics(self, auth: AuthContext) -> HiringAnalytics:
        candidate_count = await self.db.scalar(
            select(func.count()).select_from(Candidate).where(
                Candidate.organization_id == auth.organization_id,
                Candidate.owner_id == auth.user_id,
            )
        )
        bookmark_count = await self.db.scalar(
            select(func.count()).select_from(CandidateBookmark).where(
                CandidateBookmark.organization_id == auth.organization_id,
                CandidateBookmark.owner_id == auth.user_id,
            )
        )
        note_count = await self.db.scalar(
            select(func.count()).select_from(RecruiterNote).where(
                RecruiterNote.organization_id == auth.organization_id,
                RecruiterNote.owner_id == auth.user_id,
            )
        )
        return HiringAnalytics(
            total_candidates=int(candidate_count or 0),
            by_stage=await self.workflow.stage_counts(auth.organization_id, auth.user_id),
            bookmarked=int(bookmark_count or 0),
            notes=int(note_count or 0),
        )

    async def _activity(self, auth: AuthContext, activity_type: str, payload: dict) -> None:
        self.db.add(
            RecruiterActivity(
                organization_id=auth.organization_id,
                owner_id=auth.user_id,
                user_id=auth.user_id,
                candidate_id=payload.get("candidate_id"),
                job_description_id=payload.get("job_description_id"),
                activity_type=activity_type,
                payload=payload,
            )
        )

    async def _ensure_candidate_in_org(self, auth: AuthContext, candidate_id) -> None:
        candidate = await CandidateRepository(self.db).get_for_owner(candidate_id, auth.organization_id, auth.user_id)
        if candidate is None:
            raise HTTPException(status_code=404, detail="Candidate not found")

    async def _ensure_job_in_org(self, auth: AuthContext, job_description_id) -> None:
        job = await JobDescriptionRepository(self.db).get_for_owner(job_description_id, auth.organization_id, auth.user_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job description not found")
