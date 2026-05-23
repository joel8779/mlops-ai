from dataclasses import dataclass
from uuid import UUID, uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, FieldCondition, Filter, MatchAny, MatchValue, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from app.core.config import settings


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
        vectors = self.model.encode([chunk.text for chunk in chunks], normalize_embeddings=True)
        return [vector.tolist() for vector in vectors]

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
        vector = self.model.encode(query, normalize_embeddings=True).tolist()
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
        vector = self.model.encode(query, normalize_embeddings=True).tolist()
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
