"""Token tracking and cost accounting for LLM usage."""

import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class TokenUsage:
    """Token usage record for a single request."""

    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    feature: str = ""


@dataclass
class TokenStats:
    """Aggregated token statistics."""

    total_requests: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0

    def add_usage(self, usage: TokenUsage) -> None:
        """Add a usage record to stats."""
        self.total_requests += 1
        self.total_prompt_tokens += usage.prompt_tokens
        self.total_completion_tokens += usage.completion_tokens
        self.total_tokens += usage.total_tokens
        self.total_cost_usd += usage.cost_usd


class TokenTracker:
    """Thread-safe token tracker for cost accounting and observability."""

    def __init__(self) -> None:
        """Initialize token tracker."""
        self._lock = threading.Lock()
        self._usage_history: list[TokenUsage] = []
        self._stats_by_model: dict[str, TokenStats] = defaultdict(TokenStats)
        self._stats_by_feature: dict[str, TokenStats] = defaultdict(TokenStats)
        self._global_stats = TokenStats()

    def track(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        feature: str = "",
    ) -> TokenUsage:
        """Track a single LLM usage.

        Args:
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            cost_usd: Estimated cost in USD
            feature: Feature name (e.g., "candidate_summary")

        Returns:
            TokenUsage record
        """
        total_tokens = prompt_tokens + completion_tokens

        usage = TokenUsage(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            feature=feature,
        )

        with self._lock:
            self._usage_history.append(usage)
            self._global_stats.add_usage(usage)
            self._stats_by_model[model].add_usage(usage)
            if feature:
                self._stats_by_feature[feature].add_usage(usage)

        return usage

    def get_global_stats(self) -> TokenStats:
        """Get global token statistics.

        Returns:
            Global TokenStats
        """
        with self._lock:
            return TokenStats(
                total_requests=self._global_stats.total_requests,
                total_prompt_tokens=self._global_stats.total_prompt_tokens,
                total_completion_tokens=self._global_stats.total_completion_tokens,
                total_tokens=self._global_stats.total_tokens,
                total_cost_usd=self._global_stats.total_cost_usd,
            )

    def get_model_stats(self, model: str) -> Optional[TokenStats]:
        """Get statistics for a specific model.

        Args:
            model: Model name

        Returns:
            TokenStats for the model, or None if not found
        """
        with self._lock:
            stats = self._stats_by_model.get(model)
            if stats:
                return TokenStats(
                    total_requests=stats.total_requests,
                    total_prompt_tokens=stats.total_prompt_tokens,
                    total_completion_tokens=stats.total_completion_tokens,
                    total_tokens=stats.total_tokens,
                    total_cost_usd=stats.total_cost_usd,
                )
            return None

    def get_feature_stats(self, feature: str) -> Optional[TokenStats]:
        """Get statistics for a specific feature.

        Args:
            feature: Feature name

        Returns:
            TokenStats for the feature, or None if not found
        """
        with self._lock:
            stats = self._stats_by_feature.get(feature)
            if stats:
                return TokenStats(
                    total_requests=stats.total_requests,
                    total_prompt_tokens=stats.total_prompt_tokens,
                    total_completion_tokens=stats.total_completion_tokens,
                    total_tokens=stats.total_tokens,
                    total_cost_usd=stats.total_cost_usd,
                )
            return None

    def get_all_model_stats(self) -> dict[str, TokenStats]:
        """Get statistics for all models.

        Returns:
            Dictionary mapping model names to TokenStats
        """
        with self._lock:
            return {
                model: TokenStats(
                    total_requests=stats.total_requests,
                    total_prompt_tokens=stats.total_prompt_tokens,
                    total_completion_tokens=stats.total_completion_tokens,
                    total_tokens=stats.total_tokens,
                    total_cost_usd=stats.total_cost_usd,
                )
                for model, stats in self._stats_by_model.items()
            }

    def get_all_feature_stats(self) -> dict[str, TokenStats]:
        """Get statistics for all features.

        Returns:
            Dictionary mapping feature names to TokenStats
        """
        with self._lock:
            return {
                feature: TokenStats(
                    total_requests=stats.total_requests,
                    total_prompt_tokens=stats.total_prompt_tokens,
                    total_completion_tokens=stats.total_completion_tokens,
                    total_tokens=stats.total_tokens,
                    total_cost_usd=stats.total_cost_usd,
                )
                for feature, stats in self._stats_by_feature.items()
            }

    def get_recent_usage(self, limit: int = 100) -> list[TokenUsage]:
        """Get recent usage records.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of recent TokenUsage records
        """
        with self._lock:
            return self._usage_history[-limit:]

    def reset(self) -> None:
        """Reset all tracking data."""
        with self._lock:
            self._usage_history.clear()
            self._stats_by_model.clear()
            self._stats_by_feature.clear()
            self._global_stats = TokenStats()

    def get_usage_summary(self) -> dict[str, any]:
        """Get a comprehensive usage summary.

        Returns:
            Dictionary with usage summary
        """
        with self._lock:
            return {
                "global": {
                    "total_requests": self._global_stats.total_requests,
                    "total_prompt_tokens": self._global_stats.total_prompt_tokens,
                    "total_completion_tokens": self._global_stats.total_completion_tokens,
                    "total_tokens": self._global_stats.total_tokens,
                    "total_cost_usd": round(self._global_stats.total_cost_usd, 4),
                },
                "by_model": {
                    model: {
                        "total_requests": stats.total_requests,
                        "total_tokens": stats.total_tokens,
                        "total_cost_usd": round(stats.total_cost_usd, 4),
                    }
                    for model, stats in self._stats_by_model.items()
                },
                "by_feature": {
                    feature: {
                        "total_requests": stats.total_requests,
                        "total_tokens": stats.total_tokens,
                        "total_cost_usd": round(stats.total_cost_usd, 4),
                    }
                    for feature, stats in self._stats_by_feature.items()
                },
            }
