# ML and MLOps Design

## Ranking Algorithm

Initial ranking is a hybrid score:

```text
score =
  0.35 * semantic_similarity(candidate_embedding, job_embedding)
  0.25 * normalized_skill_overlap
  0.15 * relevant_experience_score
  0.10 * title_similarity
  0.10 * recency_and_seniority_score
  0.05 * recruiter_feedback_prior
```

Each component is stored as an explanation factor. Later phases replace or calibrate this with a trained learning-to-rank model registered in MLflow.

## RAG Pipeline

1. Parse resumes and job descriptions into structured chunks.
2. Embed chunks with `sentence-transformers`.
3. Store vectors in Qdrant with organization and candidate metadata.
4. Retrieve relevant candidates and snippets for recruiter queries.
5. Pass retrieved evidence to an LLM for grounded summaries, comparisons, and explanations.

## Feature Store Design

Feature tables live in Postgres first:

- `candidate_features`: profile, skill, seniority, and recency features.
- `job_features`: required skills, seniority, domain, and embedding references.
- `ranking_feedback`: human actions, shortlist decisions, rejections, and interview outcomes.

## Evaluation

- Ranking: NDCG@k, MAP@k, precision@k, recruiter acceptance rate.
- Parsing: field-level F1, skill extraction precision/recall.
- Fairness: score distribution and selection-rate checks across available, compliant demographic proxies only when legally appropriate.
- Drift: embedding centroid shifts, skill distribution changes, parse failure rates.
