from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import CandidateMatch, RankingFeedback
from app.ml.training.ranking.feature_pipeline import RankingFeatureVector


@dataclass(frozen=True)
class RankingDataset:
    features: list[list[float]]
    labels: list[float]
    groups: list[int]
    feature_names: list[str]


class RankingDatasetBuilder:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def build_for_organization(self, organization_id: UUID) -> RankingDataset:
        rows = await self.db.execute(
            select(CandidateMatch, RankingFeedback)
            .join(
                RankingFeedback,
                (RankingFeedback.candidate_id == CandidateMatch.candidate_id)
                & (RankingFeedback.job_description_id == CandidateMatch.job_description_id),
                isouter=True,
            )
            .where(CandidateMatch.organization_id == organization_id)
            .order_by(CandidateMatch.job_description_id)
        )
        features: list[list[float]] = []
        labels: list[float] = []
        group_counts: dict[str, int] = {}
        for match, feedback in rows.all():
            vector = RankingFeatureVector(
                semantic_similarity=float(match.semantic_score) / 100,
                skill_overlap=float(match.skill_match) / 100,
                title_similarity=0.5,
                experience_alignment=float(match.experience_match) / 100,
                recruiter_engagement=float(feedback.reward) / 5 if feedback else 0.0,
                ats_score=0.75,
                hiring_outcome_score=float(feedback.reward) / 5 if feedback else 0.0,
                recency_score=1.0,
                embedding_distance=1 - (float(match.semantic_score) / 100),
                keyword_density=float(match.keyword_score) / 100,
            )
            features.append(vector.as_list())
            labels.append(float(feedback.reward) if feedback else 0.0)
            group_counts[str(match.job_description_id)] = group_counts.get(str(match.job_description_id), 0) + 1
        return RankingDataset(
            features=features,
            labels=labels,
            groups=list(group_counts.values()),
            feature_names=[
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
            ],
        )
