from app.observability.metrics import RECOMMENDATION_ACCEPTANCE_RATE, RECRUITER_SHORTLIST_RATE


class RankingMetrics:
    def set_shortlist_rate(self, organization_id: str, value: float) -> None:
        RECRUITER_SHORTLIST_RATE.labels(organization_id).set(value)

    def set_acceptance_rate(self, organization_id: str, value: float) -> None:
        RECOMMENDATION_ACCEPTANCE_RATE.labels(organization_id).set(value)
