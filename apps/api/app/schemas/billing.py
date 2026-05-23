from uuid import UUID

from pydantic import BaseModel, Field

from app.subscriptions.plans import PlanCode


class PlanRead(BaseModel):
    code: PlanCode
    monthly_price_usd: int
    seat_limit: int | None
    resume_limit: int
    llm_token_limit: int
    vector_query_limit: int
    features: list[str]


class CheckoutRequest(BaseModel):
    plan: PlanCode
    seats: int = Field(default=1, ge=1, le=10_000)


class CheckoutResponse(BaseModel):
    organization_id: UUID
    plan: PlanCode
    checkout_url: str
    provider_session_id: str


class FeatureGateResponse(BaseModel):
    plan: PlanCode
    feature: str
    enabled: bool
