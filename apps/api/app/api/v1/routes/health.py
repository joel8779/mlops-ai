"""Health check endpoints for infrastructure validation."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
import httpx
import os
from datetime import datetime

from app.db.session import async_session_maker, async_engine

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check - always returns 200 if server is running."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }


@router.get("/ready")
async def readiness_check():
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
        redis_client = redis.from_url(os.getenv("REDIS_URL"))
        await redis_client.ping()
        health_status["dependencies"]["redis"] = "healthy"
    except Exception as e:
        health_status["status"] = "not_ready"
        health_status["dependencies"]["redis"] = f"unhealthy: {str(e)}"
    
    # Check Qdrant
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{os.getenv('QDRANT_URL')}/healthz",
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
    
    return health_status


@router.get("/live")
async def liveness_check():
    """Liveness check - always returns 200 if server is running."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
