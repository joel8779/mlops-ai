from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "resume-intelligence"
    environment: str = "local"
    log_level: str = "INFO"

    database_url: str = Field(default="postgresql+asyncpg://resume:resume@localhost:5432/resume_ai")
    sync_database_url: str = Field(default="postgresql://resume:resume@localhost:5432/resume_ai")

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    jwt_issuer: str = ""
    jwt_audience: str = ""
    jwt_jwks_url: str = ""
    auth_dev_bypass: bool = False

    s3_endpoint_url: str | None = None
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_bucket: str = "resumes"
    s3_region: str = "us-east-1"

    qdrant_url: str = "http://localhost:6333"
    mlflow_tracking_uri: str = "http://localhost:5000"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
