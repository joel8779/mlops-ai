from fastapi import APIRouter, Depends

from app.billing.feature_gates import FeatureGateService
from app.billing.stripe_gateway import StripeBillingGateway
from app.core.auth import get_current_auth
from app.schemas.auth import AuthContext
from app.schemas.billing import CheckoutRequest, CheckoutResponse, FeatureGateResponse, PlanRead
from app.subscriptions.plans import PLAN_CATALOG, PlanCode

router = APIRouter()


@router.get("/plans", response_model=list[PlanRead])
async def list_plans(auth: AuthContext = Depends(get_current_auth)):
    return [
        PlanRead(
            code=plan.code,
            monthly_price_usd=plan.monthly_price_usd,
            seat_limit=plan.seat_limit,
            resume_limit=plan.resume_limit,
            llm_token_limit=plan.llm_token_limit,
            vector_query_limit=plan.vector_query_limit,
            features=sorted(plan.features),
        )
        for plan in PLAN_CATALOG.values()
    ]


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(payload: CheckoutRequest, auth: AuthContext = Depends(get_current_auth)):
    session = await StripeBillingGateway().create_checkout_session(auth.organization_id, payload.plan, payload.seats)
    return CheckoutResponse(**session.__dict__)


@router.get("/features/{feature}", response_model=FeatureGateResponse)
async def check_feature(feature: str, plan: PlanCode = PlanCode.FREE, auth: AuthContext = Depends(get_current_auth)):
    return FeatureGateResponse(plan=plan, feature=feature, enabled=FeatureGateService().is_enabled(plan, feature))
