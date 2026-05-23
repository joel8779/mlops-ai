"""Evaluation Suite - Comprehensive AI evaluation."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.benchmarking.benchmark_runner import BenchmarkRunner
from app.benchmarking.metrics_calculator import MetricsCalculator


@dataclass
class EvaluationResult:
    """Result of an evaluation."""

    evaluation_id: UUID
    name: str
    metrics: dict[str, float]
    benchmark_results: list[Any]
    timestamp: datetime
    metadata: dict[str, Any]


class EvaluationSuite:
    """Comprehensive evaluation suite for AI systems."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize evaluation suite.

        Args:
            db: Database session
        """
        self.db = db
        self.benchmark_runner = BenchmarkRunner(db)
        self.metrics_calculator = MetricsCalculator()
        self.evaluations: list[EvaluationResult] = []

    async def evaluate_llm_quality(
        self,
        model_name: str,
        test_cases: list[dict[str, Any]],
        evaluation_fn: Callable,
    ) -> EvaluationResult:
        """Evaluate LLM quality.

        Args:
            model_name: Name of the model being evaluated
            test_cases: List of test cases
            evaluation_fn: Function to evaluate responses

        Returns:
            EvaluationResult object
        """
        evaluation_id = UUID()

        # Run evaluation
        scores = []
        for test_case in test_cases:
            score = await evaluation_fn(test_case)
            scores.append(score)

        avg_score = sum(scores) / len(scores) if scores else 0

        result = EvaluationResult(
            evaluation_id=evaluation_id,
            name=f"llm_quality_{model_name}",
            metrics={
                "average_score": avg_score,
                "min_score": min(scores) if scores else 0,
                "max_score": max(scores) if scores else 0,
                "test_cases_count": len(test_cases),
            },
            benchmark_results=[],
            timestamp=datetime.now(timezone.utc),
            metadata={"model_name": model_name},
        )

        self.evaluations.append(result)
        return result

    async def evaluate_ranking_quality(
        self,
        ranked_lists: list[list[int]],
        relevant_items: list[list[int]],
        k: int = 10,
    ) -> EvaluationResult:
        """Evaluate ranking quality.

        Args:
            ranked_lists: List of ranked item lists
            relevant_items: List of relevant items
            k: Cutoff for metrics

        Returns:
            EvaluationResult object
        """
        evaluation_id = UUID()

        metrics = self.metrics_calculator.calculate_ranking_metrics(
            ranked_lists,
            relevant_items,
            k,
        )

        result = EvaluationResult(
            evaluation_id=evaluation_id,
            name="ranking_quality",
            metrics={
                "ndcg": metrics.ndcg,
                "mrr": metrics.mean_reciprocal_rank,
                "map": metrics.mean_average_precision,
                **{f"precision_at_{k}": v for k, v in metrics.precision_at_k.items()},
            },
            benchmark_results=[],
            timestamp=datetime.now(timezone.utc),
            metadata={"k": k, "queries_count": len(ranked_lists)},
        )

        self.evaluations.append(result)
        return result

    async def evaluate_performance(
        self,
        benchmarks: dict[str, Callable],
    ) -> EvaluationResult:
        """Evaluate system performance.

        Args:
            benchmarks: Dictionary of benchmark names to functions

        Returns:
            EvaluationResult object
        """
        evaluation_id = UUID()

        benchmark_results = await self.benchmark_runner.run_suite(benchmarks)

        metrics = {}
        for result in benchmark_results:
            metrics[f"{result.name}_duration_ms"] = result.duration_ms
            metrics[f"{result.name}_success"] = 1 if result.success else 0

        result = EvaluationResult(
            evaluation_id=evaluation_id,
            name="performance",
            metrics=metrics,
            benchmark_results=benchmark_results,
            timestamp=datetime.now(timezone.utc),
            metadata={"benchmarks_count": len(benchmarks)},
        )

        self.evaluations.append(result)
        return result

    def get_evaluations(self) -> list[EvaluationResult]:
        """Get all evaluation results.

        Returns:
            List of EvaluationResult objects
        """
        return self.evaluations

    def clear_evaluations(self) -> None:
        """Clear all evaluation results."""
        self.evaluations.clear()
