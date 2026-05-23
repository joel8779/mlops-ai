from dataclasses import dataclass
from datetime import datetime, timezone
from math import exp


@dataclass(frozen=True)
class RankingFeatureVector:
    semantic_similarity: float
    skill_overlap: float
    title_similarity: float
    experience_alignment: float
    recruiter_engagement: float
    ats_score: float
    hiring_outcome_score: float
    recency_score: float
    embedding_distance: float
    keyword_density: float

    def as_list(self) -> list[float]:
        return [
            self.semantic_similarity,
            self.skill_overlap,
            self.title_similarity,
            self.experience_alignment,
            self.recruiter_engagement,
            self.ats_score,
            self.hiring_outcome_score,
            self.recency_score,
            self.embedding_distance,
            self.keyword_density,
        ]


FEATURE_NAMES = [
    "semantic_similarity",
    "skill_overlap",
    "title_similarity",
    "experience_alignment",
    "recruiter_engagement",
    "ats_score",
    "hiring_outcome_score",
    "recency_score",
    "embedding_distance",
    "keyword_density",
]


def normalized_overlap(left: list[str], right: list[str]) -> float:
    left_set = {item.lower() for item in left}
    right_set = {item.lower() for item in right}
    if not left_set and not right_set:
        return 1.0
    return len(left_set & right_set) / max(len(left_set | right_set), 1)


def recency_score(created_at: datetime | None) -> float:
    if created_at is None:
        return 0.5
    age_days = max((datetime.now(timezone.utc) - created_at).days, 0)
    return exp(-age_days / 90)


def keyword_density(text: str, keywords: list[str]) -> float:
    if not text or not keywords:
        return 0.0
    lowered = text.lower()
    hits = sum(lowered.count(keyword.lower()) for keyword in keywords)
    return min(1.0, hits / max(len(text.split()), 1) * 20)
