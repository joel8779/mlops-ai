# Healthcheck Stabilization - PHASE 18

**Date**: 2026-05-23
**Phase**: STEP 3 - HEALTHCHECK STABILIZATION

## Current Healthcheck Configuration

### PostgreSQL
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U resume -d resume_ai"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Status**: ✅ Configured correctly
- Uses pg_isready for proper health check
- 10s interval is reasonable
- 5s timeout is appropriate
- 5 retries = 50s total wait time

### Redis
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Status**: ✅ Configured correctly
- Uses redis-cli ping for health check
- 10s interval is reasonable
- 5s timeout is appropriate
- 5 retries = 50s total wait time

### Qdrant
```yaml
healthcheck:
  test: ["CMD", "wget", "-qO-", "http://localhost:6333/healthz"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Status**: ✅ Configured correctly
- Uses HTTP health endpoint
- 10s interval is reasonable
- 5s timeout is appropriate
- 5 retries = 50s total wait time

### MinIO
```yaml
healthcheck:
  test: ["CMD", "mc", "ready", "local"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Status**: ✅ Configured correctly
- Uses MinIO client ready command
- 10s interval is reasonable
- 5s timeout is appropriate
- 5 retries = 50s total wait time

### MLflow
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"]
  interval: 15s
  timeout: 5s
  retries: 5
```

**Status**: ✅ Configured correctly
- Uses Python HTTP request
- 15s interval accounts for MLflow startup time
- 5s timeout is appropriate
- 5 retries = 75s total wait time

## Startup Ordering

### Current Configuration
```yaml
api:
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
    qdrant:
      condition: service_started
    minio-init:
      condition: service_completed_successfully
```

**Status**: ✅ Configured correctly
- API waits for PostgreSQL to be healthy
- API waits for Redis to be healthy
- API waits for Qdrant to start (not healthy - acceptable for non-critical)
- API waits for MinIO init to complete

### Recommended Improvements

**Enhanced Startup Ordering**:
```yaml
api:
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
    qdrant:
      condition: service_healthy  # Changed from service_started
    minio-init:
      condition: service_completed_successfully
```

**Reason**: Qdrant should be healthy before API starts to ensure vector operations work correctly.

## Application-Level Health Checks

### Current Implementation

The application already has health endpoints:
- `/health` - Basic health check
- `/ready` - Readiness probe
- `/live` - Liveness probe

### Enhanced Health Check

Create a comprehensive health check that validates all dependencies:

```python
# apps/api/app/api/v1/routes/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
import httpx

router = APIRouter()

@router.get("/health/deep")
async def deep_health_check(db: AsyncSession = Depends(get_db)):
    """Deep health check validating all dependencies"""
    health_status = {
        "status": "healthy",
        "dependencies": {}
    }
    
    # Check PostgreSQL
    try:
        await db.execute("SELECT 1")
        health_status["dependencies"]["postgres"] = "healthy"
    except Exception as e:
        health_status["status"] "degraded"
        health_status["dependencies"]["postgres"] = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL"))
        await redis_client.ping()
        health_status["dependencies"]["redis"] = "healthy"
    except Exception as e:
        health_status["status"] = "degraded"
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
                health_status["status"] = "degraded"
                health_status["dependencies"]["qdrant"] = "unhealthy"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["dependencies"]["qdrant"] = f"unhealthy: {str(e)}"
    
    return health_status
```

## Retry Logic Enhancement

### Database Connection Retry

The application should implement retry logic for database connections:

```python
# apps/api/app/db/session.py
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
async def get_async_session_with_retry():
    """Get async session with retry logic"""
    return async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
```

### Redis Connection Retry

```python
# apps/api/app/core/redis.py
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def get_redis_with_retry():
    """Get Redis client with retry logic"""
    return redis.from_url(
        os.getenv("REDIS_URL"),
        encoding="utf-8",
        decode_responses=True,
    )
```

## Graceful Waiting

### Application Startup

The application should wait for dependencies to be ready:

```python
# apps/api/app/main.py
async def wait_for_dependencies():
    """Wait for all dependencies to be ready"""
    max_wait = 60
    interval = 2
    elapsed = 0
    
    while elapsed < max_wait:
        try:
            # Check PostgreSQL
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            
            # Check Redis
            redis_client = redis.from_url(os.getenv("REDIS_URL"))
            await redis_client.ping()
            
            # Check Qdrant
            async with httpx.AsyncClient() as client:
                await client.get(f"{os.getenv('QDRANT_URL')}/healthz")
            
            logger.info("All dependencies are ready")
            return True
        except Exception as e:
            logger.warning(f"Dependencies not ready yet: {e}")
            await asyncio.sleep(interval)
            elapsed += interval
    
    logger.error("Dependencies failed to become ready")
    return False

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting application...")
    
    # Wait for dependencies
    if not await wait_for_dependencies():
        logger.error("Failed to wait for dependencies")
        # Continue anyway - allow degraded mode
```

## Race Condition Prevention

### Docker Compose Dependencies

Ensure proper dependency ordering in docker-compose.yml:

```yaml
services:
  api:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_healthy
      minio-init:
        condition: service_completed_successfully
  
  worker:
    depends_on:
      api:
        condition: service_healthy
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
```

### Application-Level Ordering

The application should handle startup gracefully even if dependencies are not immediately ready:

```python
# apps/api/app/main.py
@app.on_event("startup")
async def startup_event():
    """Application startup event with graceful degradation"""
    logger.info("Starting application...")
    
    # Try to connect to dependencies
    postgres_ready = await check_postgres()
    redis_ready = await check_redis()
    qdrant_ready = await check_qdrant()
    
    if not all([postgres_ready, redis_ready, qdrant_ready]):
        logger.warning("Some dependencies are not ready, starting in degraded mode")
        # Continue anyway - allow degraded mode
    else:
        logger.info("All dependencies are ready")
```

## Validation

### Health Check Validation

Test all health checks:

```bash
# PostgreSQL
docker exec resume-intelligence-postgres-1 pg_isready -U resume -d resume_ai

# Redis
docker exec resume-intelligence-redis-1 redis-cli ping

# Qdrant
curl http://localhost:6333/healthz

# MinIO
docker exec resume-intelligence-minio-1 mc ready local

# MLflow
curl http://localhost:5000/health

# API
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/live
```

## Recommendations

### Immediate Actions

1. ✅ Healthchecks are already well-configured
2. ⚠️ Change Qdrant dependency from `service_started` to `service_healthy`
3. ⚠️ Add application-level dependency waiting
4. ⚠️ Add retry logic for database and Redis connections
5. ⚠️ Implement graceful degradation mode

### Long-term Improvements

1. Add circuit breakers for external services
2. Implement health check metrics
3. Add health check alerts
4. Implement automatic recovery
5. Add health check history

## Next Steps

1. ✅ Healthcheck stabilization documentation complete
2. ⏭️ STEP 4: Database bootstrap script
3. ⏭️ STEP 5: Environment validation
4. ⏭️ STEP 6: Local observability stability
5. ⏭️ STEP 7: Developer experience documentation
6. ⏭️ STEP 8: Final local validation

## Conclusion

The healthcheck configuration is already well-configured in docker-compose.yml. The main improvements needed are:
1. Change Qdrant dependency to wait for healthy state
2. Add application-level dependency waiting
3. Add retry logic for connections
4. Implement graceful degradation

These improvements will ensure deterministic startup ordering and eliminate race conditions.
