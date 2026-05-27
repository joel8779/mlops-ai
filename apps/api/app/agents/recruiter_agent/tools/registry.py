"""Tool Registry - Manage and execute agent tools."""

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.recruiter_agent.agent import AgentAction
from app.agents.recruiter_agent.tools.candidate_search_tool import CandidateSearchTool
from app.agents.recruiter_agent.tools.candidate_compare_tool import CandidateCompareTool
from app.agents.recruiter_agent.tools.outreach_generator_tool import OutreachGeneratorTool
from app.agents.recruiter_agent.tools.interview_planner_tool import InterviewPlannerTool
from app.agents.recruiter_agent.tools.ranking_explainer_tool import RankingExplainerTool
from app.agents.recruiter_agent.tools.skill_analyzer_tool import SkillAnalyzerTool


class Tool:
    """Base class for agent tools."""

    async def execute(self, parameters: dict[str, Any], context: dict[str, Any]) -> str:
        """Execute the tool.

        Args:
            parameters: Tool parameters
            context: Execution context

        Returns:
            Result string
        """
        raise NotImplementedError


class ToolRegistry:
    """Registry of available tools for the agent."""

    def __init__(self, db: AsyncSession, organization_id: Any, owner_id: Any | None = None) -> None:
        """Initialize tool registry.

        Args:
            db: Database session
            organization_id: Organization ID
        """
        self.db = db
        self.organization_id = organization_id
        self.owner_id = owner_id
        self._tools = {
            AgentAction.SEARCH_CANDIDATES: CandidateSearchTool(db, organization_id, owner_id),
            AgentAction.COMPARE_CANDIDATES: CandidateCompareTool(db, organization_id, owner_id),
            AgentAction.GENERATE_OUTREACH: OutreachGeneratorTool(db, organization_id, owner_id),
            AgentAction.SUGGEST_INTERVIEW: InterviewPlannerTool(db, organization_id, owner_id),
            AgentAction.EXPLAIN_RANKING: RankingExplainerTool(db, organization_id, owner_id),
            AgentAction.ANALYZE_SKILLS: SkillAnalyzerTool(db, organization_id, owner_id),
        }

    def get_tool(self, action: AgentAction) -> Optional[Tool]:
        """Get a tool by action type.

        Args:
            action: Agent action type

        Returns:
            Tool instance or None
        """
        return self._tools.get(action)

    def register_tool(self, action: AgentAction, tool: Tool) -> None:
        """Register a new tool.

        Args:
            action: Action type
            tool: Tool instance
        """
        self._tools[action] = tool

    def list_tools(self) -> list[AgentAction]:
        """List all available tools.

        Returns:
            List of AgentAction types
        """
        return list(self._tools.keys())
