from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import LLMUsageLog
from app.repositories.candidates import CandidateRepository
from app.repositories.jobs import JobDescriptionRepository
from app.schemas.ai import AIResponse
from app.schemas.auth import AuthContext
from app.services.llm_provider import LLMResult, get_llm_provider
from app.services.llm.providers import PromptManager, PromptTemplate
from app.services.llm.providers.gemini_provider import GenerationOptions


class LLMRecruiterService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.candidates = CandidateRepository(db)
        self.jobs = JobDescriptionRepository(db)
        self.provider = get_llm_provider()
        self.prompt_manager = PromptManager()

    async def summarize_candidate(self, auth: AuthContext, candidate_id: UUID) -> AIResponse:
        context = await self._candidate_context(candidate_id, auth.organization_id, auth.user_id)
        system_prompt = self.prompt_manager.format_prompt(PromptTemplate.RECRUITER_SYSTEM)
        user_prompt = self.prompt_manager.format_prompt(
            PromptTemplate.CANDIDATE_SUMMARY,
            context=context,
        )
        
        options = GenerationOptions(temperature=0.2)
        result = await self.provider.complete(user_prompt, system_prompt, options)

        # Persist summary only when the LLM returns non-empty content.
        candidate = await self.candidates.get_for_org(candidate_id, auth.organization_id)
        if candidate:
            if result.text and result.text.strip():
                candidate.summary = result.text
                await self.db.commit()
            else:
                # Preserve existing stored summary when LLM output is empty.
                result = result.__class__(**{**result.__dict__, "text": candidate.summary or ""})

        await self._log_usage(auth, "candidate_summary", result)
        return AIResponse(answer=result.text, usage=result.__dict__)

    async def interview_questions(
        self,
        auth: AuthContext,
        candidate_id: UUID,
        job_description_id: UUID | None,
        count: int,
    ) -> AIResponse:
        candidate_context = await self._candidate_context(candidate_id, auth.organization_id, auth.user_id)
        job_context = await self._job_context(job_description_id, auth.organization_id, auth.user_id)
        
        system_prompt = self.prompt_manager.format_prompt(PromptTemplate.RECRUITER_SYSTEM)
        user_prompt = self.prompt_manager.format_prompt(
            PromptTemplate.INTERVIEW_QUESTIONS,
            count=count,
            candidate_context=candidate_context,
            job_context=job_context,
        )
        
        options = GenerationOptions(temperature=0.3)
        result = await self.provider.complete(user_prompt, system_prompt, options)
        
        await self._log_usage(auth, "interview_questions", result)
        return AIResponse(answer=result.text, usage=result.__dict__)

    async def compare_candidates(
        self,
        auth: AuthContext,
        candidate_ids: list[UUID],
        job_description_id: UUID | None,
    ) -> AIResponse:
        contexts = [await self._candidate_context(candidate_id, auth.organization_id, auth.user_id) for candidate_id in candidate_ids]
        job_context = await self._job_context(job_description_id, auth.organization_id, auth.user_id)
        
        system_prompt = self.prompt_manager.format_prompt(PromptTemplate.RECRUITER_SYSTEM)
        user_prompt = self.prompt_manager.format_prompt(
            PromptTemplate.CANDIDATE_COMPARISON,
            job_context=job_context,
            candidate_context="\n\n".join(contexts),
        )
        
        options = GenerationOptions(temperature=0.2)
        result = await self.provider.complete(user_prompt, system_prompt, options)
        
        await self._log_usage(auth, "candidate_comparison", result)
        return AIResponse(answer=result.text, usage=result.__dict__)

    async def _candidate_context(self, candidate_id: UUID, organization_id: UUID, owner_id: UUID) -> str:
        candidate = await self.candidates.get_for_org(candidate_id, organization_id)
        if candidate is None:
            return f"Candidate {candidate_id} not found."
        resume = await self.candidates.latest_resume(candidate.id, organization_id)
        skills = await self.candidates.skills_for_candidate(candidate.id, organization_id)
        
        # Try to get resume text from extracted_text, fallback to raw_profile
        resume_text = ""
        if resume and resume.extracted_text:
            resume_text = resume.extracted_text
        elif candidate.raw_profile and isinstance(candidate.raw_profile, dict):
            # Check if raw_profile contains resume text
            resume_text = str(candidate.raw_profile.get("resume_text", ""))
        
        # Log what we're sending to Gemini
        from app.logging import get_logger
        logger = get_logger(__name__)
        logger.info(
            "summary_generation_input",
            candidate_id=str(candidate_id),
            resume_id=str(resume.id) if resume else None,
            resume_status=resume.status.value if resume else None,
            extracted_text_length=len(resume.extracted_text or "") if resume else 0,
            skills_count=len(skills),
            resume_text_length=len(resume_text),
            has_resume_text=bool(resume_text),
        )
        
        return (
            f"Candidate ID: {candidate.id}\nName: {candidate.full_name}\n"
            f"Headline: {candidate.headline}\nLocation: {candidate.location}\n"
            f"Skills: {', '.join(skills)}\nResume excerpt: {resume_text[:3000]}"
        )

    async def _job_context(self, job_id: UUID | None, organization_id: UUID, owner_id: UUID) -> str:
        if job_id is None:
            return "No job description provided."
        job = await self.jobs.get_for_org(job_id, organization_id)
        if job is None:
            return f"Job {job_id} not found."
        return (
            f"Job ID: {job.id}\nTitle: {job.title}\nCategory: {job.role_category}\n"
            f"Required skills: {', '.join(job.required_skills)}\nDescription: {job.description[:3000]}"
        )

    async def _log_usage(self, auth: AuthContext, feature: str, result: LLMResult) -> None:
        self.db.add(
            LLMUsageLog(
                organization_id=auth.organization_id,
                owner_id=auth.user_id,
                user_id=auth.user_id,
                provider=result.provider,
                model=result.model,
                feature=feature,
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                estimated_cost_usd=result.estimated_cost_usd,
            )
        )
        await self.db.commit()
