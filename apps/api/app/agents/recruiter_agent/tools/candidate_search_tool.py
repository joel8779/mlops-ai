"""Candidate Search Tool - Search for candidates matching criteria."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.recruiter_agent.tools.registry import Tool
from app.repositories.candidates import CandidateRepository
from app.services.semantic_search_service import SemanticSearchService


class CandidateSearchTool(Tool):
    """Tool for searching candidates."""

    def __init__(self, db: AsyncSession, organization_id: UUID, owner_id: UUID | None = None) -> None:
        """Initialize candidate search tool.

        Args:
            db: Database session
            organization_id: Organization ID
        """
        self.db = db
        self.organization_id = organization_id
        self.owner_id = owner_id
        self.candidates = CandidateRepository(db)
        self.search_service = SemanticSearchService(db)

    async def execute(self, parameters: dict[str, Any], context: dict[str, Any]) -> str:
        """Execute candidate search.

        Args:
            parameters: Search parameters
            context: Execution context

        Returns:
            Search results as string
        """
        query = parameters.get("query", "")
        job_id = parameters.get("job_id")
        limit = parameters.get("limit", 10)
        owner_id = self.owner_id or context.get("recruiter_id") or context.get("user_id")
        if owner_id is None:
            return "Candidate search requires an authenticated recruiter context."

        # Perform semantic search
        results = await self.search_service.search_candidates(
            organization_id=self.organization_id,
            owner_id=UUID(str(owner_id)),
            query=query,
            job_description_id=job_id,
            limit=limit,
        )

        # Format results
        if not results:
            return f"No candidates found matching query: {query}"

        output = f"Found {len(results)} candidates:\n\n"
        for i, candidate in enumerate(results, 1):
            output += f"{i}. {candidate.full_name}\n"
            output += f"   Headline: {candidate.headline}\n"
            output += f"   Location: {candidate.location}\n"
            output += f"   Match Score: {getattr(candidate, 'match_score', 'N/A')}\n\n"

        return output
