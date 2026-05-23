"""Startup-grade candidate recommendation service."""

from collections import defaultdict
from time import perf_counter
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.knowledge_graph.taxonomy.taxonomy_service import TaxonomyService
from app.ml.recommendation import CandidateNode, CandidateSimilarityNetwork
from app.models.domain import Candidate, CandidateSkill, RankingFeedback
from app.observability.metrics import (
    ML_INFERENCE_FAILURES_TOTAL,
    ML_INFERENCE_LATENCY_MS,
    RECOMMENDATION_GENERATION_TIME_MS,
    RECOMMENDATION_RESULTS,
    elapsed_ms,
)
from app.observability.tracing import get_tracer
from app.schemas.auth import AuthContext
from app.schemas.recommendation import RecommendationItem, RecommendationRequest, RecommendationResponse


tracer = get_tracer(__name__)


class RecommendationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.taxonomy = TaxonomyService()
        self.network = CandidateSimilarityNetwork()

    async def recommend(self, auth: AuthContext, payload: RecommendationRequest) -> RecommendationResponse:
        strategy = "skill_graph_personalized"
        start_time = perf_counter()
        try:
            with tracer.start_as_current_span("recommendation.generate") as span:
                span.set_attribute("recommendation.strategy", strategy)
                span.set_attribute("recommendation.limit", payload.limit)
                span.set_attribute("organization.id", str(auth.organization_id))

                candidates = await self._load_candidates(auth.organization_id, payload.limit * 5)
                skills_by_candidate = await self._load_skills(auth.organization_id)
                preferred_skills = (
                    set(self.taxonomy.skills.expand(payload.skills))
                    if payload.skills
                    else await self._recruiter_skills(auth)
                )
                nodes = [
                    CandidateNode(
                        candidate_id=candidate.id,
                        skills={skill.lower() for skill in skills_by_candidate.get(candidate.id, [])},
                    )
                    for candidate in candidates
                ]
                graph = self.network.build_edges(nodes, threshold=0.2)
                seed_ids = set(payload.candidate_ids)
                recommendations: list[RecommendationItem] = []
                for candidate in candidates:
                    candidate_skills = {skill.lower() for skill in skills_by_candidate.get(candidate.id, [])}
                    skill_overlap = len(candidate_skills & preferred_skills) / max(1, len(preferred_skills))
                    graph_boost = sum(score for neighbor, score in graph.get(candidate.id, []) if neighbor in seed_ids)
                    profile_boost = 0.1 if candidate.source and candidate.source.lower() in {"referral", "linkedin"} else 0.0
                    score = round((0.7 * skill_overlap) + (0.2 * graph_boost) + profile_boost, 4)
                    if score <= 0:
                        continue
                    reasons = self._reasons(candidate_skills, preferred_skills, graph_boost)
                    recommendations.append(RecommendationItem(candidate_id=candidate.id, score=score, reasons=reasons))
                recommendations.sort(key=lambda item: item.score, reverse=True)
                result = RecommendationResponse(
                    recommendations=recommendations[: payload.limit],
                    diagnostics={"candidate_pool": len(candidates), "preferred_skill_count": len(preferred_skills)},
                )
                span.set_attribute("recommendation.result_count", len(result.recommendations))
        except Exception as exc:
            duration_ms = elapsed_ms(start_time)
            RECOMMENDATION_GENERATION_TIME_MS.labels(strategy, "error").observe(duration_ms)
            ML_INFERENCE_LATENCY_MS.labels("recommendation_engine", strategy, "error").observe(duration_ms)
            ML_INFERENCE_FAILURES_TOTAL.labels("recommendation_engine", strategy, type(exc).__name__).inc()
            raise

        duration_ms = elapsed_ms(start_time)
        RECOMMENDATION_GENERATION_TIME_MS.labels(strategy, "success").observe(duration_ms)
        RECOMMENDATION_RESULTS.labels(strategy).observe(len(result.recommendations))
        ML_INFERENCE_LATENCY_MS.labels("recommendation_engine", strategy, "success").observe(duration_ms)
        return result

    async def _load_candidates(self, organization_id: UUID, limit: int) -> list[Candidate]:
        result = await self.db.scalars(
            select(Candidate)
            .where(Candidate.organization_id == organization_id, Candidate.deleted_at.is_(None))
            .order_by(Candidate.created_at.desc())
            .limit(limit)
        )
        return list(result.all())

    async def _load_skills(self, organization_id: UUID) -> dict[UUID, list[str]]:
        result = await self.db.execute(
            select(CandidateSkill.candidate_id, CandidateSkill.normalized_skill).where(
                CandidateSkill.organization_id == organization_id
            )
        )
        skills: dict[UUID, list[str]] = defaultdict(list)
        for candidate_id, skill in result.all():
            skills[candidate_id].append(skill)
        return skills

    async def _recruiter_skills(self, auth: AuthContext) -> set[str]:
        result = await self.db.scalars(
            select(RankingFeedback).where(
                RankingFeedback.organization_id == auth.organization_id,
                RankingFeedback.user_id == auth.user_id,
            )
        )
        skills: set[str] = set()
        for feedback in result.all():
            snapshot = feedback.feature_snapshot or {}
            skills.update(str(skill).lower() for skill in snapshot.get("matched_skills", []))
        return set(self.taxonomy.skills.expand(list(skills))) if skills else {"python", "typescript", "kubernetes", "mlops"}

    @staticmethod
    def _reasons(candidate_skills: set[str], preferred_skills: set[str], graph_boost: float) -> list[str]:
        reasons = [f"Matches {skill}" for skill in sorted(candidate_skills & preferred_skills)[:4]]
        if graph_boost:
            reasons.append("Similar to recruiter-selected candidates")
        return reasons or ["Relevant latent skill profile"]
