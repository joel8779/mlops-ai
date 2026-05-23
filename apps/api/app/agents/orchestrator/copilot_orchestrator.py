"""Hiring Copilot 2.0 orchestration facade."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.execution.workflow_executor import AutonomousWorkflowExecutor, WorkflowExecutionResult
from app.agents.memory.long_term_memory import LongTermRecruiterMemory
from app.agents.planning.autonomous_planner import AutonomousHiringPlanner
from app.agents.reasoning.intent import RecruiterIntentClassifier


class HiringCopilotOrchestrator:
    def __init__(self, db: AsyncSession) -> None:
        self.intent_classifier = RecruiterIntentClassifier()
        self.planner = AutonomousHiringPlanner()
        self.executor = AutonomousWorkflowExecutor(db)
        self.memory = LongTermRecruiterMemory(db)

    async def run(
        self,
        organization_id: UUID,
        recruiter_id: UUID,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> WorkflowExecutionResult:
        context = context or {}
        prior_preferences = await self.memory.load_preferences(organization_id, recruiter_id)
        context = {**context, "memory_preferences": [fact.__dict__ for fact in prior_preferences[:10]]}
        intent = self.intent_classifier.classify(query, context)
        plan = self.planner.build_plan(query, intent, context)
        result = await self.executor.execute(organization_id, recruiter_id, plan, query, context)
        await self.memory.remember_preference(
            organization_id=organization_id,
            recruiter_id=recruiter_id,
            key=f"intent:{intent.primary.value}",
            value={"last_query": query, "confidence": intent.confidence},
            confidence=intent.confidence,
        )
        return result
