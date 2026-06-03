"""Async Connection Pool - Manage async connection pools."""

from dataclasses import dataclass
from typing import Any, Optional, Callable
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


@dataclass
class PoolConfig:
    """Connection pool configuration."""

    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True


class AsyncConnectionPool:
    """Async connection pool for database and external services."""

    def __init__(
        self,
        database_url: str,
        config: Optional[PoolConfig] = None,
    ) -> None:
        """Initialize async connection pool.

        Args:
            database_url: Database connection URL
            config: Pool configuration
        """
        self.config = config or PoolConfig()
        self.engine = create_async_engine(
            database_url,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            pool_pre_ping=self.config.pool_pre_ping,
            echo=False,
        )
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        """Get a database session from the pool.

        Yields:
            AsyncSession instance
        """
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def execute_query(
        self,
        query_fn: Callable[[AsyncSession], Any],
    ) -> Any:
        """Execute a query with a session from the pool.

        Args:
            query_fn: Query function

        Returns:
            Query result
        """
        async with self.get_session() as session:
            return await query_fn(session)

    async def close(self) -> None:
        """Close the connection pool."""
        await self.engine.dispose()

    async def get_pool_status(self) -> dict[str, Any]:
        """Get pool status.

        Returns:
            Dictionary with pool status
        """
        pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "max_overflow": self.config.max_overflow,
        }
