# Candidate Search Aggregation

Semantic search now returns candidate intelligence, not raw vector chunks.

## Runtime Flow

1. Embed recruiter query.
2. Query Qdrant candidate resume chunks.
3. Aggregate chunk hits by candidate.
4. Fetch candidate profile, latest resume, skills, and optional job-context match data from PostgreSQL.
5. Rerank by ATS alignment, semantic score, and experience fit.
6. Return recruiter-ready candidate cards.

## Response Shape

Search results include:

- candidate name
- semantic score
- optional job-context ATS alignment
- matched skills
- missing skills
- experience fit
- summary
- overlap reasoning

The UI should never expose Qdrant payloads or raw chunk internals.
