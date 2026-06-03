"""Embedding Deduplicator - Detect and deduplicate similar embeddings."""

import numpy as np
from uuid import UUID


class EmbeddingDeduplicator:
    """Deduplicate similar embeddings to reduce storage and computation."""

    def __init__(
        self,
        similarity_threshold: float = 0.95,
    ) -> None:
        """Initialize embedding deduplicator.

        Args:
            similarity_threshold: Cosine similarity threshold for deduplication
        """
        self.similarity_threshold = similarity_threshold

    def cosine_similarity(self, emb1: list[float], emb2: list[float]) -> float:
        """Calculate cosine similarity between two embeddings.

        Args:
            emb1: First embedding
            emb2: Second embedding

        Returns:
            Cosine similarity score
        """
        vec1 = np.array(emb1)
        vec2 = np.array(emb2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def is_duplicate(
        self,
        embedding: list[float],
        existing_embeddings: list[list[float]],
    ) -> bool:
        """Check if an embedding is a duplicate of existing ones.

        Args:
            embedding: Embedding to check
            existing_embeddings: List of existing embeddings

        Returns:
            True if duplicate, False otherwise
        """
        for existing in existing_embeddings:
            similarity = self.cosine_similarity(embedding, existing)
            if similarity >= self.similarity_threshold:
                return True

        return False

    def find_duplicates(
        self,
        embeddings: dict[UUID, list[float]],
    ) -> dict[UUID, list[UUID]]:
        """Find duplicate embeddings in a collection.

        Args:
            embeddings: Dictionary mapping IDs to embeddings

        Returns:
            Dictionary mapping IDs to list of duplicate IDs
        """
        duplicates = {}
        ids = list(embeddings.keys())

        for i, id1 in enumerate(ids):
            duplicate_ids = []
            for id2 in ids[i + 1:]:
                similarity = self.cosine_similarity(embeddings[id1], embeddings[id2])
                if similarity >= self.similarity_threshold:
                    duplicate_ids.append(id2)

            if duplicate_ids:
                duplicates[id1] = duplicate_ids

        return duplicates

    def deduplicate(
        self,
        embeddings: dict[UUID, list[float]],
    ) -> dict[UUID, list[float]]:
        """Remove duplicate embeddings from a collection.

        Args:
            embeddings: Dictionary mapping IDs to embeddings

        Returns:
            Deduplicated dictionary
        """
        duplicates = self.find_duplicates(embeddings)

        # Keep only the first occurrence of each duplicate group
        seen = set()
        deduplicated = {}

        for id1, dup_ids in duplicates.items():
            if id1 not in seen:
                deduplicated[id1] = embeddings[id1]
                seen.add(id1)
                for id2 in dup_ids:
                    seen.add(id2)

        # Add non-duplicate embeddings
        for id1, emb in embeddings.items():
            if id1 not in seen:
                deduplicated[id1] = emb

        return deduplicated

    def cluster_embeddings(
        self,
        embeddings: dict[UUID, list[float]],
        cluster_threshold: float = 0.9,
    ) -> dict[int, list[UUID]]:
        """Cluster similar embeddings.

        Args:
            embeddings: Dictionary mapping IDs to embeddings
            cluster_threshold: Similarity threshold for clustering

        Returns:
            Dictionary mapping cluster IDs to list of embedding IDs
        """
        clusters = {}
        cluster_id = 0
        ids = list(embeddings.keys())
        assigned = set()

        for i, id1 in enumerate(ids):
            if id1 in assigned:
                continue

            # Start new cluster
            cluster = [id1]
            assigned.add(id1)

            # Find similar embeddings
            for id2 in ids[i + 1:]:
                if id2 in assigned:
                    continue

                similarity = self.cosine_similarity(embeddings[id1], embeddings[id2])
                if similarity >= cluster_threshold:
                    cluster.append(id2)
                    assigned.add(id2)

            clusters[cluster_id] = cluster
            cluster_id += 1

        return clusters
