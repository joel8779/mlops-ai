# Architecture

AI Resume Intelligence is a multi-tenant hiring intelligence platform built around FastAPI, PostgreSQL, Redis, Qdrant, MLflow, Celery, and Next.js.

```mermaid
flowchart LR
  Web[Recruiter Web] --> API[FastAPI API]
  API --> PG[(PostgreSQL)]
  API --> Redis[(Redis Streams)]
  API --> Qdrant[(Qdrant)]
  API --> LLM[OpenAI/Gemini]
  Redis --> Worker[Celery Workers]
  Worker --> Parser[Resume/JD Parsers]
  Worker --> Embed[Embedding Service]
  Embed --> Qdrant
  Worker --> MLflow[MLflow]
```

All recruiter-facing APIs are tenant-aware and organization-scoped. Heavy AI work runs asynchronously through workers and events.
