"""Planner/executor task decomposition for Hiring Copilot 2.0."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.agents.reasoning.intent import HiringIntent, RecruiterIntent


class WorkflowStepType(StrEnum):
    RETRIEVE_CONTEXT = "retrieve_context"
    SOURCE_CANDIDATES = "source_candidates"
    SCORE_AND_RERANK = "score_and_rerank"
    ANALYZE_RISK = "analyze_risk"
    PREDICT_INTERVIEW = "predict_interview"
    GENERATE_STRATEGY = "generate_strategy"
    PERSONALIZE = "personalize"


@dataclass(frozen=True)
class WorkflowStep:
    step_type: WorkflowStepType
    description: str
    inputs: dict[str, Any] = field(default_factory=dict)
    required: bool = True


@dataclass(frozen=True)
class AutonomousHiringPlan:
    objective: str
    intent: HiringIntent
    steps: list[WorkflowStep]
    confidence: float


class AutonomousHiringPlanner:
    def build_plan(self, query: str, intent: RecruiterIntent, context: dict[str, Any]) -> AutonomousHiringPlan:
        steps = [
            WorkflowStep(
                WorkflowStepType.RETRIEVE_CONTEXT,
                "Load session memory, recruiter preferences, and hiring context.",
                {"query": query, **context},
            )
        ]
        if intent.primary in {HiringIntent.SOURCE, HiringIntent.RANK, HiringIntent.GENERAL}:
            steps.extend(
                [
                    WorkflowStep(WorkflowStepType.SOURCE_CANDIDATES, "Find matching candidates.", context),
                    WorkflowStep(WorkflowStepType.SCORE_AND_RERANK, "Personalize ranking using recruiter preference signals.", context),
                ]
            )
        if intent.primary in {HiringIntent.RISK, HiringIntent.RANK, HiringIntent.INTERVIEW, HiringIntent.GENERAL}:
            steps.extend(
                [
                    WorkflowStep(WorkflowStepType.ANALYZE_RISK, "Assess candidate and pipeline risk.", context, required=False),
                    WorkflowStep(WorkflowStepType.PREDICT_INTERVIEW, "Estimate interview success likelihood.", context, required=False),
                ]
            )
        if intent.primary in {HiringIntent.STRATEGY, HiringIntent.SOURCE, HiringIntent.GENERAL}:
            steps.append(WorkflowStep(WorkflowStepType.GENERATE_STRATEGY, "Generate hiring strategy recommendations.", context))
        steps.append(WorkflowStep(WorkflowStepType.PERSONALIZE, "Adapt recommendations to recruiter preferences.", context))
        return AutonomousHiringPlan(
            objective=query,
            intent=intent.primary,
            steps=steps,
            confidence=intent.confidence,
        )
