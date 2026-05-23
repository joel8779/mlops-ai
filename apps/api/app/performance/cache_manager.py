"""Cache Manager - Multi-level caching strategy."""

import json
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Callable
from functools import wraps

from app.core.redis import get_redis_client


@dataclass
class CacheConfig:
    """Cache configuration."""

    ttl_seconds: int = 3600
    prefix: str = "cache"
    enable_local: bool = True
    enable_redis: bool = True
    local_max_size: int = 1000


class CacheManager:
    """Multi-level cache manager with L1 (local) and L2 (Redis) caching."""

    def __init__(self, config: Optional[CacheConfig] = None) -> None:
        """Initialize cache manager.

        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig()
        self._local_cache: dict[str, tuple[Any, datetime]] = {}
        self._local_cache_order: list[str] = []

    def _make_key(self, *args: Any, **kwargs: Any) -> str:
        """Generate cache key from arguments.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Cache key string
        """
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()
        return f"{self.config.prefix}:{key_hash}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        # Try local cache first
        if self.config.enable_local:
            if key in self._local_cache:
                value, expiry = self._local_cache[key]
                if datetime.now(timezone.utc) < expiry:
                    return value
                else:
                    # Expired, remove from local cache
                    self._remove_from_local(key)

        # Try Redis cache
        if self.config.enable_redis:
            try:
                redis = get_redis_client()
                cached = await redis.get(key)
                if cached:
                    value = json.loads(cached)
                    # Store in local cache
                    if self.config.enable_local:
                        self._add_to_local(key, value, self.config.ttl_seconds)
                    return value
            except Exception:
                pass

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        ttl = ttl or self.config.ttl_seconds

        # Set in local cache
        if self.config.enable_local:
            self._add_to_local(key, value, ttl)

        # Set in Redis cache
        if self.config.enable_redis:
            try:
                redis = get_redis_client()
                await redis.set(key, json.dumps(value), ex=ttl)
            except Exception:
                pass

    async def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key
        """
        # Remove from local cache
        if self.config.enable_local:
            self._remove_from_local(key)

        # Remove from Redis cache
        if self.config.enable_redis:
            try:
                redis = get_redis_client()
                await redis.delete(key)
            except Exception:
                pass

    async def clear(self) -> None:
        """Clear all cached values."""
        self._local_cache.clear()
        self._local_cache_order.clear()

        if self.config.enable_redis:
            try:
                redis = get_redis_client()
                pattern = f"{self.config.prefix}:*"
                keys = await redis.keys(pattern)
                if keys:
                    await redis.delete(*keys)
            except Exception:
                pass

    def _add_to_local(self, key: str, value: Any, ttl: int) -> None:
        """Add value to local cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        expiry = datetime.now(timezone.utc) + timedelta(seconds=ttl)

        # Evict if over limit
        if len(self._local_cache) >= self.config.local_max_size:
            oldest_key = self._local_cache_order.pop(0)
            del self._local_cache[oldest_key]

        self._local_cache[key] = (value, expiry)
        self._local_cache_order.append(key)

    def _remove_from_local(self, key: str) -> None:
        """Remove value from local cache.

        Args:
            key: Cache key
        """
        if key in self._local_cache:
            del self._local_cache[key]
        if key in self._local_cache_order:
            self._local_cache_order.remove(key)

    def cached(self, ttl: Optional[int] = None):
        """Decorator for caching function results.

        Args:
            ttl: Time to live in seconds

        Returns:
            Decorator function
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                key = self._make_key(func.__name__, *args, **kwargs)
                result = await self.get(key)
                if result is not None:
                    return result

                result = await func(*args, **kwargs)
                await self.set(key, result, ttl)
                return result

            return wrapper
        return decorator

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        stats = {
            "local_cache_size": len(self._local_cache),
            "local_cache_max_size": self.config.local_max_size,
            "local_enabled": self.config.enable_local,
            "redis_enabled": self.config.enable_redis,
        }

        if self.config.enable_redis:
            try:
                redis = get_redis_client()
                pattern = f"{self.config.prefix}:*"
                keys = await redis.keys(pattern)
                stats["redis_cache_size"] = len(keys)
            except Exception:
                stats["redis_cache_size"] = 0

        return stats
