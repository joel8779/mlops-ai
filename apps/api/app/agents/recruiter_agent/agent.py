"""AI Recruiter Agent - Intelligent agent for recruiting workflows."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.recruiter_agent.memory import AgentMemory
from app.agents.recruiter_agent.planner import TaskPlanner
from app.agents.recruiter_agent.tools import ToolRegistry
from app.services.llm.providers import ModelRouter, ModelType
from app.services.llm.providers.gemini_provider import LLMResult


class AgentAction(str, Enum):
    """Types of agent actions."""

    SEARCH_CANDIDATES = "search_candidates"
    COMPARE_CANDIDATES = "compare_candidates"
    GENERATE_OUTREACH = "generate_outreach"
    SUGGEST_INTERVIEW = "suggest_interview"
    EXPLAIN_RANKING = "explain_ranking"
    ANALYZE_SKILLS = "analyze_skills"
    RECOMMEND_HIRING = "recommend_hiring"
    ANSWER_QUESTION = "answer_question"


@dataclass
class AgentThought:
    """Chain-of-thought reasoning step."""

    step: int
    thought: str
    action: Optional[AgentAction] = None
    action_input: Optional[dict[str, Any]] = None
    observation: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AgentResponse:
    """Final agent response."""

    answer: str
    thoughts: list[AgentThought]
    actions_taken: list[AgentAction]
    sources_used: list[str]
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


class RecruiterAgent:
    """AI Recruiter Agent with tool calling and chain-of-thought reasoning."""

    def __init__(
        self,
        db: AsyncSession,
        organization_id: UUID,
        user_id: UUID,
        model_router: Optional[ModelRouter] = None,
    ) -> None:
        """Initialize recruiter agent.

        Args:
            db: Database session
            organization_id: Organization ID
            user_id: User ID
            model_router: Optional model router
        """
        self.db = db
        self.organization_id = organization_id
        self.user_id = user_id
        self.model_router = model_router or ModelRouter()
        self.memory = AgentMemory(organization_id, user_id)
        self.planner = TaskPlanner()
        self.tool_registry = ToolRegistry(db, organization_id, user_id)
        self.session_id = uuid4()

    async def process_query(
        self,
        query: str,
        context: Optional[dict[str, Any]] = None,
        enable_cot: bool = True,
    ) -> AgentResponse:
        """Process a recruiter query with chain-of-thought reasoning.

        Args:
            query: Recruiter's question or request
            context: Additional context (job_id, candidate_ids, etc.)
            enable_cot: Whether to use chain-of-thought reasoning

        Returns:
            AgentResponse with answer and reasoning
        """
        context = context or {}

        # Store query in memory
        await self.memory.add_message("user", query, context)

        # Plan the task
        task_plan = await self.planner.plan_task(query, context)

        thoughts: list[AgentThought] = []
        actions_taken: list[AgentAction] = []
        sources_used: list[str] = []

        # Chain-of-thought reasoning
        if enable_cot:
            thought = AgentThought(
                step=1,
                thought=f"Understanding query: {query}",
            )
            thoughts.append(thought)

            thought = AgentThought(
                step=2,
                thought=f"Task type: {task_plan.task_type.value}",
                action=task_plan.suggested_action,
            )
            thoughts.append(thought)

        # Execute actions based on task plan
        observations = []
        for action in task_plan.actions:
            try:
                observation = await self._execute_action(action, context)
                observations.append(observation)

                if enable_cot:
                    thought = AgentThought(
                        step=len(thoughts) + 1,
                        thought=f"Executing {action.action_type.value}",
                        action=action.action_type,
                        action_input=action.parameters,
                        observation=observation[:500] if observation else "",
                    )
                    thoughts.append(thought)

                actions_taken.append(action.action_type)

                # Track sources
                if action.action_type in [AgentAction.SEARCH_CANDIDATES, AgentAction.COMPARE_CANDIDATES]:
                    sources_used.extend(action.parameters.get("candidate_ids", []))

            except Exception as e:
                if enable_cot:
                    thought = AgentThought(
                        step=len(thoughts) + 1,
                        thought=f"Error executing {action.action_type.value}: {str(e)}",
                    )
                    thoughts.append(thought)

        # Generate final response
        provider, _ = self.model_router.get_provider_for_task(
            ModelType.REASONING,
            api_key=None,  # Uses default from settings
        )

        system_prompt = self._build_system_prompt(observations, context)
        user_prompt = self._build_user_prompt(query, observations, context)

        result = await provider.complete(user_prompt, system_prompt)

        # Store response in memory
        await self.memory.add_message("assistant", result.text, {"actions": actions_taken})

        return AgentResponse(
            answer=result.text,
            thoughts=thoughts,
            actions_taken=actions_taken,
            sources_used=sources_used,
            confidence=self._calculate_confidence(result, observations),
            metadata={
                "model": result.model,
                "tokens_used": result.total_tokens,
                "cost_usd": result.estimated_cost_usd,
                "latency_ms": result.latency_ms,
            },
        )

    async def _execute_action(
        self,
        action: Any,
        context: dict[str, Any],
    ) -> str:
        """Execute a single action using tool registry.

        Args:
            action: Action to execute
            context: Execution context

        Returns:
            Observation/result string
        """
        tool = self.tool_registry.get_tool(action.action_type)
        if not tool:
            return f"Tool not found for action: {action.action_type}"

        result = await tool.execute(action.parameters, context)
        return str(result)

    def _build_system_prompt(self, observations: list[str], context: dict[str, Any]) -> str:
        """Build system prompt with observations.

        Args:
            observations: List of action observations
            context: Context information

        Returns:
            System prompt string
        """
        base_prompt = """You are an expert AI recruiter assistant with access to candidate data, job descriptions, and hiring analytics.

