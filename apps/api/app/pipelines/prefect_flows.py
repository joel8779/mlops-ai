from datetime import timedelta

try:
    from prefect import flow, task
    from prefect.tasks import task_input_hash
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False

    def flow(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def task(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def task_input_hash(*args, **kwargs):
        return None


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


def _call_local(decorated_callable, *args, **kwargs):
    """Call a Prefect-decorated flow/task without requiring a Prefect API server."""
    fn = getattr(decorated_callable, "fn", decorated_callable)
    return fn(*args, **kwargs)


def run_resume_ingestion_local(batch_id: str) -> str:
    return _call_local(ingest_resume_batch, batch_id)


def run_embedding_refresh_local(scope: str = "all") -> str:
    return _call_local(refresh_embeddings, scope)


def run_nightly_candidate_ranking_local() -> str:
    run_embedding_refresh_local("active-candidates")
    return _call_local(rank_candidates_for_active_jobs)
