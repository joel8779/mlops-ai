import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse
from sqlalchemy import text
import redis.asyncio as redis
import httpx

try:
    from prometheus_fastapi_instrumentator import Instrumentator
except ImportError:
    Instrumentator = None

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.dependency_guard import assert_core_dependency_runtime
from app.core.exceptions import install_exception_handlers
from app.logging import configure_logging, get_logger
from app.db.database import close_database
from app.db.schema_validation import get_runtime_schema_report, validate_runtime_schema
from app.db.session import engine
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.tenant import TenantContextMiddleware
from app.observability.tracing import configure_tracing, shutdown_tracing
from app.schemas.health import HealthResponse
from app.services.email_service import EmailService
import app.observability.metrics  # Ensure all prometheus metrics are registered at startup

configure_logging()
logger = get_logger(__name__)

def custom_key_func(request: Request) -> str | None:
    if request.url.path in {"/ready", "/live", "/metrics", "/health", "/smtp-health"}:
        return None
    return get_remote_address(request)

limiter = Limiter(key_func=custom_key_func, default_limits=[settings.rate_limit_default])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Production-grade lifespan manager with graceful shutdown.

    Handles startup/shutdown with proper exception suppression for
    expected shutdown signals (CancelledError, KeyboardInterrupt).
    """
    # Startup
    logger.info("api_starting", environment=settings.environment, version=settings.app_version)
    dependency_results = assert_core_dependency_runtime()
    logger.info(
        "core_dependency_runtime_validated",
        dependencies={result.name: result.installed_version for result in dependency_results},
    )
    schema_report = await validate_runtime_schema()
    if schema_report.ready:
        logger.info("runtime_schema_validated")
    else:
        logger.warning("runtime_schema_drift_detected", schema=schema_report.model_dump())
    email_service = EmailService()
    email_service.validate_configuration()
    try:
        yield
    except (asyncio.CancelledError, KeyboardInterrupt):
        # Expected shutdown signals - suppress noisy traces
        logger.info("api_shutdown_signal", reason="user_interrupt")
    finally:
        # Shutdown sequence
        logger.info("api_stopping")
        try:
            # Close database connections
            await close_database()
            # Shutdown telemetry exporters
            await shutdown_tracing()
            logger.info("api_stopped", status="clean")
        except asyncio.CancelledError:
            # Suppress final CancelledError during cleanup
            logger.info("api_stopped", status="cancelled")
        except Exception as exc:
            # Log unexpected errors during shutdown but don't crash
            logger.warning("api_shutdown_error", error=str(exc), exc_info=False)


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Resume Intelligence API",
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url=None,
        lifespan=lifespan,
    )
    app.state.limiter = limiter

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(TenantContextMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    install_exception_handlers(app)
    configure_tracing(app)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request, exc: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

    @app.get("/", tags=["system"])
    async def root() -> dict[str, str]:
        """Root endpoint with service information."""
        return {
            "status": "healthy",
            "service": "AI Resume Intelligence Platform",
            "version": settings.app_version,
            "environment": settings.environment,
            "docs": "/docs",
            "health": "/health",
            "ready": "/ready",
            "live": "/live",
            "metrics": "/metrics",
        }

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    async def health() -> HealthResponse:
        """Liveness check: process is up and able to serve HTTP."""
        return HealthResponse(status="ok", service=settings.app_name, version=settings.app_version)

    @app.get("/ready", tags=["system"])
    async def ready() -> JSONResponse:
        """Readiness check: dependencies and schema are ready for workflows."""
        payload = await _readiness_payload()
        status_code = 200 if payload["status"] == "ready" else 503
        return JSONResponse(status_code=status_code, content=payload)

    @app.get("/live", response_model=HealthResponse, tags=["system"])
    async def live() -> HealthResponse:
        """Liveness check endpoint - Kubernetes live probe."""
        return HealthResponse(status="alive", service=settings.app_name, version=settings.app_version)

    @app.get("/smtp-health", tags=["system"])
    async def smtp_health() -> JSONResponse:
        email_service = EmailService()
        report = await email_service.verify_connection_async()
        status_code = 200 if report["status"] in {"healthy", "configured", "disabled"} else 503
        return JSONResponse(status_code=status_code, content=report)

    app.include_router(api_router, prefix="/api/v1")
    if Instrumentator is not None:
        Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
    return app


async def _readiness_payload() -> dict:
    dependencies: dict[str, dict] = {}
    status = "ready"

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        dependencies["postgres"] = {"status": "healthy"}
    except Exception as exc:
        status = "not_ready"
        dependencies["postgres"] = {"status": "unhealthy", "error": str(exc)}

    try:
        redis_client = redis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.aclose()
        dependencies["redis"] = {"status": "healthy"}
    except Exception as exc:
        status = "not_ready"
        dependencies["redis"] = {"status": "unhealthy", "error": str(exc)}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{str(settings.qdrant_url).rstrip('/')}/healthz")
        if response.status_code == 200:
            dependencies["qdrant"] = {"status": "healthy"}
        else:
            status = "not_ready"
            dependencies["qdrant"] = {"status": "unhealthy", "status_code": response.status_code}
    except Exception as exc:
        status = "not_ready"
        dependencies["qdrant"] = {"status": "unhealthy", "error": str(exc)}

    try:
        schema_report = await get_runtime_schema_report()
        dependencies["schema"] = schema_report.model_dump()
        if schema_report.status in {"drift_detected", "validation_error"}:
            status = "not_ready"
            logger.warning(
                "readiness_schema_check_failed",
                status=schema_report.status,
                current_revision=schema_report.current_revision,
                expected_revision=schema_report.expected_revision,
                drift=[item.message() for item in schema_report.drift],
                error=schema_report.error,
            )
    except Exception as exc:
        status = "not_ready"
        dependencies["schema"] = {"status": "unhealthy", "error": str(exc)}
        logger.exception("readiness_schema_check_error", error=str(exc))

    dependencies["gemini"] = {
        "status": "configured" if settings.llm_provider == "disabled" or settings.gemini_api_key else "degraded",
        "provider": settings.llm_provider,
    }

    smtp_report = EmailService().health_report()
    dependencies["smtp"] = smtp_report

    return {
        "status": status,
        "service": settings.app_name,
        "version": settings.app_version,
        "dependencies": dependencies,
    }


app = create_app()