Your role is to help recruiters make data-driven decisions by:
- Searching and analyzing candidates
- Comparing candidates objectively
- Generating outreach and interview materials
- Explaining AI rankings and scores
- Providing actionable hiring recommendations

Use the provided observations from tool executions to inform your answers.
Be specific, data-driven, and always cite your sources.
If you're uncertain, acknowledge it rather than making assumptions."""

        if observations:
            observations_text = "\n\nTool Observations:\n" + "\n".join(
                f"- {obs}" for obs in observations
            )
            base_prompt += observations_text

        return base_prompt

    def _build_user_prompt(
        self,
        query: str,
        observations: list[str],
        context: dict[str, Any],
    ) -> str:
        """Build user prompt.

        Args:
            query: Original query
            observations: Action observations
            context: Context information

        Returns:
            User prompt string
        """
        prompt = f"Recruiter Query: {query}\n\n"

        if context:
            prompt += f"Context: {json.dumps(context, indent=2)}\n\n"

        prompt += "Based on the tool observations above, provide a comprehensive answer to the recruiter's query."

        return prompt

    def _calculate_confidence(self, result: LLMResult, observations: list[str]) -> float:
        """Calculate confidence score for the response.

        Args:
            result: LLM result
            observations: Action observations

        Returns:
            Confidence score between 0 and 1
        """
        base_confidence = 0.7

        # Increase confidence if we have observations
        if observations:
            base_confidence += 0.2

        # Decrease confidence if safety ratings indicate issues
        if result.safety_ratings:
            high_risk = any(
                "HIGH" in rating or "MEDIUM" in rating
                for rating in result.safety_ratings.values()
            )
            if high_risk:
                base_confidence -= 0.3

        return min(max(base_confidence, 0.0), 1.0)

    async def get_memory_summary(self) -> dict[str, Any]:
        """Get summary of agent memory.

        Returns:
            Memory summary dictionary
        """
        return await self.memory.get_summary()

    async def clear_memory(self) -> None:
        """Clear agent memory."""
        await self.memory.clear()
