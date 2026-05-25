# Semantic Search Runtime

Semantic search uses Qdrant candidate embeddings, not SQL text search.

## Flow

1. Recruiter enters a natural-language query.
2. `SemanticSearchService` embeds the query.
3. Qdrant is queried with an organization filter.
4. Optional facets such as skills and location filter the returned payloads.
5. Results are reranked with lightweight lexical overlap from the returned resume chunk.

## Search Examples

- `FastAPI backend engineer`
- `Kubernetes + GCP`
- `ML engineer with NLP`

## Operational Requirements

Search requires processed resumes with candidate embeddings. If resumes are uploaded but still queued/parsing, search should show empty states rather than fake matches.

## Related APIs

- `POST /api/v1/search/candidates`
- Qdrant collection: configured by `settings.qdrant_collection`
- Embedding runtime: `EmbeddingService`
