# Recruiter Search Experience

Search should feel like asking the recruiting system for candidates, not inspecting vector infrastructure.

## Expected Queries

- `FastAPI backend engineer`
- `Kubernetes + GCP`
- `ML engineer with NLP`

## Expected Result Card

Each result should show:

- candidate name
- headline or location
- semantic relevance
- ATS alignment for the selected job
- matched skills
- recruiter-readable reasoning

## Product Rule

Do not expose raw chunks, vector payloads, collection names, or Qdrant internals in the recruiter UI.
