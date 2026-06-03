# Gemini Prompt Audit

Allowed Gemini responsibilities:
- Candidate summaries.
- Recruiter email drafting.
- ATS/ranking explanations using provided scores.
- Job description structured extraction and summarization.

Hardening applied:
- Candidate extraction defaults to deterministic mode, preventing Gemini from fabricating resume skills or seniority in worker ingestion.
- Prompt templates now prohibit invented years, seniority, skills, credentials, scores, rankings, employers, and compensation.
- JD structured extraction instructs Gemini to return empty/null fields when evidence is absent.

Remaining note:
- Some recruiter-agent tools still expose interview planning, skill analysis, and comparisons. They are not removed in this pass to avoid breaking existing integrations, but they should be product-gated or explicitly disabled if Gemini must be limited strictly to the allowed responsibilities above.

