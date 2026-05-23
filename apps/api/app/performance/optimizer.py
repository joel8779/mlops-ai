"""Query Optimizer - Optimize database queries."""

from typing import Any, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession


class QueryOptimizer:
    """Optimize database queries for better performance."""

    @staticmethod
    def optimize_candidate_query(
        eager_load: bool = True,
        limit: int = 100,
    ):
        """Decorator to optimize candidate queries.

        Args:
            eager_load: Whether to use eager loading
            limit: Result limit

        Returns:
            Decorator function
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Apply optimizations
                if eager_load:
                    kwargs["options"] = [joinedload("resumes"), selectinload("skills")]

                if "limit" not in kwargs:
                    kwargs["limit"] = limit

                return await func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def use_index_hint(index_name: str):
        """Add index hint to query.

        Args:
            index_name: Name of index to use

        Returns:
            Decorator function
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                kwargs["index_hint"] = index_name
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def batch_fetch(batch_size: int = 100):
        """Fetch results in batches.

        Args:
            batch_size: Batch size

        Returns:
            Decorator function
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                kwargs["batch_size"] = batch_size
                return await func(*args, **kwargs)
            return wrapper
        return decorator
