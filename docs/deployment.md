# Deployment Plan

## Free-Tier Friendly Strategy

- Frontend: Vercel.
- API: Railway or Render web service.
- Database: Neon/Supabase Postgres free tier.
- Redis: Upstash Redis.
- Vector DB: Qdrant Cloud free tier or Chroma in a small container for demos.
- Object storage: Cloudinary free tier or S3-compatible provider.
- MLflow: lightweight container on Render/Railway for demos; managed artifact storage for production.
- Monitoring: Grafana Cloud free tier plus Prometheus-compatible metrics.

## Cost Optimization

- Use batch embeddings and cache document hashes.
- Defer OCR until file type or extraction confidence requires it.
- Keep LLM calls behind explicit recruiter actions.
- Store original files in object storage and keep extracted text compressed.
- Scale workers separately from API.
