"""Candidate Compare Tool - Compare multiple candidates."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.recruiter_agent.tools.registry import Tool
from app.repositories.candidates import CandidateRepository
from app.services.llm_recruiter_service import LLMRecruiterService


class CandidateCompareTool(Tool):
    """Tool for comparing candidates."""

    def __init__(self, db: AsyncSession, organization_id: UUID, owner_id: UUID | None = None) -> None:
        """Initialize candidate compare tool.

        Args:
            db: Database session
            organization_id: Organization ID
        """
        self.db = db
        self.organization_id = organization_id
        self.owner_id = owner_id
        self.recruiter_service = LLMRecruiterService(db)

    async def execute(self, parameters: dict[str, Any], context: dict[str, Any]) -> str:
        """Execute candidate comparison.

        Args:
            parameters: Comparison parameters
            context: Execution context

        Returns:
            Comparison result as string
        """
        candidate_ids = parameters.get("candidate_ids", [])
        job_id = parameters.get("job_id")

        if not candidate_ids:
            return "No candidate IDs provided for comparison."
        owner_id = self.owner_id or context.get("recruiter_id") or context.get("user_id")
        if owner_id is None:
            return "Candidate comparison requires an authenticated recruiter context."

        # Convert string IDs to UUID if needed
        from app.schemas.auth import AuthContext

        auth_context = AuthContext(
            organization_id=self.organization_id,
            user_id=UUID(str(owner_id)),
            email="agent@neuralops.local",
            roles=["recruiter"],
        )

        # Use LLM service for comparison
        result = await self.recruiter_service.compare_candidates(
            auth=auth_context,
            candidate_ids=[UUID(cid) if isinstance(cid, str) else cid for cid in candidate_ids],
            job_description_id=UUID(job_id) if job_id else None,
        )

        return result.answer
