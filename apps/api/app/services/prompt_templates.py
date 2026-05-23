RECRUITER_SYSTEM_PROMPT = (
    "You are a precise recruiting intelligence assistant. Use only the provided context, "
    "cite candidate IDs when making claims, and avoid protected-class or demographic inferences."
)

CANDIDATE_SUMMARY_PROMPT = """Summarize this candidate for a recruiter.

Candidate context:
{context}

Return: strengths, risks, best-fit roles, and evidence."""

INTERVIEW_QUESTIONS_PROMPT = """Generate {count} interview questions.

Candidate context:
{candidate_context}

Job context:
{job_context}

Mix technical, behavioral, and evidence-checking questions."""

COMPARISON_PROMPT = """Compare the following candidates for the role.

Job context:
{job_context}

Candidates:
{candidate_context}

Return a concise ranking with tradeoffs and evidence."""

COPILOT_PROMPT = """Recruiter query:
{query}

Retrieved candidate evidence:
{context}

Answer naturally, recommend next actions, and include citations using candidate IDs."""
