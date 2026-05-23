"""Query Batcher - Batch database queries for efficiency."""

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_


@dataclass
class BatchConfig:
    """Batch configuration."""

    max_batch_size: int = 100
    max_wait_time_ms: int = 100
    enable_deduplication: bool = True


class QueryBatcher:
    """Batch database queries to reduce round trips."""

    def __init__(self, config: Optional[BatchConfig] = None) -> None:
        """Initialize query batcher.

        Args:
            config: Batch configuration
        """
        self.config = config or BatchConfig()
        self._batches: dict[str, list] = defaultdict(list)
        self._pending: dict[str, list] = defaultdict(list)
        self._results: dict[str, Any] = {}

    async def add_query(
        self,
        batch_key: str,
        query_fn: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Add a query to a batch.

        Args:
            batch_key: Key to identify the batch
            query_fn: Query function to execute
            *args: Query arguments
            **kwargs: Query keyword arguments

        Returns:
            Query ID
        """
        query_id = str(UUID())
        self._batches[batch_key].append({
            "id": query_id,
            "fn": query_fn,
            "args": args,
            "kwargs": kwargs,
        })

        # Check if batch is ready to execute
        if len(self._batches[batch_key]) >= self.config.max_batch_size:
            await self._execute_batch(batch_key)

        return query_id

    async def get_result(self, query_id: str) -> Optional[Any]:
        """Get result for a query.

        Args:
            query_id: Query ID

        Returns:
            Query result or None
        """
        return self._results.get(query_id)

    async def flush_all(self) -> None:
        """Flush all pending batches."""
        for batch_key in list(self._batches.keys()):
            if self._batches[batch_key]:
                await self._execute_batch(batch_key)

    async def _execute_batch(self, batch_key: str) -> None:
        """Execute a batch of queries.

        Args:
            batch_key: Batch key
        """
        queries = self._batches[batch_key]
        if not queries:
            return

        # Execute all queries in parallel
        tasks = []
        for query in queries:
            task = query["fn"](*query["args"], **query["kwargs"])
            tasks.append((query["id"], task))

        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

        # Store results
        for (query_id, _), result in zip(tasks, results):
            if not isinstance(result, Exception):
                self._results[query_id] = result

        # Clear batch
        self._batches[batch_key].clear()

    async def get_batch_stats(self) -> dict[str, Any]:
        """Get batch statistics.

        Returns:
            Dictionary with batch statistics
        """
        return {
            "pending_batches": len(self._batches),
            "total_pending_queries": sum(len(queries) for queries in self._batches.values()),
            "completed_queries": len(self._results),
            "max_batch_size": self.config.max_batch_size,
        }
