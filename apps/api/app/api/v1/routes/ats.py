from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.db.session import get_db
from app.repositories.resumes import ResumeRepository
from app.schemas.ats import ATSScoreRead
from app.schemas.auth import AuthContext
from app.services.ats_scoring_service import ATSScoringService

router = APIRouter()


@router.post("/resumes/{resume_id}/score", response_model=ATSScoreRead)
async def score_resume(resume_id: UUID, auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    resume = await ResumeRepository(db).get_for_org(resume_id, auth.organization_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return await ATSScoringService(db).score_resume(resume)
