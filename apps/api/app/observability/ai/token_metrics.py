from app.observability.metrics import LLM_TOKENS_INPUT_TOTAL, LLM_TOKENS_OUTPUT_TOTAL


class TokenMetrics:
    def record(self, provider: str, model: str, feature: str, input_tokens: int, output_tokens: int) -> None:
        LLM_TOKENS_INPUT_TOTAL.labels(provider, model, feature).inc(input_tokens)
        LLM_TOKENS_OUTPUT_TOTAL.labels(provider, model, feature).inc(output_tokens)
