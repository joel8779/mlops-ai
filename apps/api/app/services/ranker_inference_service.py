from pathlib import Path

import joblib

from app.core.logging import get_logger

logger = get_logger(__name__)


class RankerInferenceService:
    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path
        self._bundle = None
        if model_path and model_path.exists():
            self._bundle = joblib.load(model_path)

    @property
    def version(self) -> str:
        if self._bundle:
            return str(self._bundle.get("version", "unknown"))
        return "hybrid-fallback"

    def score(self, feature_rows: list[list[float]], fallback_scores: list[float]) -> list[float]:
        if not feature_rows:
            return []
        if not self._bundle:
            return fallback_scores
        try:
            predictions = self._bundle["model"].predict(feature_rows).tolist()
        except Exception:
            logger.exception("ranker_inference_failed")
            return fallback_scores
        min_score = min(predictions)
        max_score = max(predictions)
        span = max(max_score - min_score, 1e-9)
        return [round((score - min_score) / span * 100, 2) for score in predictions]
