from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.db.session import get_db
from app.repositories.jobs import JobDescriptionRepository
from app.schemas.auth import AuthContext
from app.schemas.matching import CandidateMatchRead, MatchRequest
from app.services.matching_service import MatchingService

router = APIRouter()


@router.post("/rank", response_model=list[CandidateMatchRead])
async def rank_candidates(
    payload: MatchRequest,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    job = await JobDescriptionRepository(db).get_for_owner(payload.job_description_id, auth.organization_id, auth.user_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job description not found")
    return await MatchingService(db).rank_candidates(
        auth.organization_id,
        auth.user_id,
        job,
        payload.limit,
        payload.weights,
        payload.recruiter_preferences,
    )
