from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.db.session import get_db
from app.schemas.auth import AuthContext
from app.schemas.workflow import (
    HiringAnalytics,
    RecruiterNoteCreate,
    RecruiterNoteResponse,
    StageUpdateRequest,
    StageUpdateResponse,
    WorkflowActivityRead,
    BookmarkResponse,
)
from app.services.workflow_service import WorkflowService

router = APIRouter()


@router.post("/stages", response_model=StageUpdateResponse)
async def update_stage(payload: StageUpdateRequest, auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return await WorkflowService(db).update_stage(auth, payload)


@router.post("/notes", response_model=RecruiterNoteResponse)
async def add_note(payload: RecruiterNoteCreate, auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return await WorkflowService(db).add_note(auth, payload)


@router.post("/bookmarks/{candidate_id}", response_model=BookmarkResponse)
async def bookmark(candidate_id: UUID, auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return await WorkflowService(db).bookmark(auth, candidate_id)


@router.get("/timeline", response_model=list[WorkflowActivityRead])
async def timeline(auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return await WorkflowService(db).timeline(auth)


@router.get("/analytics", response_model=HiringAnalytics)
async def analytics(auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return await WorkflowService(db).analytics(auth)
