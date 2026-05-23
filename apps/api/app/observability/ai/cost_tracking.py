from app.observability.metrics import LLM_COST, LLM_ESTIMATED_COST_USD


class CostTracker:
    def record_cost(self, provider: str, model: str, feature: str, cost_usd: float) -> None:
        LLM_COST.labels(provider, model, feature).inc(cost_usd)
        LLM_ESTIMATED_COST_USD.labels(provider, model, feature).inc(cost_usd)
