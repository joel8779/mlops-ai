from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta


@task(retries=3, retry_delay_seconds=30, cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
def ingest_resume_batch(batch_id: str) -> str:
    return f"resume-batch-ingested:{batch_id}"


@task(retries=3, retry_delay_seconds=30)
def refresh_embeddings(scope: str) -> str:
    return f"embeddings-refreshed:{scope}"


@task(retries=2, retry_delay_seconds=60)
def rank_candidates_for_active_jobs() -> str:
    return "nightly-ranking-complete"


@task(retries=2, retry_delay_seconds=60)
def monitor_embedding_drift() -> str:
    return "drift-monitoring-complete"


@task(retries=1, retry_delay_seconds=120)
def retrain_reranker() -> str:
    return "reranker-training-complete"


@flow(name="resume-ingestion")
def resume_ingestion_flow(batch_id: str) -> str:
    return ingest_resume_batch(batch_id)


@flow(name="embedding-refresh")
def embedding_refresh_flow(scope: str = "all") -> str:
    return refresh_embeddings(scope)


@flow(name="nightly-candidate-ranking")
def nightly_candidate_ranking_flow() -> str:
    refresh_embeddings("active-candidates")
    return rank_candidates_for_active_jobs()


@flow(name="drift-monitoring")
def drift_monitoring_flow() -> str:
    return monitor_embedding_drift()


@flow(name="retraining")
def retraining_flow() -> str:
    monitor_embedding_drift()
    return retrain_reranker()
