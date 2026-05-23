from typing import Any

import mlflow

from app.core.config import settings


def configure_mlflow(experiment_name: str) -> None:
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)


def log_embedding_experiment(metrics: dict[str, float], params: dict[str, Any]) -> str:
    configure_mlflow("embedding-quality")
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        return run.info.run_id


def log_ranking_experiment(metrics: dict[str, float], params: dict[str, Any]) -> str:
    configure_mlflow("candidate-ranking")
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        return run.info.run_id
