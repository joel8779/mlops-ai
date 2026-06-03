"""Metrics Calculator - Calculate evaluation metrics."""

from dataclasses import dataclass
from typing import List
import numpy as np


@dataclass
class ClassificationMetrics:
    """Classification evaluation metrics."""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int


@dataclass
class RankingMetrics:
    """Ranking evaluation metrics."""

    ndcg: float  # Normalized Discounted Cumulative Gain
    precision_at_k: dict[int, float]
    mean_reciprocal_rank: float
    mean_average_precision: float


class MetricsCalculator:
    """Calculate evaluation metrics for AI systems."""

    @staticmethod
    def calculate_classification_metrics(
        predictions: List[int],
        labels: List[int],
    ) -> ClassificationMetrics:
        """Calculate classification metrics.

        Args:
            predictions: Predicted labels
            labels: Ground truth labels

        Returns:
            ClassificationMetrics object
        """
        true_positives = sum(1 for p, l in zip(predictions, labels) if p == 1 and l == 1)
        false_positives = sum(1 for p, l in zip(predictions, labels) if p == 1 and l == 0)
        true_negatives = sum(1 for p, l in zip(predictions, labels) if p == 0 and l == 0)
        false_negatives = sum(1 for p, l in zip(predictions, labels) if p == 0 and l == 1)

        accuracy = (true_positives + true_negatives) / len(labels) if labels else 0
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return ClassificationMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            true_positives=true_positives,
            false_positives=false_positives,
            true_negatives=true_negatives,
            false_negatives=false_negatives,
        )

    @staticmethod
    def calculate_ranking_metrics(
        ranked_lists: List[List[int]],
        relevant_items: List[List[int]],
        k: int = 10,
    ) -> RankingMetrics:
        """Calculate ranking metrics.

        Args:
            ranked_lists: List of ranked item lists
            relevant_items: List of relevant items for each query
            k: Cutoff for precision@k

        Returns:
            RankingMetrics object
        """
        # Calculate NDCG
        ndcg_scores = []
        for ranked, relevant in zip(ranked_lists, relevant_items):
            dcg = 0
            for i, item in enumerate(ranked[:k]):
                if item in relevant:
                    dcg += 1 / np.log2(i + 2)
            # Ideal DCG
            ideal_ranked = sorted(relevant, reverse=True)
            idcg = 0
            for i, item in enumerate(ideal_ranked[:k]):
                idcg += 1 / np.log2(i + 2)
            ndcg = dcg / idcg if idcg > 0 else 0
            ndcg_scores.append(ndg)

        avg_ndcg = np.mean(ndcg_scores) if ndcg_scores else 0

        # Calculate Precision@K
        precision_at_k = {}
        for cutoff in [1, 5, 10, 20]:
            if cutoff <= k:
                precisions = []
                for ranked, relevant in zip(ranked_lists, relevant_items):
                    top_k = ranked[:cutoff]
                    relevant_in_top_k = sum(1 for item in top_k if item in relevant)
                    precision = relevant_in_top_k / cutoff
                    precisions.append(precision)
                precision_at_k[cutoff] = np.mean(precisions) if precisions else 0

        # Calculate MRR
        reciprocal_ranks = []
        for ranked, relevant in zip(ranked_lists, relevant_items):
            for i, item in enumerate(ranked):
                if item in relevant:
                    reciprocal_ranks.append(1 / (i + 1))
                    break
            else:
                reciprocal_ranks.append(0)

        mrr = np.mean(reciprocal_ranks) if reciprocal_ranks else 0

        # Calculate MAP
        average_precisions = []
        for ranked, relevant in zip(ranked_lists, relevant_items):
            if not relevant:
                average_precisions.append(0)
                continue
            relevant_count = 0
            precision_sum = 0
            for i, item in enumerate(ranked):
                if item in relevant:
                    relevant_count += 1
                    precision_sum += relevant_count / (i + 1)
            ap = precision_sum / len(relevant)
            average_precisions.append(ap)

        map_score = np.mean(average_precisions) if average_precisions else 0

        return RankingMetrics(
            ndcg=avg_ndcg,
            precision_at_k=precision_at_k,
            mean_reciprocal_rank=mrr,
            mean_average_precision=map_score,
        )
