"""Collaborative filtering over recruiter-candidate feedback."""

from collections import defaultdict
from dataclasses import dataclass
from math import sqrt
from uuid import UUID


@dataclass(frozen=True)
class Interaction:
    recruiter_id: UUID
    candidate_id: UUID
    weight: float


class CollaborativeFilteringRecommender:
    def recommend(self, interactions: list[Interaction], recruiter_id: UUID, limit: int = 10) -> list[tuple[UUID, float]]:
        by_recruiter: dict[UUID, dict[UUID, float]] = defaultdict(dict)
        for item in interactions:
            by_recruiter[item.recruiter_id][item.candidate_id] = item.weight
        target = by_recruiter.get(recruiter_id, {})
        scores: dict[UUID, float] = defaultdict(float)
        for other_id, other in by_recruiter.items():
            if other_id == recruiter_id:
                continue
            similarity = self._cosine(target, other)
            if similarity <= 0:
                continue
            for candidate_id, weight in other.items():
                if candidate_id not in target:
                    scores[candidate_id] += similarity * weight
        return sorted(scores.items(), key=lambda item: item[1], reverse=True)[:limit]

    @staticmethod
    def _cosine(left: dict[UUID, float], right: dict[UUID, float]) -> float:
        shared = set(left).intersection(right)
        numerator = sum(left[key] * right[key] for key in shared)
        left_norm = sqrt(sum(value * value for value in left.values()))
        right_norm = sqrt(sum(value * value for value in right.values()))
        return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0
