from time import perf_counter

from app.observability.ai.cost_tracking import CostTracker
from app.observability.ai.token_metrics import TokenMetrics
from app.observability.metrics import (
    LLM_FAILURES_TOTAL,
    LLM_PROMPT_SIZE_BYTES,
    LLM_REQUEST_LATENCY_MS,
    LLM_RESPONSE_SIZE_BYTES,
    elapsed_ms,
)


class LLMObserver:
    def __init__(self) -> None:
        self.tokens = TokenMetrics()
        self.costs = CostTracker()

    def start_timer(self) -> float:
        return perf_counter()

    def record_success(
        self,
        provider: str,
        model: str,
        feature: str,
        start_time: float,
        prompt: str,
        response: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
    ) -> None:
        LLM_REQUEST_LATENCY_MS.labels(provider, model, feature, "success").observe(elapsed_ms(start_time))
        LLM_PROMPT_SIZE_BYTES.labels(provider, model, feature).observe(len(prompt.encode("utf-8")))
        LLM_RESPONSE_SIZE_BYTES.labels(provider, model, feature).observe(len(response.encode("utf-8")))
        self.tokens.record(provider, model, feature, input_tokens, output_tokens)
        self.costs.record_cost(provider, model, feature, cost_usd)

    def record_failure(self, provider: str, model: str, feature: str, start_time: float, exc: Exception) -> None:
        LLM_REQUEST_LATENCY_MS.labels(provider, model, feature, "error").observe(elapsed_ms(start_time))
        LLM_FAILURES_TOTAL.labels(provider, model, feature, type(exc).__name__).inc()
