from prometheus_client import Counter, Histogram

API_LATENCY = Histogram("resume_ai_api_latency_seconds", "API request latency", ["method", "path"])
EMBEDDING_LATENCY = Histogram("resume_ai_embedding_latency_seconds", "Embedding latency", ["model"])
RANKING_LATENCY = Histogram("resume_ai_ranking_latency_seconds", "Ranking latency", ["version"])
RETRIEVAL_LATENCY = Histogram("resume_ai_retrieval_latency_seconds", "Retrieval latency", ["strategy"])
LLM_COST = Counter("resume_ai_llm_cost_usd_total", "Estimated LLM cost", ["provider", "model", "feature"])
RECRUITER_ACTIONS = Counter("resume_ai_recruiter_actions_total", "Recruiter actions", ["action"])
WEBSOCKET_CONNECTIONS = Counter("resume_ai_websocket_connections_total", "WebSocket connections", ["organization_id"])
