"""Recruiter preference learning and lightweight embedding profiles."""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from math import sqrt
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import RankingFeedback, RecruiterActivity


@dataclass
class RecruiterPreferenceProfile:
    recruiter_id: UUID
    skill_weights: dict[str, float] = field(default_factory=dict)
    source_weights: dict[str, float] = field(default_factory=dict)
    behavior_embedding: list[float] = field(default_factory=list)
    confidence: float = 0.0


class RecruiterPreferenceModel:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def build_profile(self, organization_id: UUID, recruiter_id: UUID) -> RecruiterPreferenceProfile:
        feedback = await self.db.scalars(
            select(RankingFeedback).where(
                RankingFeedback.organization_id == organization_id,
                RankingFeedback.user_id == recruiter_id,
            )
        )
        activities = await self.db.scalars(
            select(RecruiterActivity).where(
                RecruiterActivity.organization_id == organization_id,
                RecruiterActivity.user_id == recruiter_id,
            )
        )

        skill_scores: dict[str, float] = defaultdict(float)
        source_scores: dict[str, float] = defaultdict(float)
        action_counts: Counter[str] = Counter()

        for item in feedback.all():
            reward = float(item.reward)
            snapshot = item.feature_snapshot or {}
            for skill in snapshot.get("matched_skills", []) + snapshot.get("skills", []):
                skill_scores[str(skill).lower()] += reward
            if source := snapshot.get("source"):
                source_scores[str(source).lower()] += reward
            action_counts[item.action.value] += 1

        for activity in activities.all():
            action_counts[activity.activity_type] += 1
            payload = activity.payload or {}
            for skill in payload.get("skills", []):
                skill_scores[str(skill).lower()] += 0.2

        embedding = self._behavior_embedding(skill_scores, source_scores, action_counts)
        confidence = min(1.0, (sum(action_counts.values()) + len(skill_scores)) / 30)
        return RecruiterPreferenceProfile(
            recruiter_id=recruiter_id,
            skill_weights=self._normalize(skill_scores),
            source_weights=self._normalize(source_scores),
            behavior_embedding=embedding,
            confidence=round(confidence, 3),
        )

    def score_candidate_payload(self, profile: RecruiterPreferenceProfile, payload: dict[str, Any]) -> float:
        skills = [str(skill).lower() for skill in payload.get("skills", [])]
        source = str(payload.get("source", "")).lower()
        skill_score = sum(profile.skill_weights.get(skill, 0.0) for skill in skills)
        source_score = profile.source_weights.get(source, 0.0)
        return round((skill_score * 0.8) + (source_score * 0.2), 4)

    @staticmethod
    def _normalize(values: dict[str, float]) -> dict[str, float]:
        total = sum(abs(value) for value in values.values()) or 1.0
        return {key: round(value / total, 4) for key, value in values.items()}

    def _behavior_embedding(
        self,
        skills: dict[str, float],
        sources: dict[str, float],
        actions: Counter[str],
        dimensions: int = 32,
    ) -> list[float]:
        vector = [0.0] * dimensions
        for namespace, values in (("skill", skills), ("source", sources), ("action", actions)):
            for key, value in values.items():
                vector[hash(f"{namespace}:{key}") % dimensions] += float(value)
        norm = sqrt(sum(value * value for value in vector)) or 1.0
        return [round(value / norm, 6) for value in vector]
