"""Outreach Generator Tool - Generate personalized outreach emails."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.recruiter_agent.tools.registry import Tool
from app.repositories.candidates import CandidateRepository
from app.repositories.jobs import JobDescriptionRepository
from app.services.llm.providers import PromptManager, PromptTemplate
from app.services.llm.providers.gemini_provider import GenerationOptions
from app.services.llm_provider import get_llm_provider


class OutreachGeneratorTool(Tool):
    """Tool for generating outreach emails."""

    def __init__(self, db: AsyncSession, organization_id: UUID) -> None:
        """Initialize outreach generator tool.

        Args:
            db: Database session
            organization_id: Organization ID
        """
        self.db = db
        self.organization_id = organization_id
        self.candidates = CandidateRepository(db)
        self.jobs = JobDescriptionRepository(db)
        self.prompt_manager = PromptManager()

    async def execute(self, parameters: dict[str, Any], context: dict[str, Any]) -> str:
        """Execute outreach generation.

        Args:
            parameters: Generation parameters
            context: Execution context

        Returns:
            Generated email as string
        """
        candidate_id = parameters.get("candidate_id")
        job_id = parameters.get("job_id")
        tone = parameters.get("tone", "professional")

        if not candidate_id:
            return "No candidate ID provided for outreach generation."

        # Get candidate context
        candidate = await self.candidates.get_for_org(UUID(candidate_id), self.organization_id)
        if not candidate:
            return f"Candidate {candidate_id} not found."

        candidate_context = f"Name: {candidate.full_name}\nHeadline: {candidate.headline}\nLocation: {candidate.location}"

        # Get job context
        job_context = "No job specified"
        if job_id:
            job = await self.jobs.get_for_org(UUID(job_id), self.organization_id)
            if job:
                job_context = f"Title: {job.title}\nDescription: {job.description[:500]}"

        # Generate email
        provider = get_llm_provider()
        user_prompt = self.prompt_manager.format_prompt(
            PromptTemplate.OUTREACH_EMAIL,
            candidate_context=candidate_context,
            job_context=job_context,
            tone=tone,
            key_points="Relevant experience, skills match, exciting opportunity",
        )

        options = GenerationOptions(temperature=0.7)
        result = await provider.complete(user_prompt, None, options)

        return result.text
