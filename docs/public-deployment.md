# Public Deployment Guide - PHASE 17

**Date**: 2026-05-23
**Phase**: STEP 8 - PUBLIC DEPLOYMENT

## Overview

This guide covers deploying the AI Resume Intelligence Platform to production using modern cloud services.

## Architecture

### Frontend (Vercel)
- Platform: Vercel
- Framework: Next.js 15
- Build: Static export with ISR
- Edge functions for API routes

### Backend (Railway/Render)
- Platform: Railway (recommended) or Render
- Runtime: Python 3.11+
- Framework: FastAPI
- Workers: Celery with Redis

### Database (Neon)
- Platform: Neon (PostgreSQL)
- Version: PostgreSQL 15+
- Features: Serverless, branching

### Cache (Upstash)
- Platform: Upstash Redis
- Version: Redis 7+
- Features: Serverless, edge caching

### Vector DB (Qdrant Cloud)
- Platform: Qdrant Cloud
- Version: Qdrant 1.7+
- Features: Managed vector database

### Storage (Cloudflare R2 or MinIO)
- Platform: Cloudflare R2 (recommended) or MinIO
- Features: S3-compatible object storage

## Environment Variables

### Frontend (Vercel)
```env
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com/api/v1
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com
```

### Backend (Railway/Render)
```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379

# Qdrant
QDRANT_URL=https://your-qdrant-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Object Storage
S3_ENDPOINT_URL=https://your-r2-endpoint.r2.cloudflarest.com
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=resume-intelligence

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_PRO_MODEL=gemini-2.5-pro

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=14

# CORS
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Observability
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=https://your-otlp-endpoint
OTEL_SERVICE_NAME=ai-resume-intelligence

# Application
APP_NAME=AI Resume Intelligence
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false

# File Upload
MAX_UPLOAD_BYTES=10485760  # 10MB

# Celery
CELERY_BROKER_URL=redis://host:6379/0
CELERY_RESULT_BACKEND=redis://host:6379/0
```

## Deployment Steps

### 1. Set Up Neon PostgreSQL

