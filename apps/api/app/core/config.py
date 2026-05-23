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

    database_url: str = "postgresql+asyncpg://resume:resume@localhost:5432/resume_ai"
    sync_database_url: str = "postgresql+psycopg://resume:resume@localhost:5432/resume_ai"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    auth_dev_bypass: bool = False

    s3_endpoint_url: str | None = None
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_bucket: str = "resumes"
    s3_region: str = "us-east-1"

    qdrant_url: AnyHttpUrl | str = "http://localhost:6333"
    qdrant_collection: str = "candidate_embeddings"
    qdrant_job_collection: str = "job_description_embeddings"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_vector_size: int = 384
    mlflow_tracking_uri: str = "http://localhost:5000"

    openai_api_key: str | None = None  # Deprecated, kept for migration
    openai_model: str = "gpt-4o-mini"  # Deprecated
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    llm_provider: Literal["gemini", "disabled"] = "gemini"
    rate_limit_default: str = "100/minute"
    max_upload_bytes: int = 10 * 1024 * 1024

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
