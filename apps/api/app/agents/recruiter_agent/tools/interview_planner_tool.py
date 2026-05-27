"""Interview Planner Tool - Generate interview plans."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.recruiter_agent.tools.registry import Tool
from app.repositories.candidates import CandidateRepository
from app.repositories.jobs import JobDescriptionRepository
from app.services.llm.providers import PromptManager, PromptTemplate
from app.services.llm.providers.gemini_provider import GenerationOptions
from app.services.llm_provider import get_llm_provider


class InterviewPlannerTool(Tool):
    """Tool for generating interview plans."""

    def __init__(self, db: AsyncSession, organization_id: UUID, owner_id: UUID | None = None) -> None:
        """Initialize interview planner tool.

        Args:
            db: Database session
            organization_id: Organization ID
        """
        self.db = db
        self.organization_id = organization_id
        self.owner_id = owner_id
        self.candidates = CandidateRepository(db)
        self.jobs = JobDescriptionRepository(db)
        self.prompt_manager = PromptManager()

    async def execute(self, parameters: dict[str, Any], context: dict[str, Any]) -> str:
        """Execute interview plan generation.

        Args:
            parameters: Generation parameters
            context: Execution context

        Returns:
            Generated interview plan as string
        """
        candidate_id = parameters.get("candidate_id")
        job_id = parameters.get("job_id")
        duration = parameters.get("duration", 60)

        if not candidate_id:
            return "No candidate ID provided for interview planning."
        owner_id = self.owner_id or context.get("recruiter_id") or context.get("user_id")
        if owner_id is None:
            return "Interview planning requires an authenticated recruiter context."

        # Get candidate context
        candidate = await self.candidates.get_for_owner(UUID(candidate_id), self.organization_id, UUID(str(owner_id)))
        if not candidate:
            return f"Candidate {candidate_id} not found."

        candidate_context = f"Name: {candidate.full_name}\nHeadline: {candidate.headline}"

        # Get job context
        job_context = "No job specified"
        if job_id:
            job = await self.jobs.get_for_owner(UUID(job_id), self.organization_id, UUID(str(owner_id)))
            if job:
                job_context = f"Title: {job.title}\nRequired Skills: {', '.join(job.required_skills)}"

        # Generate interview plan
        provider = get_llm_provider()
        user_prompt = self.prompt_manager.format_prompt(
            PromptTemplate.INTERVIEW_PLAN,
            candidate_context=candidate_context,
            job_context=job_context,
            duration_minutes=duration,
            interview_type="technical",
        )

        options = GenerationOptions(temperature=0.3)
        result = await provider.complete(user_prompt, None, options)

        return result.text
