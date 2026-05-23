from xgboost import XGBRanker

from app.ml.evaluation.ranking_metrics import ndcg_at_k


def evaluate_ranker(model: XGBRanker, features: list[list[float]], labels: list[float], k: int = 10) -> dict[str, float]:
    if not features:
        return {"ndcg_at_k": 0.0, "mean_prediction": 0.0}
    predictions = model.predict(features).tolist()
    ranked = sorted(zip(predictions, labels, strict=True), key=lambda item: item[0], reverse=True)
    gains = [label for _, label in ranked]
    return {
        "ndcg_at_k": round(ndcg_at_k(gains, k), 4),
        "mean_prediction": round(sum(predictions) / len(predictions), 4),
    }
