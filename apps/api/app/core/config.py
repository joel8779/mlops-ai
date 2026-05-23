from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables.

    Pydantic Settings keeps deployment concerns outside the codebase while still
    validating types at process start.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "resume-intelligence"
    app_version: str = "0.1.0"
    environment: Literal["local", "test", "staging", "production"] = "local"
    debug: bool = False
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    backend_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    frontend_url: str = "http://localhost:3000"

    database_url: str = "postgresql+asyncpg://resume:resume@localhost:5432/resume_ai"
    sync_database_url: str = "postgresql+psycopg://resume:resume@localhost:5432/resume_ai"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_statement_timeout_ms: int = 30000
    db_read_replica_url: str | None = None

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    redis_stream_resume_events: str = "resume-events"
    redis_stream_ai_events: str = "ai-events"
    redis_stream_workflow_events: str = "workflow-events"
    redis_consumer_group: str = "resume-intelligence-workers"
    redis_pubsub_channel: str = "realtime-updates"
    redis_max_connections: int = 50

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    auth_dev_bypass: bool = False
    api_key_pepper: str = "change-me"
    encryption_key: str = "change-me"
    prompt_injection_defense_enabled: bool = True
    pii_masking_enabled: bool = True
    audit_log_retention_days: int = 365

    s3_endpoint_url: str | None = None
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_bucket: str = "resumes"
    s3_region: str = "us-east-1"
    minio_console_url: str = "http://localhost:9001"

    qdrant_url: AnyHttpUrl | str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "candidate_embeddings"
    qdrant_job_collection: str = "job_description_embeddings"
    qdrant_memory_collection: str = "recruiter_memory_embeddings"
    qdrant_recommendation_collection: str = "recommendation_embeddings"
    qdrant_timeout_seconds: int = 20
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_vector_size: int = 384
    embedding_batch_size: int = 32
    mlflow_tracking_uri: str = "http://localhost:5000"
    prefect_api_url: str | None = None

    openai_api_key: str | None = None  # Deprecated, kept for migration
    openai_model: str = "gpt-4o-mini"  # Deprecated
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"
    gemini_timeout_seconds: int = 45
    gemini_max_output_tokens: int = 2048
    gemini_temperature: float = 0.2
    llm_provider: Literal["gemini", "disabled"] = "gemini"
    rate_limit_default: str = "100/minute"
    max_upload_bytes: int = 10 * 1024 * 1024

    otel_service_name: str = "resume-intelligence-api"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_traces_exporter: str = "otlp"
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    grafana_url: str = "http://localhost:3001"
    loki_url: str = "http://localhost:3100"
    ai_metrics_enabled: bool = True
    log_json: bool = True

    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_free: str | None = None
    stripe_price_pro: str | None = None
    stripe_price_enterprise: str | None = None
    billing_portal_base_url: str = "https://billing.stripe.com"

    analytics_enabled: bool = True
    analytics_snapshot_cron: str = "0 * * * *"
    recruiter_satisfaction_metric_enabled: bool = True
    ranking_drift_threshold: float = 0.15
    recommendation_quality_threshold: float = 0.72

    feature_copilot_2: bool = True
    feature_recommendations: bool = True
    feature_knowledge_graph: bool = True
    feature_adaptive_retrieval: bool = True
    feature_billing: bool = True
    feature_live_collaboration: bool = True
    feature_ai_safety: bool = True
    feature_demo_mode: bool = True

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "resume-graph-password"
    neo4j_database: str = "neo4j"
    skill_graph_refresh_interval_seconds: int = 3600

    ai_safety_enabled: bool = True
    hallucination_check_enabled: bool = True
    grounding_check_enabled: bool = True
    unsafe_output_detection_enabled: bool = True
    ai_confidence_threshold: float = 0.65
    retrieval_min_confidence: float = 0.45

    recommendation_engine_enabled: bool = True
    recommendation_graph_min_similarity: float = 0.35
    recommendation_max_candidates: int = 500
    recruiter_memory_enabled: bool = True
    recruiter_memory_ttl_seconds: int = 2592000
    personalization_min_feedback_events: int = 5

    websocket_enabled: bool = True
    websocket_redis_channel: str = "realtime-updates"
    websocket_heartbeat_seconds: int = 30
    websocket_max_connections_per_org: int = 250

    match_semantic_weight: float = 0.40
    match_skill_weight: float = 0.25
    match_experience_weight: float = 0.15
    match_education_weight: float = 0.10
    match_keyword_weight: float = 0.10

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
