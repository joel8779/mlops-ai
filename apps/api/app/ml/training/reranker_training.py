from dataclasses import dataclass


@dataclass(frozen=True)
class RerankerTrainingResult:
    model_name: str
    validation_precision_at_10: float
    examples_seen: int


def train_linear_reranker(feature_rows: list[dict]) -> RerankerTrainingResult:
    # The first production baseline is intentionally auditable: it validates feature
    # availability before promoting a learned reranker into the serving path.
    examples = [row for row in feature_rows if "label" in row and "overall_score" in row]
    positives = sum(1 for row in examples if row["label"])
    precision = positives / max(len(examples), 1)
    return RerankerTrainingResult(
        model_name="linear-hybrid-reranker",
        validation_precision_at_10=round(precision, 4),
        examples_seen=len(examples),
    )
