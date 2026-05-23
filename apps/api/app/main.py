import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import install_exception_handlers
from app.logging import configure_logging, get_logger
from app.db.database import check_database, close_database
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.tenant import TenantContextMiddleware
from app.observability.tracing import configure_tracing, shutdown_tracing
from app.schemas.health import HealthResponse

configure_logging()
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit_default])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Production-grade lifespan manager with graceful shutdown.

    Handles startup/shutdown with proper exception suppression for
    expected shutdown signals (CancelledError, KeyboardInterrupt).
    """
    # Startup
    logger.info("api_starting", environment=settings.environment, version=settings.app_version)
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
        """Health check endpoint - verifies service health."""
        await check_database()
        return HealthResponse(status="ok", service=settings.app_name, version=settings.app_version)

    @app.get("/ready", response_model=HealthResponse, tags=["system"])
    async def ready() -> HealthResponse:
        """Readiness check endpoint - Kubernetes ready probe."""
        await check_database()
        return HealthResponse(status="ready", service=settings.app_name, version=settings.app_version)

    @app.get("/live", response_model=HealthResponse, tags=["system"])
    async def live() -> HealthResponse:
        """Liveness check endpoint - Kubernetes live probe."""
        return HealthResponse(status="alive", service=settings.app_name, version=settings.app_version)

    app.include_router(api_router, prefix="/api/v1")
    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
    return app


app = create_app()
