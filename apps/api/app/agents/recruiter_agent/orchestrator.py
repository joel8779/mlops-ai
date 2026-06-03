"""Agent Orchestrator - Manage multiple agent instances and workflows."""

import asyncio
from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.recruiter_agent.agent import RecruiterAgent, AgentResponse


@dataclass
class OrchestratorConfig:
    """Configuration for agent orchestrator."""

    max_concurrent_agents: int = 5
    agent_timeout_seconds: int = 120
    enable_caching: bool = True
    enable_logging: bool = True


class AgentOrchestrator:
    """Orchestrate multiple agent instances and manage workflows."""

    def __init__(
        self,
        db: AsyncSession,
        config: Optional[OrchestratorConfig] = None,
    ) -> None:
        """Initialize agent orchestrator.

        Args:
            db: Database session
            config: Optional orchestrator configuration
        """
        self.db = db
        self.config = config or OrchestratorConfig()
        self._active_agents: dict[UUID, RecruiterAgent] = {}
        self._agent_lock = asyncio.Lock()
        self._response_cache: dict[str, AgentResponse] = {}

    async def create_agent(
        self,
        organization_id: UUID,
        user_id: UUID,
        session_id: Optional[UUID] = None,
    ) -> RecruiterAgent:
        """Create a new agent instance.

        Args:
            organization_id: Organization ID
            user_id: User ID
            session_id: Optional session ID

        Returns:
            RecruiterAgent instance
        """
        async with self._agent_lock:
            # Check concurrent agent limit
            if len(self._active_agents) >= self.config.max_concurrent_agents:
                # Remove oldest idle agent
                oldest_id = next(iter(self._active_agents))
                del self._active_agents[oldest_id]

            agent = RecruiterAgent(
                db=self.db,
                organization_id=organization_id,
                user_id=user_id,
            )
            agent_id = session_id or uuid4()
            self._active_agents[agent_id] = agent

            return agent

    async def get_agent(self, agent_id: UUID) -> Optional[RecruiterAgent]:
        """Get an existing agent instance.

        Args:
            agent_id: Agent ID

        Returns:
            RecruiterAgent or None
        """
        return self._active_agents.get(agent_id)

    async def remove_agent(self, agent_id: UUID) -> None:
        """Remove an agent instance.

        Args:
            agent_id: Agent ID
        """
        async with self._agent_lock:
            if agent_id in self._active_agents:
                del self._active_agents[agent_id]

    async def process_query(
        self,
        organization_id: UUID,
        user_id: UUID,
        query: str,
        context: Optional[dict[str, Any]] = None,
        session_id: Optional[UUID] = None,
        enable_cot: bool = True,
    ) -> AgentResponse:
        """Process a query through the orchestrator.

        Args:
            organization_id: Organization ID
            user_id: User ID
            query: Recruiter query
            context: Additional context
            session_id: Optional session ID for continuity
            enable_cot: Whether to use chain-of-thought

        Returns:
            AgentResponse
        """
        # Check cache
        cache_key = f"{organization_id}:{user_id}:{hash(query)}"
        if self.config.enable_caching and cache_key in self._response_cache:
            return self._response_cache[cache_key]

        # Get or create agent
        agent = await self.get_agent(session_id) if session_id else None
        if not agent:
            agent = await self.create_agent(organization_id, user_id, session_id)

        # Process with timeout
        try:
            response = await asyncio.wait_for(
                agent.process_query(query, context, enable_cot),
                timeout=self.config.agent_timeout_seconds,
            )
        except asyncio.TimeoutError:
            # Return timeout response
            response = AgentResponse(
                answer="I'm sorry, but processing your query took too long. Please try a simpler query or contact support.",
                thoughts=[],
                actions_taken=[],
                sources_used=[],
                confidence=0.0,
                metadata={"error": "timeout", "timeout_seconds": self.config.agent_timeout_seconds},
            )

        # Cache response
        if self.config.enable_caching:
            self._response_cache[cache_key] = response

        return response

    async def batch_process_queries(
        self,
        organization_id: UUID,
        user_id: UUID,
        queries: list[str],
        context: Optional[dict[str, Any]] = None,
    ) -> list[AgentResponse]:
        """Process multiple queries in parallel.

        Args:
            organization_id: Organization ID
            user_id: User ID
            queries: List of queries
            context: Shared context

        Returns:
            List of AgentResponse objects
        """
        tasks = [
            self.process_query(
                organization_id=organization_id,
                user_id=user_id,
                query=query,
                context=context,
            )
            for query in queries
        ]

        return await asyncio.gather(*tasks, return_exceptions=True)

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self._response_cache.clear()

    async def get_active_agent_count(self) -> int:
        """Get the number of active agents.

        Returns:
            Number of active agents
        """
        async with self._agent_lock:
            return len(self._active_agents)

    async def shutdown(self) -> None:
        """Shutdown the orchestrator and clean up resources."""
        async with self._agent_lock:
            for agent in self._active_agents.values():
                await agent.clear_memory()
            self._active_agents.clear()
        self.clear_cache()
