# Candidate Extraction Forensics

Problem:

Candidates stayed as `Candidate Profile` with no skills, which means extraction and persistence were not producing recruiter-ready candidate intelligence.

Extraction hierarchy implemented:

1. Gemini structured extraction, when Gemini is configured and available.
2. Resume header parsing.
3. Email-derived name extraction.
4. Filename parsing.
5. PDF metadata.
6. Regex fallback.

Persisted fields:

- `Candidate.full_name`
- `Candidate.email`
- `Candidate.phone`
- `Candidate.headline`
- `Candidate.summary`
- `Candidate.raw_profile.education`
- `Candidate.raw_profile.experience`
- `Candidate.raw_profile.projects`
- `Candidate.raw_profile.inferred_seniority`
- `Candidate.raw_profile.skills`
- `CandidateSkill` rows

Safety behavior:

- `Candidate Profile` is blocked as a detected real name.
- A real existing candidate name is not overwritten by fallback identity.
- Gemini failures fall back to deterministic extraction instead of failing the whole resume.

Validation probe:

Input text with `Jane Doe`, `jane@example.com`, `Python`, `FastAPI`, `Docker`, `PostgreSQL`, and `5 years` returns:

- full name: `Jane Doe`
- email: `jane@example.com`
- skills: `docker`, `fastapi`, `postgresql`, `python`
- seniority: `mid`
