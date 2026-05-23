from app.observability.metrics import RECOMMENDATION_ACCEPTANCE_RATE


class RecommendationQualityMonitor:
    def record_acceptance_rate(self, organization_id: str, rate: float) -> None:
        RECOMMENDATION_ACCEPTANCE_RATE.labels(organization_id).set(rate)
