from fastapi import APIRouter, Depends

from app.core.auth import get_current_auth
from app.schemas.auth import AuthContext
from app.schemas.matching import SemanticSearchRequest, SemanticSearchResult
from app.services.semantic_search_service import SemanticSearchService

router = APIRouter()


@router.post("/candidates", response_model=list[SemanticSearchResult])
async def search_candidates(
    payload: SemanticSearchRequest,
    auth: AuthContext = Depends(get_current_auth),
):
    return SemanticSearchService().search(auth.organization_id, payload)
