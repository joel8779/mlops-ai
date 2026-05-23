# Backend Installation Guide

## Install Commands

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

On Windows PowerShell:

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## Environment Variables

Copy the root example file and edit secrets before production use:

```bash
cp .env.example .env
```

For local Docker development, the defaults point to Compose service names such as `postgres`,
`redis`, `qdrant`, `minio`, and `mlflow`.

## Docker Startup

```bash
docker compose up --build
```

API: `http://localhost:8000`
Docs: `http://localhost:8000/docs`
Metrics: `http://localhost:8000/metrics`
MLflow: `http://localhost:5000`
Qdrant: `http://localhost:6333/dashboard`
MinIO: `http://localhost:9001`

## Alembic Migrations

```bash
docker compose exec api alembic upgrade head
docker compose exec api alembic revision --autogenerate -m "describe change"
```

For local non-Docker runs, set `DATABASE_URL` and `SYNC_DATABASE_URL` to localhost addresses,
then run:

```bash
cd apps/api
alembic upgrade head
```

## Local Development

```bash
cd apps/api
uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000
```

Start the worker in another terminal:

```bash
cd apps/api
celery -A app.workers.celery_app.celery_app worker --loglevel=INFO
```

## Troubleshooting

- `connection refused`: confirm `docker compose ps` shows healthy `postgres` and `redis`.
- `Invalid token`: verify `JWT_SECRET_KEY` is identical for API and worker.
- OCR returns empty text: install the `tesseract-ocr` system package outside Docker.
- Qdrant insert fails: confirm `QDRANT_URL` points to `http://qdrant:6333` in Docker or `http://localhost:6333` locally.
- Slow first parse: `sentence-transformers/all-MiniLM-L6-v2` downloads on first worker startup.
