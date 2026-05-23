# Local Development Guide - PHASE 18

**Date**: 2026-05-23
**Phase**: STEP 7 - DEVELOPER EXPERIENCE

## Overview

This guide covers the complete local development workflow for the AI Resume Intelligence Platform, including infrastructure startup, application startup, migrations, and troubleshooting.

## Prerequisites

### Required Software
- Docker Desktop (for containerized infrastructure)
- Python 3.11+ (for backend development)
- Node.js 18+ (for frontend development)
- psql (PostgreSQL client, optional)
- redis-cli (Redis client, optional)

### System Requirements
- 8GB RAM minimum (16GB recommended)
- 20GB disk space minimum
- Docker with at least 4GB RAM allocated

## Quick Start

### One-Command Startup (Recommended)

**Windows PowerShell**:
```powershell
cd c:\Users\Lenovo\Desktop\mlops-ai
.\scripts\dev-start.ps1
```

**Linux/Mac**:
```bash
cd /path/to/mlops-ai
chmod +x scripts/dev-start.sh
./scripts/dev-start.sh
```

**With Frontend**:
```powershell
.\scripts\dev-start.ps1 --frontend
```

This script will:
1. Start infrastructure services (PostgreSQL, Redis, Qdrant, MinIO, MLflow)
2. Wait for services to be healthy
3. Validate connectivity
4. Run database migrations
5. Start the backend API
6. Optionally start the frontend

## Docker Startup

### Start All Infrastructure Services

```bash
cd c:\Users\Lenovo\Desktop\mlops-ai
docker compose up -d
```

This starts all services including:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Qdrant (port 6333, 6334)
- MinIO (port 9000, 9001)
- MLflow (port 5000)
- API (port 8000)
- Worker (Celery)

### Start Infrastructure Only

```bash
docker compose up -d postgres redis qdrant minio mlflow
```

### Stop All Services

```bash
docker compose down
```

### Stop and Remove Volumes

```bash
docker compose down -v
```

⚠️ **Warning**: This will delete all data including database data.

## Infrastructure Startup Order

### Correct Startup Order

1. **Infrastructure Services** (can start in parallel):
   - PostgreSQL
   - Redis
   - Qdrant
   - MinIO

2. **MinIO Init** (depends on MinIO):
   - Wait for MinIO to be healthy
   - Create buckets

3. **MLflow** (can start in parallel with infrastructure):
   - MLflow server

4. **API** (depends on infrastructure):
   - Wait for PostgreSQL to be healthy
   - Wait for Redis to be healthy
   - Wait for Qdrant to be healthy
   - Wait for MinIO init to complete

5. **Worker** (depends on API):
   - Wait for API to be healthy
   - Wait for Redis to be healthy
   - Wait for PostgreSQL to be healthy

### Health Check Status

Check service health:
```bash
docker compose ps
```

Expected output should show all services as "healthy" or "running".

## Backend Startup

### Using Startup Script (Recommended)

```bash
cd apps/api
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

### Using Docker Compose

```bash
docker compose up -d api
```

### Manual Startup

```bash
cd apps/api
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

### Backend Endpoints

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health
- **Ready**: http://localhost:8000/ready
- **Live**: http://localhost:8000/live
- **Metrics**: http://localhost:8000/metrics

## Frontend Startup

### Using Startup Script

```bash
cd apps/web
npm install
npm run dev
```

### Manual Startup

```bash
cd apps/web
# Install dependencies
npm install

# Start development server
npm run dev
```

### Frontend Endpoints

- **Frontend**: http://localhost:3000
- **Sign In**: http://localhost:3000/sign-in
- **Sign Up**: http://localhost:3000/sign-up

## Database Migrations

### Run All Migrations

```bash
cd apps/api
alembic upgrade head
```

### Create New Migration

```bash
cd apps/api
alembic revision --autogenerate -m "description"
```

### Rollback One Migration

```bash
cd apps/api
alembic downgrade -1
```

### Rollback to Base

```bash
cd apps/api
alembic downgrade base
```

### View Migration History

```bash
cd apps/api
alembic history
```

### View Current Revision

```bash
cd apps/api
alembic current
```

## Database Bootstrap

### Bootstrap with Demo Data

```bash
cd apps/api
python scripts/bootstrap_local_env.py --seed
```

### Bootstrap Without Demo Data

```bash
cd apps/api
python scripts/bootstrap_local_env.py
```

### Seed Demo Data Separately

```bash
cd apps/api
python scripts/setup_demo_environment.py
```

## Environment Validation

### Validate Environment Configuration

```bash
cd apps/api
python scripts/validate_env.py
```

This validates:
- DATABASE_URL
- REDIS_URL
- Qdrant_URL
- S3 endpoint config
- Required environment variables

## Troubleshooting Guide

### Common Connectivity Issues

#### PostgreSQL Connection Refused

**Symptom**: `OSError: Connect call failed ('127.0.0.1', 5432)`

**Cause**: PostgreSQL container not running

**Solution**:
```bash
# Check if PostgreSQL is running
docker compose ps postgres

# Start PostgreSQL
docker compose up -d postgres

# Wait for PostgreSQL to be healthy
docker compose logs -f postgres
```

#### Redis Connection Refused

**Symptom**: `Error connecting to Redis`

**Cause**: Redis container not running

**Solution**:
```bash
# Check if Redis is running
docker compose ps redis

# Start Redis
docker compose up -d redis

# Test Redis connection
redis-cli ping
```

