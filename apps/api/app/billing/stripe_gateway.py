"""Stripe abstraction boundary for subscription billing."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.subscriptions.plans import PlanCode


@dataclass(frozen=True)
class CheckoutSession:
    organization_id: UUID
    plan: PlanCode
    checkout_url: str
    provider_session_id: str


class BillingGateway(Protocol):
    async def create_checkout_session(self, organization_id: UUID, plan: PlanCode, seats: int) -> CheckoutSession: ...


class StripeBillingGateway:
    def __init__(self, billing_portal_base_url: str = "https://billing.stripe.com") -> None:
        self.billing_portal_base_url = billing_portal_base_url.rstrip("/")

    async def create_checkout_session(self, organization_id: UUID, plan: PlanCode, seats: int) -> CheckoutSession:
        session_id = f"cs_{organization_id.hex[:12]}_{plan.value}_{seats}"
        return CheckoutSession(
            organization_id=organization_id,
            plan=plan,
            checkout_url=f"{self.billing_portal_base_url}/pay/{session_id}",
            provider_session_id=session_id,
        )
