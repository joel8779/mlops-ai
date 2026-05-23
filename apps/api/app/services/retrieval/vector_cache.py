"""Vector Cache - Cache embeddings and vectors to reduce computation."""

import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from uuid import UUID

from app.core.redis import get_redis_client


class VectorCache:
    """Cache for embeddings and vectors."""

    def __init__(
        self,
        ttl_seconds: int = 86400,  # 24 hours
        prefix: str = "vector_cache",
    ) -> None:
        """Initialize vector cache.

        Args:
            ttl_seconds: Time-to-live for cached items
            prefix: Redis key prefix
        """
        self.ttl_seconds = ttl_seconds
        self.prefix = prefix

    def _make_key(self, text: str, model: str) -> str:
        """Generate cache key from text and model.

        Args:
            text: Text to embed
            model: Model name

        Returns:
            Cache key
        """
        # Hash the text to create a consistent key
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        return f"{self.prefix}:{model}:{text_hash}"

    async def get(self, text: str, model: str) -> Optional[list[float]]:
        """Get cached embedding.

        Args:
            text: Text that was embedded
            model: Model name used

        Returns:
            Cached embedding or None
        """
        try:
            redis = get_redis_client()
            key = self._make_key(text, model)
            cached = await redis.get(key)

            if cached:
                return json.loads(cached)
        except Exception:
            pass

        return None

    async def set(
        self,
        text: str,
        model: str,
        embedding: list[float],
    ) -> None:
        """Cache an embedding.

        Args:
            text: Text that was embedded
            model: Model name used
            embedding: Embedding vector
        """
        try:
            redis = get_redis_client()
            key = self._make_key(text, model)
            await redis.set(key, json.dumps(embedding), ex=self.ttl_seconds)
        except Exception:
            pass

    async def get_batch(
        self,
        texts: list[str],
        model: str,
    ) -> dict[str, Optional[list[float]]]:
        """Get multiple cached embeddings.

        Args:
            texts: List of texts
            model: Model name

        Returns:
            Dictionary mapping text to cached embedding or None
        """
        results = {}
        for text in texts:
            results[text] = await self.get(text, model)
        return results

    async def set_batch(
        self,
        embeddings: dict[str, list[float]],
        model: str,
    ) -> None:
        """Cache multiple embeddings.

        Args:
            embeddings: Dictionary mapping text to embedding
            model: Model name
        """
        for text, embedding in embeddings.items():
            await self.set(text, model, embedding)

    async def invalidate(self, text: str, model: str) -> None:
        """Invalidate a cached embedding.

        Args:
            text: Text to invalidate
            model: Model name
        """
        try:
            redis = get_redis_client()
            key = self._make_key(text, model)
            await redis.delete(key)
        except Exception:
            pass

    async def clear_all(self) -> None:
        """Clear all cached vectors."""
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
