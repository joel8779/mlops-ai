"""Pytest configuration for deterministic testing."""

import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler

from app.main import create_app
from app.db.session import get_db
from app.models.base import Base

SQLiteTypeCompiler.visit_JSONB = SQLiteTypeCompiler.visit_JSON


def _visit_uuid_for_sqlite(self, type_, **kw):
    return "VARCHAR(36)"

SQLiteTypeCompiler.visit_UUID = _visit_uuid_for_sqlite


# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests.

    Yields:
        AsyncIO event loop
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db():
    """Create an isolated test database.

    Yields:
        AsyncSession for test database
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_client(test_db):
    """Create a test client with database session.

    Args:
        test_db: Test database fixture

    Yields:
        AsyncClient for testing
    """
    app = create_app()
    
    # Override database dependency
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def redis_client():
    """Create a test Redis client.

    Yields:
        Redis client for testing
    """
    try:
        from redis.asyncio import Redis
        redis = Redis.from_url("redis://localhost:6379/15", decode_responses=True)
        await redis.ping()
        yield redis
        await redis.flushdb()
        await redis.close()
    except Exception:
        # Skip Redis tests if not available
        pytest.skip("Redis not available for testing")


@pytest.fixture(scope="function")
async def clean_redis(redis_client):
    """Clean Redis after test.

    Args:
        redis_client: Redis client fixture
    """
    yield
    if redis_client:
        await redis_client.flushdb()


@pytest.fixture(scope="function")
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing.

    Args:
        monkeypatch: Pytest monkeypatch fixture

    Yields:
        None
    """
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LLM_PROVIDER", "disabled")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/15")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    yield


# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(autouse=True)
async def cleanup_telemetry():
    """Clean up telemetry after each test.

    Yields:
        None
    """
    yield
    # Clean up any telemetry side effects
    # Clear metrics if needed
    # This is a no-op for now but can be expanded


@pytest.fixture(scope="session")
def app():
    """Create FastAPI app for testing.

    Yields:
        FastAPI app instance
    """
    return create_app()
