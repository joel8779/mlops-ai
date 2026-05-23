from time import perf_counter

from prometheus_client import Counter, Gauge, Histogram

API_LATENCY = Histogram("resume_ai_api_latency_seconds", "API request latency", ["method", "path"])
EMBEDDING_LATENCY = Histogram("resume_ai_embedding_latency_seconds", "Embedding latency", ["model"])
RANKING_LATENCY = Histogram("resume_ai_ranking_latency_seconds", "Ranking latency", ["version"])
RETRIEVAL_LATENCY = Histogram("resume_ai_retrieval_latency_seconds", "Retrieval latency", ["strategy"])
LLM_COST = Counter("resume_ai_llm_cost_usd_total", "Estimated LLM cost", ["provider", "model", "feature"])
RECRUITER_ACTIONS = Counter("resume_ai_recruiter_actions_total", "Recruiter actions", ["action"])
WEBSOCKET_CONNECTIONS = Counter("resume_ai_websocket_connections_total", "WebSocket connections", ["organization_id"])

LLM_REQUEST_LATENCY_MS = Histogram(
    "llm_request_latency_ms",
    "LLM request latency in milliseconds",
    ["provider", "model", "feature", "status"],
)
LLM_TOKENS_INPUT_TOTAL = Counter(
    "llm_tokens_input_total",
    "Total LLM input tokens",
    ["provider", "model", "feature"],
)
LLM_TOKENS_OUTPUT_TOTAL = Counter(
    "llm_tokens_output_total",
    "Total LLM output tokens",
    ["provider", "model", "feature"],
)
LLM_FAILURES_TOTAL = Counter(
    "llm_failures_total",
    "LLM failures",
    ["provider", "model", "feature", "error_type"],
)
LLM_RETRY_COUNT_TOTAL = Counter(
    "llm_retry_count_total",
    "LLM retry attempts",
    ["provider", "model", "feature"],
)
LLM_ESTIMATED_COST_USD = Counter(
    "llm_estimated_cost_usd",
    "Estimated LLM cost in USD",
    ["provider", "model", "feature"],
)
LLM_PROMPT_SIZE_BYTES = Histogram(
    "llm_prompt_size_bytes",
    "LLM prompt size in bytes",
    ["provider", "model", "feature"],
)
LLM_RESPONSE_SIZE_BYTES = Histogram(
    "llm_response_size_bytes",
    "LLM response size in bytes",
    ["provider", "model", "feature"],
)
MODEL_FALLBACK_TOTAL = Counter(
    "model_fallback_frequency_total",
    "Model fallback frequency",
    ["from_model", "to_model", "reason"],
)
AI_SAFETY_EVENTS_TOTAL = Counter(
    "ai_safety_events_total",
    "AI safety, hallucination, and grounding events",
    ["event_type", "severity", "feature"],
)
RECOMMENDATION_GENERATION_TIME_MS = Histogram(
    "recommendation_generation_time_ms",
    "Recommendation generation latency in milliseconds",
    ["strategy", "status"],
)
RECOMMENDATION_RESULTS = Histogram(
    "recommendation_results_count",
    "Number of recommendations returned",
    ["strategy"],
)
RETRIEVAL_TOPK_LATENCY_MS = Histogram(
    "retrieval_topk_latency_ms",
    "Top-k retrieval latency in milliseconds",
    ["strategy", "status"],
)
RETRIEVAL_RESULT_COUNT = Histogram(
    "retrieval_result_count",
    "Number of retrieval results returned",
    ["strategy"],
)
RETRIEVAL_CONFIDENCE = Histogram(
    "retrieval_confidence",
    "Retrieval confidence score",
    ["strategy"],
)
RETRIEVAL_SIMILARITY_SCORE = Histogram(
    "retrieval_similarity_score",
    "Semantic similarity score distribution",
    ["strategy"],
)
RETRIEVAL_CACHE_HITS_TOTAL = Counter(
    "retrieval_cache_hits_total",
    "Retrieval cache hits",
    ["cache_name"],
)
RETRIEVAL_CACHE_MISSES_TOTAL = Counter(
    "retrieval_cache_misses_total",
    "Retrieval cache misses",
    ["cache_name"],
)
WEBSOCKET_ACTIVE_CONNECTIONS = Gauge(
    "websocket_active_connections",
    "Active websocket connections",
    ["organization_id"],
)
REDIS_STREAM_CONSUMER_LAG = Gauge(
    "redis_stream_consumer_lag",
    "Redis stream pending message count by consumer group",
    ["stream", "consumer_group"],
)
REDIS_STREAM_EVENTS_PUBLISHED_TOTAL = Counter(
    "redis_stream_events_published_total",
    "Redis stream events published",
    ["stream", "event_type"],
)
REDIS_STREAM_EVENTS_CONSUMED_TOTAL = Counter(
    "redis_stream_events_consumed_total",
    "Redis stream events consumed",
    ["stream", "consumer_group", "event_type", "status"],
)
AGENT_EXECUTION_FAILURES_TOTAL = Counter(
    "agent_execution_failures_total",
    "Agent execution failures",
    ["workflow_step", "error_type"],
)
AGENT_STEP_LATENCY_MS = Histogram(
    "agent_step_latency_ms",
    "Agent workflow step latency in milliseconds",
    ["workflow_step", "status"],
)
TOOL_INVOCATION_DURATION_MS = Histogram(
    "tool_invocation_duration_ms",
    "Agent tool invocation duration in milliseconds",
    ["tool_name", "status"],
)
PLANNER_EXECUTION_DURATION_MS = Histogram(
    "planner_execution_duration_ms",
    "Planner execution duration in milliseconds",
    ["planner", "status"],
)
AUTONOMOUS_ACTIONS_TOTAL = Counter(
    "autonomous_actions_total",
    "Autonomous agent actions",
    ["action", "outcome"],
)
WEBSOCKET_DROPPED_CONNECTIONS_TOTAL = Counter(
    "websocket_dropped_connections_total",
    "Dropped websocket connections",
    ["organization_id", "reason"],
)
WEBSOCKET_BROADCAST_LATENCY_MS = Histogram(
    "websocket_broadcast_latency_ms",
    "Websocket broadcast latency in milliseconds",
    ["organization_id", "status"],
)
REDIS_STREAM_PROCESSING_LATENCY_MS = Histogram(
    "redis_stream_processing_latency_ms",
    "Redis stream event processing latency in milliseconds",
    ["stream", "consumer_group", "event_type", "status"],
)
EMBEDDING_GENERATION_DURATION_MS = Histogram(
    "embedding_generation_duration_ms",
    "Embedding generation duration in milliseconds",
    ["model", "status"],
)
ML_INFERENCE_LATENCY_MS = Histogram(
    "ml_inference_latency_ms",
    "ML inference latency in milliseconds",
    ["model", "operation", "status"],
)
ML_INFERENCE_FAILURES_TOTAL = Counter(
    "ml_inference_failures_total",
    "ML inference failures",
    ["model", "operation", "error_type"],
)
RANKING_MODEL_DRIFT_SCORE = Gauge(
    "ranking_model_drift_score",
    "Ranking model drift score",
    ["model_version"],
)
RECRUITER_SHORTLIST_RATE = Gauge(
    "recruiter_shortlist_rate",
    "Recruiter shortlist rate",
    ["organization_id"],
)
RECOMMENDATION_ACCEPTANCE_RATE = Gauge(
    "recommendation_acceptance_rate",
    "Recommendation acceptance rate",
    ["organization_id"],
)


def elapsed_ms(start_time: float) -> float:
    return (perf_counter() - start_time) * 1000
