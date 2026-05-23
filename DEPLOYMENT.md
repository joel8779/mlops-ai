# Deployment Guide - Resume Intelligence Platform

## Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (for production)
- Helm 3.x
- Terraform 1.6+
- AWS/GCP/Azure account (for cloud deployment)
- Gemini API key

## Environment Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-org/mlops-ai.git
cd mlops-ai
```

### 2. Configure environment variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Required environment variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/resume_ai

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# Vector Database
QDRANT_URL=http://localhost:6333

# Gemini LLM
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
LLM_PROVIDER=gemini

# Authentication
JWT_SECRET_KEY=your-secret-key
CLERK_SECRET_KEY=your-clerk-secret-key
CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key

# S3/MinIO
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET=resume-uploads
```

## Local Development

### Using Docker Compose

```bash
# Start all services
docker-compose -f infra/docker/production-compose.yml up -d

# Run database migrations
docker-compose exec api alembic upgrade head

# Seed demo data
docker-compose exec api python -m app.scripts.seed_demo

# View logs
docker-compose logs -f
```

### Manual Setup

```bash
# Backend
cd apps/api
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload

# Frontend
cd apps/web
npm install
npm run dev
```

## Production Deployment

### Kubernetes Deployment

#### 1. Build and push Docker images

```bash
docker build -t your-registry/resume-intelligence-api:latest -f infra/docker/production.Dockerfile apps/api
docker push your-registry/resume-intelligence-api:latest
```

#### 2. Install using Helm

```bash
# Add Helm repository
helm repo add resume-intelligence https://charts.resume-intelligence.com

# Update repository
helm repo update

# Install
helm install resume-intelligence resume-intelligence/resume-intelligence \
  --namespace default \
  --values infra/helm/resume-intelligence/values.yaml \
  --set gemini.apiKey=your-gemini-api-key \
  --set database.url=your-database-url
```

#### 3. Configure Ingress

The ingress is configured in `infra/k8s/ingress.yaml`. Update the host and TLS settings:

```yaml
spec:
  tls:
  - hosts:
    - api.your-domain.com
    secretName: resume-intelligence-tls
  rules:
  - host: api.your-domain.com
```

### Terraform Infrastructure

#### 1. Initialize Terraform

```bash
cd infra/terraform
terraform init
```

#### 2. Configure variables

Create `terraform.tfvars`:

```hcl
aws_region = "us-east-1"
environment = "production"
cluster_name = "resume-intelligence"
domain = "resume-intelligence.com"
```

#### 3. Apply infrastructure

```bash
terraform plan
terraform apply
```

## CI/CD Pipeline

### GitHub Actions

The `.github/workflows/deploy.yml` file contains the CI/CD pipeline:

1. **On push to main:**
   - Run tests
   - Build Docker images
   - Push to registry
   - Deploy to staging

2. **On release:**
   - Run full test suite
   - Build production images
   - Deploy to production
   - Run smoke tests

### Manual Deployment

```bash
# Run tests
pytest apps/api/tests/

# Build
docker build -t resume-intelligence-api:latest .

# Deploy
kubectl apply -f infra/k8s/
```

## Monitoring and Observability

### Prometheus Metrics

Metrics are exposed at `/metrics` endpoint:

- Request latency
- Request count
- Error rate
- Database query time
- LLM token usage
- Cache hit rate

### Grafana Dashboards

Import the provided dashboards from `infra/monitoring/grafana-dashboards/`:

- API Performance
- Database Performance
- LLM Usage
- System Resources

### Logging

Logs are structured JSON:

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "message": "Request completed",
  "request_id": "abc123",
  "duration_ms": 150,
  "user_id": "user-123"
}
```

## Troubleshooting

### Database Connection Issues

```bash
# Check database status
kubectl exec -it postgres-0 -- pg_isready

# View logs
kubectl logs -f deployment/postgres
```

### Redis Connection Issues

```bash
# Check Redis status
kubectl exec -it redis-0 -- redis-cli ping

# View logs
kubectl logs -f deployment/redis
```

### LLM API Issues

```bash
# Check Gemini API key
echo $GEMINI_API_KEY

# Test connection
curl -X POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GEMINI_API_KEY
```

## Scaling

### Horizontal Pod Autoscaler

The HPA is configured to scale based on CPU and memory:

```yaml
minReplicas: 3
maxReplicas: 10
targetCPUUtilizationPercentage: 70
targetMemoryUtilizationPercentage: 80
```

### Vertical Scaling

Adjust resource limits in `infra/k8s/api-deployment.yaml`:

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "4000m"
```

## Backup and Recovery

### Database Backup

```bash
# Backup
kubectl exec postgres-0 -- pg_dump resume_ai > backup.sql

# Restore
kubectl exec -i postgres-0 -- psql resume_ai < backup.sql
```

### Vector Database Backup

Qdrant snapshots:

```bash
# Create snapshot
curl -X PUT http://qdrant:6333/collections/candidate_embeddings/snapshots/my-snapshot

# Restore from snapshot
curl -X PUT http://qdrant:6333/collections/candidate_embeddings/snapshots/recover \
  -d '{"location": "my-snapshot"}'
```

## Security

### Secrets Management

Use Kubernetes secrets or a secret manager:

```bash
# Create secret
kubectl create secret generic resume-intelligence-secrets \
  --from-literal=database-url=$DATABASE_URL \
  --from-literal=gemini-api-key=$GEMINI_API_KEY
```

### SSL/TLS

Use cert-manager for automatic certificate management:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/your-org/mlops-ai/issues
- Documentation: https://docs.resume-intelligence.com
- Email: support@resume-intelligence.com
