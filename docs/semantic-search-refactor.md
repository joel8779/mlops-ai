# Semantic Search Refactor

The search page has moved from vector-debugging output to recruiter intelligence output.

## Before

Search returned chunks, payloads, snippets, and vector internals.

## Now

Search returns aggregated candidates with recruiter-facing reasoning.

## Backend

`SemanticSearchService.search` requires a database session and returns `CandidateSearchResult`.

`raw_chunk_search` remains available only for advanced retrieval internals that need chunk-level data.

## Frontend

The search UI supports optional job context and shows:

- candidate identity
- semantic relevance
- ATS alignment when a job is selected
- matched skills
- overlap reasoning
