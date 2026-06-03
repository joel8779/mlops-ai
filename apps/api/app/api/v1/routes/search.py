from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.db.session import get_db
from app.schemas.auth import AuthContext
from app.schemas.matching import CandidateSearchResult, SemanticSearchRequest
from app.services.semantic_search_service import SemanticSearchService

router = APIRouter()


@router.post("/candidates", response_model=list[CandidateSearchResult])
async def search_candidates(
    payload: SemanticSearchRequest,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    from app.core.rate_limit import rate_limiter
    await rate_limiter.check_rate_limit(f"rate:search:{auth.user_id}", 120, 3600)

    return await SemanticSearchService(db).search(auth.organization_id, auth.user_id, payload)
