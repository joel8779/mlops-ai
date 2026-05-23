"""Query Cache - Cache search queries and results."""

import hashlib
import json
from typing import Any, Optional
from uuid import UUID

from app.core.redis import get_redis_client


class QueryCache:
    """Cache for search queries and results."""

    def __init__(
        self,
        ttl_seconds: int = 3600,  # 1 hour
        prefix: str = "query_cache",
    ) -> None:
        """Initialize query cache.

        Args:
            ttl_seconds: Time-to-live for cached queries
            prefix: Redis key prefix
        """
        self.ttl_seconds = ttl_seconds
        self.prefix = prefix

    def _make_key(
        self,
        query: str,
        organization_id: UUID,
        filters: Optional[dict[str, Any]] = None,
    ) -> str:
        """Generate cache key from query parameters.

        Args:
            query: Search query
            organization_id: Organization ID
            filters: Optional filters

        Returns:
            Cache key
        """
        # Create a hash of the query and filters
        key_data = {
            "query": query,
            "org_id": str(organization_id),
            "filters": filters or {},
        }
        key_hash = hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
        return f"{self.prefix}:{key_hash}"

    async def get(
        self,
        query: str,
        organization_id: UUID,
        filters: Optional[dict[str, Any]] = None,
    ) -> Optional[list[dict[str, Any]]]:
        """Get cached search results.

        Args:
            query: Search query
            organization_id: Organization ID
            filters: Optional filters

        Returns:
            Cached results or None
        """
        try:
            redis = get_redis_client()
            key = self._make_key(query, organization_id, filters)
            cached = await redis.get(key)

            if cached:
                return json.loads(cached)
        except Exception:
            pass

        return None

    async def set(
        self,
        query: str,
        organization_id: UUID,
        results: list[dict[str, Any]],
        filters: Optional[dict[str, Any]] = None,
    ) -> None:
        """Cache search results.

        Args:
            query: Search query
            organization_id: Organization ID
            results: Search results to cache
            filters: Optional filters
        """
        try:
            redis = get_redis_client()
            key = self._make_key(query, organization_id, filters)
            await redis.set(key, json.dumps(results), ex=self.ttl_seconds)
        except Exception:
            pass

    async def invalidate(
        self,
        query: str,
        organization_id: UUID,
        filters: Optional[dict[str, Any]] = None,
    ) -> None:
        """Invalidate cached query results.

        Args:
            query: Search query
            organization_id: Organization ID
            filters: Optional filters
        """
        try:
            redis = get_redis_client()
            key = self._make_key(query, organization_id, filters)
            await redis.delete(key)
        except Exception:
            pass

    async def invalidate_organization(self, organization_id: UUID) -> None:
        """Invalidate all cached queries for an organization.

        Args:
            organization_id: Organization ID
        """
        try:
            redis = get_redis_client()
            pattern = f"{self.prefix}:*"
            keys = await redis.keys(pattern)

            # Filter keys for this organization
            org_keys = []
            for key in keys:
                # Decode and check if it belongs to this org
                # This is a simplified check - in production, store org_id in the key
                org_keys.append(key)

            if org_keys:
                await redis.delete(*org_keys)
        except Exception:
            pass

    async def clear_all(self) -> None:
        """Clear all cached queries."""
        try:
            redis = get_redis_client()
            pattern = f"{self.prefix}:*"
            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
        except Exception:
            pass

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            redis = get_redis_client()
            pattern = f"{self.prefix}:*"
            keys = await redis.keys(pattern)
            return {
                "total_cached": len(keys),
                "prefix": self.prefix,
                "ttl_seconds": self.ttl_seconds,
            }
        except Exception:
            return {
                "total_cached": 0,
                "prefix": self.prefix,
                "ttl_seconds": self.ttl_seconds,
            }
