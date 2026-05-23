"""Task Planner - Plan and decompose recruiter queries into executable actions."""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from app.agents.recruiter_agent.agent import AgentAction


class TaskType(str, Enum):
    """Types of tasks the agent can perform."""

    SEARCH = "search"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    COMPARISON = "comparison"
    EXPLANATION = "explanation"
    RECOMMENDATION = "recommendation"


@dataclass
class Action:
    """Executable action with parameters."""

    action_type: AgentAction
    parameters: dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class TaskPlan:
    """Plan for executing a recruiter query."""

    task_type: TaskType
    suggested_action: Optional[AgentAction] = None
    actions: list[Action] = field(default_factory=list)
    reasoning: str = ""
    confidence: float = 0.0


class TaskPlanner:
    """Plan recruiter queries into executable actions."""

    # Keyword patterns for task classification
    PATTERNS = {
        TaskType.SEARCH: [
            r"\bfind\b",
            r"\bsearch\b",
            r"\blook for\b",
            r"\bcandidates?\b",
            r"\bmatching\b",
        ],
        TaskType.ANALYSIS: [
            r"\banalyze\b",
            r"\bassess\b",
            r"\bevaluate\b",
            r"\bskills?\b",
            r"\bqualifications?\b",
        ],
        TaskType.GENERATION: [
            r"\bgenerate\b",
            r"\bcreate\b",
            r"\bwrite\b",
            r"\bdraft\b",
            r"\boutreach\b",
            r"\bemail\b",
            r"\binterview\b",
        ],
        TaskType.COMPARISON: [
            r"\bcompare\b",
            r"\bdifference\b",
            r"\bbetter\b",
            r"\bversus\b",
            r"\bvs\b",
        ],
        TaskType.EXPLANATION: [
            r"\bexplain\b",
            r"\bwhy\b",
            r"\bhow\b",
            r"\bwhat\b",
            r"\bmeaning\b",
            r"\bscore\b",
            r"\branking\b",
        ],
        TaskType.RECOMMENDATION: [
            r"\brecommend\b",
            r"\bsuggest\b",
            r"\badvice\b",
            r"\bshould\b",
            r"\bbest\b",
            r"\bhire\b",
        ],
    }

    async def plan_task(self, query: str, context: dict[str, Any]) -> TaskPlan:
        """Plan a task based on the query and context.

        Args:
            query: Recruiter's query
            context: Additional context (job_id, candidate_ids, etc.)

        Returns:
            TaskPlan with actions and reasoning
        """
        query_lower = query.lower()

        # Classify task type
        task_type = self._classify_task(query_lower)

        # Determine suggested action
        suggested_action = self._determine_action(task_type, query_lower, context)

        # Build action plan
        actions = self._build_actions(task_type, suggested_action, context)

        # Generate reasoning
        reasoning = self._generate_reasoning(task_type, suggested_action, query)

        # Calculate confidence
        confidence = self._calculate_confidence(task_type, query_lower, context)

        return TaskPlan(
            task_type=task_type,
            suggested_action=suggested_action,
            actions=actions,
            reasoning=reasoning,
            confidence=confidence,
        )

    def _classify_task(self, query: str) -> TaskType:
        """Classify the task type based on query.

        Args:
            query: Lowercase query string

        Returns:
            TaskType enum
        """
        scores = {task_type: 0 for task_type in TaskType}

        for task_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    scores[task_type] += 1

        # Return task type with highest score
        return max(scores, key=scores.get) if any(scores.values()) else TaskType.EXPLANATION

    def _determine_action(
        self,
        task_type: TaskType,
        query: str,
        context: dict[str, Any],
    ) -> Optional[AgentAction]:
        """Determine the primary action for the task.

        Args:
            task_type: Classified task type
            query: Query string
            context: Context information

        Returns:
            AgentAction or None
        """
        action_map = {
            TaskType.SEARCH: AgentAction.SEARCH_CANDIDATES,
            TaskType.COMPARISON: AgentAction.COMPARE_CANDIDATES,
            TaskType.GENERATION: self._determine_generation_action(query),
            TaskType.EXPLANATION: self._determine_explanation_action(query, context),
            TaskType.RECOMMENDATION: AgentAction.RECOMMEND_HIRING,
            TaskType.ANALYSIS: AgentAction.ANALYZE_SKILLS,
        }

        return action_map.get(task_type)

    def _determine_generation_action(self, query: str) -> AgentAction:
        """Determine which generation action to use.

        Args:
            query: Query string

        Returns:
            AgentAction
        """
        if "outreach" in query or "email" in query:
            return AgentAction.GENERATE_OUTREACH
        if "interview" in query:
            return AgentAction.SUGGEST_INTERVIEW
        return AgentAction.GENERATE_OUTREACH  # Default

    def _determine_explanation_action(
        self,
        query: str,
        context: dict[str, Any],
    ) -> AgentAction:
        """Determine which explanation action to use.

        Args:
            query: Query string
            context: Context information

        Returns:
            AgentAction
        """
        if "ranking" in query or "score" in query:
            return AgentAction.EXPLAIN_RANKING
        if "candidate" in query:
            return AgentAction.ANSWER_QUESTION
        return AgentAction.ANSWER_QUESTION  # Default

    def _build_actions(
        self,
        task_type: TaskType,
        suggested_action: Optional[AgentAction],
        context: dict[str, Any],
    ) -> list[Action]:
        """Build the list of actions to execute.

        Args:
            task_type: Task type
            suggested_action: Suggested primary action
            context: Context information

        Returns:
            List of Action objects
        """
        actions = []

        if suggested_action:
            parameters = self._extract_parameters(suggested_action, context)
            actions.append(
                Action(
                    action_type=suggested_action,
                    parameters=parameters,
                    description=f"Execute {suggested_action.value}",
                )
            )

        # Add follow-up actions based on task type
        if task_type == TaskType.COMPARISON:
            # Comparison might need search first
            if not context.get("candidate_ids"):
                actions.insert(
                    0,
                    Action(
                        action_type=AgentAction.SEARCH_CANDIDATES,
                        parameters=context,
                        description="Search for candidates to compare",
                    ),
                )

        return actions

    def _extract_parameters(
        self,
        action: AgentAction,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Extract parameters for an action from context.

        Args:
            action: Action type
            context: Context dictionary

        Returns:
            Parameters dictionary
        """
        params = {}

        if action == AgentAction.SEARCH_CANDIDATES:
            params["query"] = context.get("query", "")
            params["job_id"] = context.get("job_id")
            params["limit"] = context.get("limit", 10)

        elif action == AgentAction.COMPARE_CANDIDATES:
            params["candidate_ids"] = context.get("candidate_ids", [])
            params["job_id"] = context.get("job_id")

        elif action == AgentAction.GENERATE_OUTREACH:
            params["candidate_id"] = context.get("candidate_id")
            params["job_id"] = context.get("job_id")
            params["tone"] = context.get("tone", "professional")

        elif action == AgentAction.SUGGEST_INTERVIEW:
            params["candidate_id"] = context.get("candidate_id")
            params["job_id"] = context.get("job_id")
            params["duration"] = context.get("duration_minutes", 60)

        elif action == AgentAction.EXPLAIN_RANKING:
            params["candidate_id"] = context.get("candidate_id")
            params["job_id"] = context.get("job_id")

        elif action == AgentAction.ANALYZE_SKILLS:
            params["candidate_id"] = context.get("candidate_id")

        return params

    def _generate_reasoning(
        self,
        task_type: TaskType,
        suggested_action: Optional[AgentAction],
        query: str,
    ) -> str:
        """Generate reasoning explanation for the plan.

        Args:
            task_type: Task type
            suggested_action: Suggested action
            query: Original query

        Returns:
            Reasoning string
        """
        reasoning = f"Query classified as {task_type.value} task."
        if suggested_action:
            reasoning += f" Primary action: {suggested_action.value}."
        return reasoning

    def _calculate_confidence(
        self,
        task_type: TaskType,
        query: str,
        context: dict[str, Any],
    ) -> float:
        """Calculate confidence in the task plan.

        Args:
            task_type: Task type
            query: Query string
            context: Context information

        Returns:
            Confidence score between 0 and 1
        """
        base_confidence = 0.7

        # Increase confidence if context has relevant information
        if context.get("candidate_ids"):
            base_confidence += 0.1
        if context.get("job_id"):
            base_confidence += 0.1

        # Decrease confidence if query is ambiguous
        if len(query.split()) < 3:
            base_confidence -= 0.2

        return min(max(base_confidence, 0.0), 1.0)
