# AI Resume Intelligence SLOs

## API Availability
- SLI: successful API responses / total API responses.
- SLO: 99.5% monthly.
- Error budget: 0.5% monthly failed or unavailable requests.

## API Latency
- SLI: p95 `resume_ai_api_latency_seconds`.
- SLO: p95 under 1 second for non-AI API routes.

## AI Runtime Latency
- SLI: p95 `llm_request_latency_ms`.
- SLO: p95 under 10 seconds for Gemini-backed recruiter workflows.

## Retrieval Latency
- SLI: p95 `retrieval_topk_latency_ms`.
- SLO: p95 under 1.5 seconds for top-k retrieval.

## Queue Freshness
- SLI: `redis_stream_consumer_lag`.
- SLO: lag under 1,000 pending events for 99% of 10-minute windows.

## AI Quality
- SLI: hallucination and grounding events per AI response.
- SLO: fewer than 3 warning-level hallucination events per 15-minute window.
