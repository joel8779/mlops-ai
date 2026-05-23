# Deployment

```mermaid
flowchart TB
  Internet --> Ingress
  Ingress --> API[FastAPI Pods]
  API --> Postgres
  API --> Redis
  API --> Qdrant
  API --> MLflow
  Redis --> Worker[Celery Workers]
  Worker --> Qdrant
  Worker --> S3[Object Storage]
```

Deploy with Helm:

```bash
helm upgrade --install resume-intelligence infra/helm/resume-intelligence
```

Run database migrations before promoting traffic:

```bash
kubectl exec deploy/resume-api -- alembic upgrade head
```
