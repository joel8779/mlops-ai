"""Candidate similarity graph based on skills and latent vectors."""

from dataclasses import dataclass, field
from math import sqrt
from uuid import UUID


@dataclass(frozen=True)
class CandidateNode:
    candidate_id: UUID
    skills: set[str] = field(default_factory=set)
    embedding: tuple[float, ...] = ()


class CandidateSimilarityNetwork:
    def build_edges(self, candidates: list[CandidateNode], threshold: float = 0.35) -> dict[UUID, list[tuple[UUID, float]]]:
        edges: dict[UUID, list[tuple[UUID, float]]] = {candidate.candidate_id: [] for candidate in candidates}
        for index, left in enumerate(candidates):
            for right in candidates[index + 1 :]:
                score = self.similarity(left, right)
                if score >= threshold:
                    edges[left.candidate_id].append((right.candidate_id, score))
                    edges[right.candidate_id].append((left.candidate_id, score))
        return {key: sorted(value, key=lambda item: item[1], reverse=True) for key, value in edges.items()}

    def similarity(self, left: CandidateNode, right: CandidateNode) -> float:
        skill_score = self._jaccard(left.skills, right.skills)
        embedding_score = self._cosine(left.embedding, right.embedding)
        if left.embedding and right.embedding:
            return round((skill_score * 0.45) + (embedding_score * 0.55), 4)
        return round(skill_score, 4)

    @staticmethod
    def _jaccard(left: set[str], right: set[str]) -> float:
        return len(left & right) / len(left | right) if left or right else 0.0

    @staticmethod
    def _cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        numerator = sum(a * b for a, b in zip(left, right, strict=True))
        denominator = sqrt(sum(a * a for a in left)) * sqrt(sum(b * b for b in right))
        return numerator / denominator if denominator else 0.0
