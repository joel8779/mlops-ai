"""Skill Analyzer Tool - Analyze candidate skills."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.recruiter_agent.tools.registry import Tool
from app.repositories.candidates import CandidateRepository
from app.services.llm.providers import PromptManager, PromptTemplate
from app.services.llm.providers.gemini_provider import GenerationOptions
from app.services.llm_provider import get_llm_provider


class SkillAnalyzerTool(Tool):
    """Tool for analyzing candidate skills."""

    def __init__(self, db: AsyncSession, organization_id: UUID) -> None:
        """Initialize skill analyzer tool.

        Args:
            db: Database session
            organization_id: Organization ID
        """
        self.db = db
        self.organization_id = organization_id
        self.candidates = CandidateRepository(db)
        self.prompt_manager = PromptManager()

    async def execute(self, parameters: dict[str, Any], context: dict[str, Any]) -> str:
        """Execute skill analysis.

        Args:
            parameters: Analysis parameters
            context: Execution context

        Returns:
            Analysis result as string
        """
        candidate_id = parameters.get("candidate_id")

        if not candidate_id:
            return "No candidate ID provided for skill analysis."

        # Get candidate and skills
        candidate = await self.candidates.get_for_org(UUID(candidate_id), self.organization_id)
        if not candidate:
            return f"Candidate {candidate_id} not found."

        skills = await self.candidates.skills_for_candidate(UUID(candidate_id))
        resume = await self.candidates.latest_resume(UUID(candidate_id))

        resume_text = resume.extracted_text[:2000] if resume else ""

        # Generate skill analysis
        provider = get_llm_provider()
        user_prompt = self.prompt_manager.format_prompt(
            PromptTemplate.SKILL_EXTRACTION,
            resume_text=resume_text,
        )

        options = GenerationOptions(temperature=0.2, json_mode=True)
        result = await provider.complete(user_prompt, None, options)

        # Format output
        output = f"Skills for {candidate.full_name}:\n\n"
        output += f"Known Skills: {', '.join(skills)}\n\n"
        output += "AI Analysis:\n"
        output += result.text

        return output