#### Qdrant Connection Refused

**Symptom**: `Error connecting to Qdrant`

**Cause**: Qdrant container not running

**Solution**:
```bash
# Check if Qdrant is running
docker compose ps qdrant

# Start Qdrant
docker compose up -d qdrant

# Test Qdrant connection
curl http://localhost:6333/healthz
```

#### MinIO Connection Refused

**Symptom**: `Error connecting to MinIO`

**Cause**: MinIO container not running

**Solution**:
```bash
# Check if MinIO is running
docker compose ps minio

# Start MinIO
docker compose up -d minio minio-init

# Test MinIO connection
curl http://localhost:9000/minio/health/live
```

### Port Conflicts

#### Port 5432 Already in Use

**Symptom**: PostgreSQL fails to start with port conflict

**Solution**:
```bash
# Check what's using port 5432
netstat -ano | findstr :5432  # Windows
lsof -i :5432  # Linux/Mac

# Option 1: Stop conflicting service
# Option 2: Change PostgreSQL port in docker-compose.yml
```

#### Port 8000 Already in Use

**Symptom**: Backend API fails to start with port conflict

**Solution**:
```bash
# Check what's using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# Option 1: Stop conflicting service
# Option 2: Change API port in .env
```

#### Port 3000 Already in Use

**Symptom**: Frontend fails to start with port conflict

**Solution**:
```bash
# Check what's using port 3000
netstat -ano | findstr :3000  # Windows
lsof -i :3000  # Linux/Mac

# Option 1: Stop conflicting service
# Option 2: Change frontend port
```

### Database Issues

#### Migration Failed

**Symptom**: Alembic migration fails

**Solution**:
```bash
# Check database connection
cd apps/api
python scripts/validate_env.py

# Check migration status
alembic current

# Reset database (WARNING: deletes data)
docker compose down -v
docker compose up -d postgres
alembic upgrade head
```

#### Database Schema Out of Sync

**Symptom**: Application errors due to schema mismatch

**Solution**:
```bash
# Check current migration
alembic current

# Run migrations
alembic upgrade head

# If still failing, reset database
docker compose down -v
docker compose up -d postgres
alembic upgrade head
```

### Docker Issues

#### Docker Daemon Not Running

**Symptom**: `Cannot connect to the Docker daemon`

**Solution**:
```bash
# Start Docker Desktop
# Or start Docker daemon (Linux)
sudo systemctl start docker
```

#### Out of Disk Space

**Symptom**: Docker fails to start containers

**Solution**:
```bash
# Check Docker disk usage
docker system df

# Clean up unused resources
docker system prune -a

# Remove specific volumes
docker volume rm $(docker volume ls -q)
```

#### Container Won't Start

**Symptom**: Container exits immediately

**Solution**:
```bash
# Check container logs
docker compose logs <service-name>

# Check container status
docker compose ps

# Restart container
docker compose restart <service-name>
```

### Application Issues

#### Import Error

**Symptom**: `ModuleNotFoundError`

**Solution**:
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
cd apps/api
pip install -r requirements.txt
```

#### Environment Variable Not Set

**Symptom**: Application fails due to missing environment variable

**Solution**:
```bash
# Validate environment
cd apps/api
python scripts/validate_env.py

# Check .env file exists
ls .env

# Copy example .env
cp .env.example .env
```

#### CORS Error

**Symptom**: Browser CORS error when accessing API

**Solution**:
```bash
# Check CORS configuration in .env
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Restart backend
```

## Service URLs

### Infrastructure Services

- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Qdrant**: http://localhost:6333
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **MinIO**: http://localhost:9000
- **MinIO Console**: http://localhost:9001
- **MLflow**: http://localhost:5000

### Application Services

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

### Observability Services

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **Loki**: http://localhost:3100

## Useful Commands

### View Logs

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f postgres
docker compose logs -f api
docker compose logs -f worker
```

### Execute Commands in Containers

```bash
# PostgreSQL
docker exec -it resume-intelligence-postgres-1 psql -U resume -d resume_ai

# Redis
docker exec -it resume-intelligence-redis-1 redis-cli

# Qdrant
docker exec -it resume-intelligence-qdrant-1 curl http://localhost:6333/healthz
```

### Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart api
docker compose restart postgres
```

### Rebuild Services

```bash
# Rebuild all services
docker compose up -d --build

# Rebuild specific service
docker compose up -d --build api
```

## Development Workflow

### Typical Development Session

1. **Start infrastructure**:
   ```bash
   docker compose up -d postgres redis qdrant minio mlflow
   ```

2. **Run migrations**:
   ```bash
   cd apps/api
   alembic upgrade head
   ```

3. **Start backend**:
   ```bash
   uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
   ```

4. **Start frontend** (new terminal):
   ```bash
   cd apps/web
   npm run dev
   ```

5. **Test application**:
   - Open http://localhost:3000
   - Sign up for account
   - Test features

6. **Stop services**:
   ```bash
   docker compose down
   ```

### Using Startup Script (Recommended)

```bash
# Start everything
.\scripts\dev-start.ps1 --frontend
```

## Next Steps

1. ✅ Developer experience documentation complete
2. ⏭️ STEP 8: Final local validation

## Conclusion

This guide provides a complete reference for local development, including infrastructure startup, application startup, migrations, and troubleshooting. Use the startup scripts for the best developer experience.
