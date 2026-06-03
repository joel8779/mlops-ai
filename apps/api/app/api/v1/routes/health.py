"""Health check endpoints for infrastructure validation."""
from fastapi import APIRouter, Response
from sqlalchemy import text
import redis.asyncio as redis
import httpx
from datetime import datetime

from app.core.config import settings
from app.db.schema_validation import get_runtime_schema_report
from app.db.session import async_engine
from app.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health")
async def health_check():
    """Basic health check - always returns 200 if server is running."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }


@router.get("/ready")
async def readiness_check(response: Response):
    """Readiness check - validates all dependencies are ready."""
    health_status = {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {}
    }
    
    # Check PostgreSQL
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["dependencies"]["postgres"] = "healthy"
    except Exception as e:
        health_status["status"] = "not_ready"
        health_status["dependencies"]["postgres"] = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        redis_client = redis.from_url(settings.redis_url)
        await redis_client.ping()
        health_status["dependencies"]["redis"] = "healthy"
    except Exception as e:
        health_status["status"] = "not_ready"
        health_status["dependencies"]["redis"] = f"unhealthy: {str(e)}"
    
    # Check Qdrant
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{str(settings.qdrant_url).rstrip('/')}/healthz",
                timeout=5.0
            )
            if response.status_code == 200:
                health_status["dependencies"]["qdrant"] = "healthy"
            else:
                health_status["status"] = "not_ready"
                health_status["dependencies"]["qdrant"] = "unhealthy"
    except Exception as e:
        health_status["status"] = "not_ready"
        health_status["dependencies"]["qdrant"] = f"unhealthy: {str(e)}"

    try:
        schema_report = await get_runtime_schema_report()
        health_status["dependencies"]["schema"] = schema_report.model_dump()
        if schema_report.status in {"drift_detected", "validation_error"}:
            health_status["status"] = "not_ready"
            logger.warning(
                "readiness_schema_check_failed",
                status=schema_report.status,
                current_revision=schema_report.current_revision,
                expected_revision=schema_report.expected_revision,
                drift=[item.message() for item in schema_report.drift],
                error=schema_report.error,
            )
    except Exception as e:
        health_status["status"] = "not_ready"
        health_status["dependencies"]["schema"] = {"status": "unhealthy", "error": str(e)}
        logger.exception("readiness_schema_check_error", error=str(e))

    if health_status["status"] != "ready":
        response.status_code = 503
    
    return health_status


@router.get("/live")
async def liveness_check():
    """Liveness check - always returns 200 if server is running."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
