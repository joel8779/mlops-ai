from dataclasses import dataclass
from time import perf_counter
from uuid import UUID, uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, FieldCondition, Filter, MatchAny, MatchValue, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.observability.metrics import (
    EMBEDDING_GENERATION_DURATION_MS,
    EMBEDDING_LATENCY,
    ML_INFERENCE_FAILURES_TOTAL,
    ML_INFERENCE_LATENCY_MS,
    elapsed_ms,
)
from app.observability.tracing import get_tracer


tracer = get_tracer(__name__)


@dataclass(frozen=True)
class TextChunk:
    index: int
    text: str


class EmbeddingService:
    def __init__(self) -> None:
        self.model = SentenceTransformer(settings.embedding_model_name)
        self.client = QdrantClient(url=str(settings.qdrant_url))
        self.ensure_collection()

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
                vectors = self.model.encode([chunk.text for chunk in chunks], normalize_embeddings=True)
            duration_ms = elapsed_ms(start_time)
            EMBEDDING_LATENCY.labels(settings.embedding_model_name).observe(duration_ms / 1000)
            EMBEDDING_GENERATION_DURATION_MS.labels(settings.embedding_model_name, "success").observe(duration_ms)
            ML_INFERENCE_LATENCY_MS.labels(
                settings.embedding_model_name,
                "embedding_generation",
                "success",
            ).observe(duration_ms)
            return [vector.tolist() for vector in vectors]
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
            raise

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
                    "chunk_index": chunk.index,
                    "text": chunk.text,
                    "model": settings.embedding_model_name,
                },
            )
            for point_id, chunk, vector in zip(point_ids, chunks, vectors, strict=True)
        ]
        if points:
            self.client.upsert(collection_name=settings.qdrant_job_collection, points=points)
        return point_ids

    def semantic_search(self, organization_id: UUID, query: str, limit: int = 10) -> list[dict]:
        start_time = perf_counter()
        vector = self.model.encode(query, normalize_embeddings=True).tolist()
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
        vector = self.model.encode(query, normalize_embeddings=True).tolist()
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