1. Create account at [Neon](https://neon.tech)
2. Create a new project
3. Copy the connection string
4. Add to Railway/Render environment variables as `DATABASE_URL`

### 2. Set Up Upstash Redis

1. Create account at [Upstash](https://upstash.com)
2. Create a new Redis database
3. Copy the connection string
4. Add to Railway/Render environment variables as `REDIS_URL`

### 3. Set Up Qdrant Cloud

1. Create account at [Qdrant Cloud](https://cloud.qdrant.io)
2. Create a new cluster
3. Copy the endpoint and API key
4. Add to Railway/Render environment variables as `QDRANT_URL` and `QDRANT_API_KEY`

### 4. Set Up Cloudflare R2

1. Create account at [Cloudflare](https://cloudflare.com)
2. Enable R2 storage
3. Create a new bucket
4. Create API token with R2 permissions
5. Add to Railway/Render environment variables as `S3_ENDPOINT_URL`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME`

### 5. Set Up Gemini AI

1. Create account at [Google Cloud](https://cloud.google.com)
2. Enable Gemini API
3. Create API key
4. Add to Railway/Render environment variables as `GEMINI_API_KEY`

### 6. Deploy Backend to Railway

1. Create account at [Railway](https://railway.app)
2. Create a new project
3. Connect GitHub repository
4. Select `apps/api` as root directory
5. Add environment variables
6. Deploy

**Railway Configuration**:
```yaml
# railway.json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:create_app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 7. Deploy Celery Worker to Railway

1. Add a new service to Railway project
2. Select same repository
3. Set start command: `celery -A app.workers.celery_app worker --loglevel=info`
4. Add same environment variables as backend
5. Deploy

### 8. Deploy Frontend to Vercel

1. Create account at [Vercel](https://vercel.com)
2. Import GitHub repository
3. Select `apps/web` as root directory
4. Add environment variables:
   - `NEXT_PUBLIC_API_BASE_URL`
   - `NEXT_PUBLIC_WS_URL`
5. Deploy

**Vercel Configuration**:
```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["iad1"],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### 9. Configure CORS

Update backend CORS configuration in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://your-vercel-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 10. Configure HTTPS

- Vercel automatically provides HTTPS
- Railway automatically provides HTTPS
- Ensure all environment variables use HTTPS URLs

### 11. Configure Secrets

- Use Railway's secret management for sensitive values
- Use Vercel's environment variables for frontend secrets
- Never commit secrets to git

### 12. Configure Observability

**OpenTelemetry**:
```env
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=https://your-otlp-endpoint
OTEL_SERVICE_NAME=ai-resume-intelligence
```

**Prometheus**:
- Enable metrics endpoint at `/metrics`
- Configure Prometheus to scrape backend

**Logging**:
- Structured JSON logs
- Send to log aggregation service

## Post-Deployment Steps

### 1. Run Database Migrations

```bash
# Connect to Railway shell
railway shell

# Run migrations
cd apps/api
alembic upgrade head
```

### 2. Seed Demo Data

```bash
# Connect to Railway shell
railway shell

# Run seed script
cd apps/api
python scripts/setup_demo_environment.py
```

### 3. Verify Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/health

# Frontend
curl https://yourdomain.com
```

### 4. Test Authentication

1. Navigate to https://yourdomain.com/sign-in
2. Register a new account
3. Verify login works
4. Verify protected routes work

### 5. Test Resume Upload

1. Navigate to https://yourdomain.com/resumes
2. Upload a test resume
3. Verify processing works

### 6. Test Semantic Search

1. Navigate to https://yourdomain.com/search
2. Enter a search query
3. Verify results appear

### 7. Test AI Copilot

1. Navigate to https://yourdomain.com/copilot
2. Ask a question
3. Verify response appears

## Monitoring

### Railway Monitoring
- CPU usage
- Memory usage
- Network traffic
- Error logs

### Vercel Analytics
- Page views
- Web Vitals
- Error tracking

### Custom Monitoring
- Prometheus metrics at `/metrics`
- OpenTelemetry traces
- Structured logs

## Rollback Strategy

### Frontend (Vercel)
- Vercel automatically keeps previous deployments
- Rollback via Vercel dashboard
- Git revert and redeploy

### Backend (Railway)
- Railway keeps deployment history
- Rollback via Railway dashboard
- Git revert and redeploy

### Database (Neon)
- Neon supports branching
- Create backup before migrations
- Rollback to previous branch

## Cost Estimates

### Monthly Costs (Production)
- Railway: $20-50/month (backend + worker)
- Vercel: $0-20/month (frontend)
- Neon: $25-100/month (database)
- Upstash: $5-20/month (Redis)
- Qdrant Cloud: $20-50/month (vector DB)
- Cloudflare R2: $0-10/month (storage)
- Gemini AI: Pay per usage

**Total**: ~$95-250/month

### Monthly Costs (Demo)
- Railway: $5-10/month (hobby plan)
- Vercel: $0 (hobby plan)
- Neon: $0 (free tier)
- Upstash: $0 (free tier)
- Qdrant Cloud: $0 (free tier)
- Cloudflare R2: $0 (free tier)
- Gemini AI: Pay per usage

**Total**: ~$5-10/month + Gemini usage

## Security Checklist

- [ ] All secrets are in environment variables
- [ ] HTTPS is enforced
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled
- [ ] Database connections are encrypted
- [ ] API keys are rotated regularly
- [ ] Logs don't contain sensitive data
- [ ] Monitoring is configured
- [ ] Backup strategy is in place
- [ ] Incident response plan is documented

## Troubleshooting

### Common Issues

**CORS Errors**
- Verify CORS origins in backend
- Check frontend API URL
- Ensure HTTPS is used

**Database Connection Errors**
- Verify DATABASE_URL
- Check Neon status
- Verify network access

**Redis Connection Errors**
- Verify REDIS_URL
- Check Upstash status
- Verify network access

**Qdrant Connection Errors**
- Verify QDRANT_URL and QDRANT_API_KEY
- Check Qdrant Cloud status
- Verify collection exists

**Gemini API Errors**
- Verify GEMINI_API_KEY
- Check API quota
- Verify model name

## Next Steps

After deployment:
1. Monitor metrics for 24 hours
2. Test all critical flows
3. Set up alerts
4. Document known issues
5. Prepare rollback procedures
