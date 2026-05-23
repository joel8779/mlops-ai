from dataclasses import dataclass
from enum import StrEnum


class PlanCode(StrEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass(frozen=True)
class SubscriptionPlan:
    code: PlanCode
    monthly_price_usd: int
    seat_limit: int | None
    resume_limit: int
    llm_token_limit: int
    vector_query_limit: int
    features: set[str]


PLAN_CATALOG: dict[PlanCode, SubscriptionPlan] = {
    PlanCode.FREE: SubscriptionPlan(PlanCode.FREE, 0, 2, 250, 100_000, 2_000, {"copilot_basic", "semantic_search"}),
    PlanCode.PRO: SubscriptionPlan(PlanCode.PRO, 99, 25, 5_000, 2_000_000, 75_000, {"copilot_2", "recommendations", "integrations"}),
    PlanCode.ENTERPRISE: SubscriptionPlan(PlanCode.ENTERPRISE, 0, None, 100_000, 50_000_000, 2_000_000, {"sso", "audit", "copilot_2", "recommendations", "custom_ai"}),
}
