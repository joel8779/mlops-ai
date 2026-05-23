"""Benchmark Runner - Run performance benchmarks."""

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""

    benchmark_id: UUID
    name: str
    duration_ms: float
    success: bool
    error: Optional[str]
    metadata: dict[str, Any]
    timestamp: datetime


class BenchmarkRunner:
    """Run performance benchmarks on system components."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize benchmark runner.

        Args:
            db: Database session
        """
        self.db = db
        self.results: list[BenchmarkResult] = []

    async def run_benchmark(
        self,
        name: str,
        fn: Callable,
        iterations: int = 10,
        warmup_iterations: int = 3,
    ) -> BenchmarkResult:
        """Run a benchmark.

        Args:
            name: Benchmark name
            fn: Function to benchmark
            iterations: Number of iterations
            warmup_iterations: Number of warmup iterations

        Returns:
            BenchmarkResult object
        """
        benchmark_id = UUID()

        # Warmup
        for _ in range(warmup_iterations):
            try:
                if asyncio.iscoroutinefunction(fn):
                    await fn()
                else:
                    fn()
            except Exception:
                pass

        # Benchmark
        durations = []
        for _ in range(iterations):
            try:
                start = time.perf_counter()
                if asyncio.iscoroutinefunction(fn):
                    await fn()
                else:
                    fn()
                duration = (time.perf_counter() - start) * 1000
                durations.append(duration)
            except Exception as e:
                result = BenchmarkResult(
                    benchmark_id=benchmark_id,
                    name=name,
                    duration_ms=0,
                    success=False,
                    error=str(e),
                    metadata={"iterations": iterations},
                    timestamp=datetime.now(timezone.utc),
                )
                self.results.append(result)
                return result

        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)

        result = BenchmarkResult(
            benchmark_id=benchmark_id,
            name=name,
            duration_ms=avg_duration,
            success=True,
            error=None,
            metadata={
                "iterations": iterations,
                "min_duration_ms": min_duration,
                "max_duration_ms": max_duration,
                "std_dev": (sum((d - avg_duration) ** 2 for d in durations) / len(durations)) ** 0.5,
            },
            timestamp=datetime.now(timezone.utc),
        )

        self.results.append(result)
        return result

    async def run_suite(
        self,
        benchmarks: dict[str, Callable],
    ) -> list[BenchmarkResult]:
        """Run a suite of benchmarks.

        Args:
            benchmarks: Dictionary of benchmark names to functions

        Returns:
            List of BenchmarkResult objects
        """
        results = []
        for name, fn in benchmarks.items():
            result = await self.run_benchmark(name, fn)
            results.append(result)
        return results

    def get_results(self) -> list[BenchmarkResult]:
        """Get all benchmark results.

        Returns:
            List of BenchmarkResult objects
        """
        return self.results

    def clear_results(self) -> None:
        """Clear all benchmark results."""
        self.results.clear()
