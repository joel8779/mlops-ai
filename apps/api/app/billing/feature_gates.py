from app.subscriptions.plans import PLAN_CATALOG, PlanCode


class FeatureGateService:
    def is_enabled(self, plan: PlanCode, feature: str) -> bool:
        return feature in PLAN_CATALOG[plan].features

    def assert_enabled(self, plan: PlanCode, feature: str) -> None:
        if not self.is_enabled(plan, feature):
            raise PermissionError(f"Feature '{feature}' requires a higher subscription tier")
