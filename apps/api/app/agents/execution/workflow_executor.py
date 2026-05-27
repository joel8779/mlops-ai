"""Execution engine for autonomous hiring plans."""

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.personalization.preference_model import RecruiterPreferenceModel
from app.agents.planning.autonomous_planner import AutonomousHiringPlan, WorkflowStepType
from app.ml.recommendation.graph_engine import CandidateRecommendationGraph
from app.ml.recommendation.trajectory_predictor import CareerTrajectoryPredictor
from app.observability.metrics import AGENT_EXECUTION_FAILURES_TOTAL, AGENT_STEP_LATENCY_MS, elapsed_ms
from app.observability.tracing import get_tracer
from app.services.retrieval.hybrid_retriever import HybridRetriever


tracer = get_tracer(__name__)


@dataclass(frozen=True)
class WorkflowExecutionResult:
    answer: str
    artifacts: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0


class AutonomousWorkflowExecutor:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.preferences = RecruiterPreferenceModel(db)
        self.graph = CandidateRecommendationGraph()
        self.trajectory = CareerTrajectoryPredictor()

    async def execute(
        self,
        organization_id: UUID,
        recruiter_id: UUID,
        plan: AutonomousHiringPlan,
        query: str,
        context: dict[str, Any],
    ) -> WorkflowExecutionResult:
        artifacts: dict[str, Any] = {"plan": [step.step_type.value for step in plan.steps]}
        profile = await self.preferences.build_profile(organization_id, recruiter_id)
        artifacts["preference_profile"] = {
            "confidence": profile.confidence,
            "top_skills": sorted(profile.skill_weights.items(), key=lambda item: item[1], reverse=True)[:8],
        }

        with tracer.start_as_current_span("agent.autonomous_workflow") as span:
            span.set_attribute("organization.id", str(organization_id))
            span.set_attribute("recruiter.id", str(recruiter_id))
            span.set_attribute("agent.intent", plan.intent.value)
            span.set_attribute("agent.step_count", len(plan.steps))

            for step in plan.steps:
                await self._execute_step(
                    artifacts=artifacts,
                    step_type=step.step_type,
                    organization_id=organization_id,
                    recruiter_id=recruiter_id,
                    query=query,
                    context=context,
                    skill_weights=profile.skill_weights,
                )

        answer = self._compose_answer(plan, artifacts)
        return WorkflowExecutionResult(answer=answer, artifacts=artifacts, confidence=min(0.95, plan.confidence + 0.1))

    async def _execute_step(
        self,
        artifacts: dict[str, Any],
        step_type: WorkflowStepType,
        organization_id: UUID,
        recruiter_id: UUID,
        query: str,
        context: dict[str, Any],
        skill_weights: dict[str, float],
    ) -> None:
        step_name = step_type.value
        start_time = perf_counter()
        try:
            with tracer.start_as_current_span("agent.workflow_step") as span:
                span.set_attribute("agent.workflow_step", step_name)
                if step_type == WorkflowStepType.SOURCE_CANDIDATES:
                    retriever = HybridRetriever(self.db)
                    artifacts["candidates"] = await retriever.search(
                        query=query,
                        organization_id=organization_id,
                        owner_id=recruiter_id,
                        job_description_id=context.get("job_id") or context.get("job_description_id"),
                        limit=int(context.get("limit", 10)),
                    )
                elif step_type == WorkflowStepType.SCORE_AND_RERANK:
                    artifacts["ranking_guidance"] = self._ranking_guidance(skill_weights)
                elif step_type == WorkflowStepType.ANALYZE_RISK:
                    artifacts["risk_analysis"] = self._risk_analysis(context)
                elif step_type == WorkflowStepType.PREDICT_INTERVIEW:
                    artifacts["interview_prediction"] = self.trajectory.predict_interview_success(context)
                elif step_type == WorkflowStepType.GENERATE_STRATEGY:
                    artifacts["strategy"] = self._strategy(query, skill_weights)
        except Exception as exc:
            AGENT_STEP_LATENCY_MS.labels(step_name, "error").observe(elapsed_ms(start_time))
            AGENT_EXECUTION_FAILURES_TOTAL.labels(step_name, type(exc).__name__).inc()
            raise

        AGENT_STEP_LATENCY_MS.labels(step_name, "success").observe(elapsed_ms(start_time))

    @staticmethod
    def _ranking_guidance(skill_weights: dict[str, float]) -> list[str]:
        return [f"Boost candidates with {skill}" for skill, _ in sorted(skill_weights.items(), key=lambda item: item[1], reverse=True)[:5]]

    @staticmethod
    def _risk_analysis(context: dict[str, Any]) -> dict[str, Any]:
        gaps = context.get("missing_skills", [])
        risk_score = min(1.0, 0.15 + (0.1 * len(gaps)))
        return {"risk_score": round(risk_score, 3), "drivers": gaps[:5], "mitigation": "Use structured screening for high-impact gaps."}

    @staticmethod
    def _strategy(query: str, skill_weights: dict[str, float]) -> list[str]:
        top_skills = ", ".join(list(skill_weights)[:3]) or "role-critical skills"
        return [
            f"Anchor sourcing searches around {top_skills}.",
            "Separate must-have criteria from coachable gaps before outreach.",
            "Use recruiter feedback after every shortlist to update ranking preferences.",
        ]

    @staticmethod
    def _compose_answer(plan: AutonomousHiringPlan, artifacts: dict[str, Any]) -> str:
        strategy = artifacts.get("strategy", [])
        candidate_count = len(artifacts.get("candidates", []))
        return (
            f"Autonomous copilot plan executed for intent '{plan.intent.value}'. "
            f"Found {candidate_count} candidate signals and generated {len(strategy)} strategy recommendations."
        )
