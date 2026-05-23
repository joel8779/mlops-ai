from app.observability.metrics import RANKING_MODEL_DRIFT_SCORE


class DriftMonitor:
    def set_drift_score(self, model_version: str, score: float) -> None:
        RANKING_MODEL_DRIFT_SCORE.labels(model_version).set(score)
