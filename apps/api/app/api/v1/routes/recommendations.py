from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.db.session import get_db
from app.knowledge_graph.taxonomy.taxonomy_service import TaxonomyService
from app.schemas.auth import AuthContext
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    SkillExpansionRequest,
    SkillExpansionResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.post("/candidates", response_model=RecommendationResponse)
async def recommend_candidates(
    payload: RecommendationRequest,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    return await RecommendationService(db).recommend(auth, payload)


@router.post("/skills/expand", response_model=SkillExpansionResponse)
async def expand_skills(payload: SkillExpansionRequest, auth: AuthContext = Depends(get_current_auth)):
    enriched = TaxonomyService().enrich_candidate_skills(payload.skills)
    return SkillExpansionResponse(**enriched)
