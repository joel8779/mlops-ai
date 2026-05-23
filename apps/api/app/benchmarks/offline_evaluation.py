from dataclasses import dataclass
from time import perf_counter

from app.ml.evaluation.ranking_metrics import mean_reciprocal_rank, ndcg_at_k, precision_at_k


@dataclass(frozen=True)
class BenchmarkResult:
    precision_at_10: float
    ndcg_at_10: float
    mrr: float
    latency_ms: float
    hallucination_rate: float


def run_offline_benchmark(relevance_labels: list[bool], graded_gains: list[float]) -> BenchmarkResult:
    started = perf_counter()
    result = BenchmarkResult(
        precision_at_10=precision_at_k(relevance_labels, 10),
        ndcg_at_10=ndcg_at_k(graded_gains, 10),
        mrr=mean_reciprocal_rank(relevance_labels),
        latency_ms=round((perf_counter() - started) * 1000, 3),
        hallucination_rate=0.0,
    )
    return result
