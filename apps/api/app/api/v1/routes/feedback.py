from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.db.session import get_db
from app.schemas.auth import AuthContext
from app.schemas.feedback import RankingFeedbackCreate, RankingFeedbackRead
from app.services.feedback_service import FeedbackService

router = APIRouter()


@router.post("/ranking", response_model=RankingFeedbackRead)
async def record_ranking_feedback(
    payload: RankingFeedbackCreate,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    return await FeedbackService(db).record(auth, payload)
