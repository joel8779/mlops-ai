"""Centralized prompt management for LLM interactions."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class PromptTemplate(str, Enum):
    """Named prompt templates."""

    RECRUITER_SYSTEM = "recruiter_system"
    CANDIDATE_SUMMARY = "candidate_summary"
    INTERVIEW_QUESTIONS = "interview_questions"
    CANDIDATE_COMPARISON = "candidate_comparison"
    ATS_EXPLANATION = "ats_explanation"
    RANKING_EXPLANATION = "ranking_explanation"
    OUTREACH_EMAIL = "outreach_email"
    INTERVIEW_PLAN = "interview_plan"
    JOB_DESCRIPTION_ENHANCEMENT = "job_description_enhancement"
    SKILL_EXTRACTION = "skill_extraction"
    RESUME_PARSING = "resume_parsing"
    RAG_RECRUITER = "rag_recruiter"


@dataclass
class Prompt:
    """Prompt with metadata."""

    template: str
    variables: list[str]
    description: str
    model_type: str = "reasoning"
    temperature: float = 0.2
    max_tokens: Optional[int] = None


class PromptManager:
    """Centralized prompt management system."""

    PROMPTS: dict[PromptTemplate, Prompt] = {
        PromptTemplate.RECRUITER_SYSTEM: Prompt(
            template="""You are an expert AI recruiter assistant with deep knowledge of hiring practices, candidate evaluation, and talent acquisition.

Your role is to help recruiters make informed decisions by:
- Analyzing candidate qualifications and fit
- Generating relevant interview questions
- Comparing candidates objectively
- Providing data-driven insights
- Maintaining professional and ethical standards

Always be:
- Objective and unbiased
- Data-driven and evidence-based
- Professional and respectful
- Clear and concise
- Focused on helping the recruiter succeed

Do not invent facts, years of experience, seniority, skills, scores, rankings, employers, or credentials. If evidence is absent, say it is not available.""",
            variables=[],
            description="System prompt for recruiter AI assistant",
            model_type="reasoning",
        ),
        PromptTemplate.CANDIDATE_SUMMARY: Prompt(
            template="""Write a clean, recruiter-ready and concise recruiter briefing card in plain text.

Maximum length: 250 words.

Use exactly these section headings:
Candidate Overview
Technical Strengths
Relevant Experience
Hiring Concerns
Recommended Fit
Interview Focus Areas

Rules:
- Use only evidence from the supplied profile and resume excerpt.
- Do not invent facts, years, seniority, skills, employers, credentials, ATS scores, or role fit certainty.
- Do not repeat resume lines verbatim.
- Candidate Overview must be 2-3 short sentences.
- Other sections must use concise bullets beginning with "- ".
- Group related technologies where useful.
- Mention fresher, student status, missing internships, or gaps only when the evidence supports it.
- If evidence is missing, write "- Not available" for that section.
- Do not use markdown tables, bold markers, numbered lists, or giant paragraphs.
- Keep language direct, recruiter-readable, and hiring-focused.

Candidate Information:
{context}""",
            variables=["context"],
            description="Generate concise recruiter summary",
            model_type="reasoning",
        ),
        PromptTemplate.INTERVIEW_QUESTIONS: Prompt(
            template="""Generate {count} interview questions for this candidate based on their profile and the job requirements.

Candidate Profile:
{candidate_context}

Job Requirements:
{job_context}

For each question, provide:
1. The question itself
2. What you're assessing (skill, experience, cultural fit, etc.)
3. What to look for in a good answer

Format as a numbered list.""",
            variables=["count", "candidate_context", "job_context"],
            description="Generate interview questions",
            model_type="reasoning",
        ),
        PromptTemplate.CANDIDATE_COMPARISON: Prompt(
            template="""Compare the following candidates for this position.

Job Requirements:
{job_context}

Candidate Profiles:
{candidate_context}

Provide a structured comparison covering:
1. Overall ranking with rationale
2. Strengths of each candidate
3. Weaknesses or concerns for each candidate
4. Best fit recommendation
5. Specific follow-up questions for each candidate

Be objective and data-driven. Do not create new scores, years, seniority, skills, or facts that are absent from the supplied profiles.""",
            variables=["job_context", "candidate_context"],
            description="Compare multiple candidates",
            model_type="reasoning",
        ),
        PromptTemplate.ATS_EXPLANATION: Prompt(
            template="""Explain the ATS (Applicant Tracking System) score for this candidate.

Candidate Profile:
{candidate_context}

Job Requirements:
{job_context}

ATS Score: {ats_score}
Score Breakdown:
{score_breakdown}

Provide:
1. What the score means
2. Key factors contributing to the score
3. Areas where the candidate excels
4. Areas for improvement
5. Recommendations for the recruiter

Do not change or fabricate the ATS score. Explain only the provided score and breakdown.""",
            variables=["candidate_context", "job_context", "ats_score", "score_breakdown"],
            description="Explain ATS scoring",
            model_type="reasoning",
        ),
        PromptTemplate.RANKING_EXPLANATION: Prompt(
            template="""Explain the AI ranking for this candidate.

Candidate Profile:
{candidate_context}

Job Requirements:
{job_context}

