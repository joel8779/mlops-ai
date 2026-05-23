from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.db.session import get_db
from app.schemas.auth import AuthContext
from app.schemas.analytics import ExecutiveDashboardResponse
from app.analytics.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/executive", response_model=ExecutiveDashboardResponse)
async def executive_dashboard(auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return await AnalyticsService(db).executive_dashboard(auth)
