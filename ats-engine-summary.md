# ATS Engine Summary

The ATS engine remains deterministic and service-owned. Gemini prompts were tightened so LLM output may explain provided scores but must not fabricate or alter scores.

Current safeguards:
- ATS score generation is backend-owned, not prompt-owned.
- Prompt templates now explicitly prohibit invented ATS scores, skills, seniority, and experience.
- Candidate/JD parsing failures are surfaced explicitly instead of hidden behind fake labels.

Validated:
- `test_job_intelligence.py` passed in the focused suite.
- `test_ai_summary.py` passed after prompt hardening.

