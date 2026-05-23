from pathlib import Path

import joblib
import mlflow
from xgboost import XGBRanker

from app.core.config import settings
from app.ml.training.ranking.dataset_builder import RankingDataset


def train_xgboost_ranker(dataset: RankingDataset, model_dir: Path) -> Path:
    if not dataset.features:
        raise ValueError("Cannot train ranker without feature rows")
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment("learning-to-rank")
    ranker = XGBRanker(
        objective="rank:pairwise",
        n_estimators=120,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
    )
    with mlflow.start_run() as run:
        ranker.fit(dataset.features, dataset.labels, group=dataset.groups)
        mlflow.log_params({"objective": "rank:pairwise", "features": ",".join(dataset.feature_names)})
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / f"xgb-ranker-{run.info.run_id}.joblib"
        joblib.dump({"model": ranker, "feature_names": dataset.feature_names, "version": run.info.run_id}, model_path)
        mlflow.log_artifact(str(model_path))
        mlflow.xgboost.log_model(ranker, artifact_path="model", registered_model_name="candidate-ranker")
        return model_path
