# Release Notes

## AI Resume Intelligence Platform — Portfolio Release

This portfolio release represents a hardened, stabilized, and multi-tenant Applicant Tracking System (ATS) platform.

### Highlights
- **Structured LLM Extraction**: Extract resumes (PDFs, DOCX, images) via Google Gemini into validated JSON schemas.
- **Hybrid Semantic Search**: Vector-based candidate searching via Qdrant combined with Jaccard skill-match overlap and experience scoring.
- **Enterprise Security**: Redis-backed rate limits, JWT access/refresh token controls, and magic number byte file scanners.
- **Robust Local Parity**: Runnable local development stack with docker-compose database seeding (Postgres, Redis, Qdrant, MinIO, MLflow).
- **Production Infrastructure Configs**: Pre-packaged configs for Railway (backend), Vercel (frontend), Helm, and Kubernetes.
