from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import UUID, uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, FieldCondition, Filter, MatchAny, MatchValue, PointIdsList, PointStruct, VectorParams

from app.core.config import settings
from app.core.ml_capabilities import ml_capabilities
from app.core.paths import get_repo_root_cached
from app.observability.metrics import (
    EMBEDDING_GENERATION_DURATION_MS,
    EMBEDDING_LATENCY,
    ML_INFERENCE_FAILURES_TOTAL,
    ML_INFERENCE_LATENCY_MS,
    elapsed_ms,
)
from app.observability.tracing import get_tracer

tracer = get_tracer(__name__)
REPO_ROOT = get_repo_root_cached()


class EmbeddingRuntimeError(RuntimeError):
    """Structured embedding failure that callers can degrade around."""

    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


@dataclass(frozen=True)
class TextChunk:
    index: int
    text: str


class EmbeddingService:
    _model: Any | None = None
    _model_error: Exception | None = None
    _executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="embedding-runtime")

    def __init__(self) -> None:
        self.client = QdrantClient(
            url=str(settings.qdrant_url),
            api_key=settings.qdrant_api_key,
            timeout=settings.qdrant_timeout_seconds,
        )

    @classmethod
    def _cache_folder(cls) -> str:
        cache_path = Path(settings.embedding_model_cache_dir)
        if not cache_path.is_absolute():
            cache_path = REPO_ROOT / cache_path
        cache_path.mkdir(parents=True, exist_ok=True)
        return str(cache_path)

    @classmethod
    def _load_model(cls) -> Any:
        if cls._model is not None:
            return cls._model
        if cls._model_error is not None:
            raise EmbeddingRuntimeError(
                "embedding_model_unavailable",
                "Embedding model is unavailable from a previous load attempt.",
                details={"error": str(cls._model_error)},
            ) from cls._model_error

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            ml_capabilities.warn_if_unavailable("sentence_transformers", "Embedding Service")
            cls._model_error = exc
            raise EmbeddingRuntimeError(
                "embedding_dependency_missing",
                "sentence-transformers is not installed. Install apps/api/requirements-embeddings.txt.",
                details={"dependency": "sentence-transformers"},
            ) from exc

        try:
            cls._model = SentenceTransformer(
                settings.embedding_model_name,
                device="cpu",
                cache_folder=cls._cache_folder(),
                local_files_only=settings.embedding_local_files_only,
            )
            return cls._model
        except Exception as exc:
            cls._model_error = exc
            raise EmbeddingRuntimeError(
                "embedding_model_load_failed",
                "Embedding model failed to load.",
                details={"model": settings.embedding_model_name, "error": str(exc)},
            ) from exc

    @classmethod
    def model_available(cls) -> bool:
        try:
            cls._load_model()
            return True
        except EmbeddingRuntimeError:
            return False

    def ensure_collection(self) -> None:
        existing = [collection.name for collection in self.client.get_collections().collections]
        for collection in [settings.qdrant_collection, settings.qdrant_job_collection]:
            if collection in existing:
                continue
            self.client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=settings.embedding_vector_size, distance=Distance.COSINE),
            )

    def chunk_text(self, text: str, max_words: int = 180, overlap: int = 40) -> list[TextChunk]:
        words = text.split()
        chunks: list[TextChunk] = []
        step = max_words - overlap
        for start in range(0, len(words), step):
            chunk = " ".join(words[start : start + max_words])
            if chunk:
                chunks.append(TextChunk(index=len(chunks), text=chunk))
        return chunks

    def embed(self, chunks: list[TextChunk]) -> list[list[float]]:
        if not chunks:
            return []
        start_time = perf_counter()
        try:
            with tracer.start_as_current_span("embedding.generate") as span:
                span.set_attribute("embedding.model", settings.embedding_model_name)
                span.set_attribute("embedding.chunk_count", len(chunks))
                model = self._load_model()
                future = self._executor.submit(
                    model.encode,
                    [chunk.text for chunk in chunks],
                    batch_size=settings.embedding_batch_size,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )
                vectors = future.result(timeout=settings.embedding_inference_timeout_seconds)
            duration_ms = elapsed_ms(start_time)
            EMBEDDING_LATENCY.labels(settings.embedding_model_name).observe(duration_ms / 1000)
            EMBEDDING_GENERATION_DURATION_MS.labels(settings.embedding_model_name, "success").observe(duration_ms)
            ML_INFERENCE_LATENCY_MS.labels(
                settings.embedding_model_name,
                "embedding_generation",
                "success",
            ).observe(duration_ms)
            return [vector.tolist() for vector in vectors]
        except FuturesTimeoutError as exc:
            duration_ms = elapsed_ms(start_time)
            EMBEDDING_GENERATION_DURATION_MS.labels(settings.embedding_model_name, "timeout").observe(duration_ms)
            ML_INFERENCE_FAILURES_TOTAL.labels(
                settings.embedding_model_name,
                "embedding_generation",
                "timeout",
            ).inc()
            raise EmbeddingRuntimeError(
                "embedding_timeout",
                "Embedding generation timed out.",
                details={"timeout_seconds": settings.embedding_inference_timeout_seconds},
            ) from exc
        except Exception as exc:
            duration_ms = elapsed_ms(start_time)
            EMBEDDING_GENERATION_DURATION_MS.labels(settings.embedding_model_name, "error").observe(duration_ms)
            ML_INFERENCE_LATENCY_MS.labels(
                settings.embedding_model_name,
                "embedding_generation",
                "error",
            ).observe(duration_ms)
            ML_INFERENCE_FAILURES_TOTAL.labels(
                settings.embedding_model_name,
                "embedding_generation",
                type(exc).__name__,
            ).inc()
            if isinstance(exc, EmbeddingRuntimeError):
                raise
            raise EmbeddingRuntimeError(
                "embedding_generation_failed",
                "Embedding generation failed.",
                details={"error": str(exc)},
            ) from exc

    def upsert_candidate_resume(
        self,
        organization_id: UUID,
        candidate_id: UUID,
        resume_id: UUID,
        chunks: list[TextChunk],
        vectors: list[list[float]],
        metadata: dict | None = None,
    ) -> list[str]:
        metadata = metadata or {}
        point_ids = [str(uuid4()) for _ in chunks]
        points = [
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "organization_id": str(organization_id),
                    "candidate_id": str(candidate_id),
                    "resume_id": str(resume_id),
                    "chunk_index": chunk.index,
                    "text": chunk.text,
                    "model": settings.embedding_model_name,
                    **metadata,
                },
            )
            for point_id, chunk, vector in zip(point_ids, chunks, vectors, strict=True)
        ]
        if points:
            self.ensure_collection()
            self.client.upsert(collection_name=settings.qdrant_collection, points=points)
        return point_ids

    def upsert_job_description(
        self,
        organization_id: UUID,
        job_description_id: UUID,
        chunks: list[TextChunk],
        vectors: list[list[float]],
    ) -> list[str]:
        point_ids = [str(uuid4()) for _ in chunks]
        points = [
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "organization_id": str(organization_id),
                    "job_description_id": str(job_description_id),
                    "job_id": str(job_description_id),
                    "chunk_index": chunk.index,
                    "text": chunk.text,
                    "model": settings.embedding_model_name,
                },
            )
            for point_id, chunk, vector in zip(point_ids, chunks, vectors, strict=True)
        ]
        if points:
            self.ensure_collection()
            self.client.upsert(collection_name=settings.qdrant_job_collection, points=points)
        return point_ids

    def semantic_search(self, organization_id: UUID, query: str, limit: int = 10) -> list[dict]:
        start_time = perf_counter()
        vector = self.embed([TextChunk(index=0, text=query)])[0]
        EMBEDDING_GENERATION_DURATION_MS.labels(settings.embedding_model_name, "success").observe(
            elapsed_ms(start_time)
        )
        results = self.client.search(
            collection_name=settings.qdrant_collection,
            query_vector=vector,
            query_filter=Filter(
                must=[FieldCondition(key="organization_id", match=MatchValue(value=str(organization_id)))]
            ),
            limit=limit,
        )
        return [{"score": hit.score, "payload": hit.payload} for hit in results]

    def candidate_search(
        self,
        organization_id: UUID,
        query: str,
        limit: int,
        skills: list[str] | None = None,
    ) -> list[dict]:
        start_time = perf_counter()
        vector = self.embed([TextChunk(index=0, text=query)])[0]
        EMBEDDING_GENERATION_DURATION_MS.labels(settings.embedding_model_name, "success").observe(
            elapsed_ms(start_time)
        )
        conditions = [FieldCondition(key="organization_id", match=MatchValue(value=str(organization_id)))]
        if skills:
            conditions.append(FieldCondition(key="skills", match=MatchAny(any=skills)))
        results = self.client.search(
            collection_name=settings.qdrant_collection,
            query_vector=vector,
            query_filter=Filter(must=conditions),
            limit=limit,
        )
        return [{"score": float(hit.score), "payload": hit.payload or {}} for hit in results]

    def delete_candidate_points(self, point_ids: list[str]) -> None:
        if point_ids:
            self.client.delete(
                collection_name=settings.qdrant_collection,
                points_selector=PointIdsList(points=point_ids),
                wait=True,
            )

    def delete_job_points(self, point_ids: list[str]) -> None:
        if point_ids:
            self.client.delete(
                collection_name=settings.qdrant_job_collection,
                points_selector=PointIdsList(points=point_ids),
                wait=True,
            )