Ranking Score: {ranking_score}
Ranking Position: {ranking_position} out of {total_candidates}

Provide:
1. Why this candidate received this ranking
2. Key strengths that contributed to the score
3. Any concerns or gaps
4. How this candidate compares to top performers
5. Recommended next steps

Do not fabricate ranking scores, skills, seniority, or experience. Use only provided ranking data.""",
            variables=["candidate_context", "job_context", "ranking_score", "ranking_position", "total_candidates"],
            description="Explain AI ranking",
            model_type="reasoning",
        ),
        PromptTemplate.OUTREACH_EMAIL: Prompt(
            template="""Draft a personalized outreach email to this candidate.

Candidate Profile:
{candidate_context}

Job Description:
{job_context}

Tone: {tone}
Key Points to Include: {key_points}

The email should be:
- Personalized and specific to the candidate
- Professional yet engaging
- Clear about the opportunity
- Include a clear call to action
- Under 200 words
- Do not invent candidate background, company claims, compensation, or job details""",
            variables=["candidate_context", "job_context", "tone", "key_points"],
            description="Generate outreach email",
            model_type="fast",
            temperature=0.7,
        ),
        PromptTemplate.INTERVIEW_PLAN: Prompt(
            template="""Create a structured interview plan for this candidate.

Candidate Profile:
{candidate_context}

Job Requirements:
{job_context}

Interview Duration: {duration_minutes} minutes
Interview Type: {interview_type}

Provide a detailed plan including:
1. Interview structure (time allocation)
2. Specific questions for each section
3. Assessment criteria
4. Who should conduct each section
5. Evaluation rubric""",
            variables=["candidate_context", "job_context", "duration_minutes", "interview_type"],
            description="Generate interview plan",
            model_type="reasoning",
        ),
        PromptTemplate.JOB_DESCRIPTION_ENHANCEMENT: Prompt(
            template="""Enhance this job description to attract top talent.

Original Job Description:
{job_context}

Industry: {industry}
Company Culture: {company_culture}

Provide:
1. An enhanced, compelling job description
2. Key improvements made
3. Suggested additions for diversity and inclusion
4. Recommended keywords for SEO""",
            variables=["job_context", "industry", "company_culture"],
            description="Enhance job description",
            model_type="reasoning",
            temperature=0.5,
        ),
        PromptTemplate.SKILL_EXTRACTION: Prompt(
            template="""Extract and categorize skills from this resume text.

Resume Text:
{resume_text}

Extract skills into these categories:
1. Technical Skills (programming languages, frameworks, tools)
2. Soft Skills (communication, leadership, etc.)
3. Domain Skills (industry-specific knowledge)
4. Certifications

Format as structured JSON. Extract only skills explicitly present in the text; do not infer related skills.""",
            variables=["resume_text"],
            description="Extract skills from resume",
            model_type="fast",
        ),
        PromptTemplate.RESUME_PARSING: Prompt(
            template="""Parse this resume text into structured data.

Resume Text:
{resume_text}

Extract the following fields as JSON:
- full_name
- email
- phone
- location
- headline
- summary
- experience (list with company, title, dates, description)
- education (list with institution, degree, dates)
- skills (list)
- certifications (list)

Use null for missing fields. Do not infer years, seniority, skills, employers, or credentials that are not explicit.""",
            variables=["resume_text"],
            description="Parse resume into structured data",
            model_type="fast",
        ),
        PromptTemplate.RAG_RECRUITER: Prompt(
            template="""You are a recruiter AI assistant with access to candidate and job information.

Answer the recruiter's question using the provided context. If the context doesn't contain enough information, acknowledge this limitation.

Recruiter Question: {question}

Relevant Context:
{context}

Provide a clear, actionable answer. If you reference specific information, cite the source.""",
            variables=["question", "context"],
            description="RAG-based recruiter assistant",
            model_type="reasoning",
        ),
    }

    @classmethod
    def get_prompt(cls, template: PromptTemplate) -> Prompt:
        """Get a prompt template.

        Args:
            template: PromptTemplate enum

        Returns:
            Prompt object
        """
        return cls.PROMPTS.get(template)

    @classmethod
    def format_prompt(cls, template: PromptTemplate, **kwargs: Any) -> str:
        """Format a prompt with variables.

        Args:
            template: PromptTemplate enum
            **kwargs: Variable values

        Returns:
            Formatted prompt string

        Raises:
            ValueError: If required variables are missing
        """
        prompt = cls.get_prompt(template)
        if not prompt:
            raise ValueError(f"Prompt template {template} not found")

        # Check for missing variables
        missing = [v for v in prompt.variables if v not in kwargs]
        if missing:
            raise ValueError(f"Missing required variables: {missing}")

        return prompt.template.format(**kwargs)

    @classmethod
    def get_all_templates(cls) -> dict[PromptTemplate, Prompt]:
        """Get all prompt templates.

        Returns:
            Dictionary of all prompts
        """
        return cls.PROMPTS.copy()

    @classmethod
    def add_custom_prompt(cls, template: PromptTemplate, prompt: Prompt) -> None:
        """Add or update a custom prompt.

        Args:
            template: PromptTemplate enum
            prompt: Prompt object
        """
        cls.PROMPTS[template] = prompt
