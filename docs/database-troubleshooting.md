# Database Troubleshooting Guide - PHASE 19

**Date**: 2026-05-23
**Phase**: STEP 7 - LOCAL TROUBLESHOOTING GUIDE

## Overview

This guide covers common issues encountered when running the AI Resume Intelligence Platform locally, with a focus on database and infrastructure problems.

## Docker Startup Issues

### Docker Daemon Not Running

**Symptom**: `Cannot connect to the Docker daemon`

**Solution**:
```bash
# Windows: Start Docker Desktop
# Linux: Start Docker daemon
sudo systemctl start docker

# Verify Docker is running
docker ps
```

### Container Won't Start

**Symptom**: Container exits immediately after starting

**Solution**:
```bash
# Check container logs
docker compose logs <service-name>

# Check container status
docker compose ps

# Restart container
docker compose restart <service-name>

# Rebuild container
docker compose up -d --build <service-name>
```

### Out of Disk Space

**Symptom**: Docker fails to start containers due to disk space

**Solution**:
```bash
# Check Docker disk usage
docker system df

# Clean up unused resources
docker system prune -a

# Remove specific volumes
docker volume rm $(docker volume ls -q)

# Remove all volumes (WARNING: deletes data)
docker compose down -v
```

## Port Conflicts

### Port 5432 Already in Use

**Symptom**: PostgreSQL fails to start with port conflict

**Solution**:
```bash
# Windows: Check what's using port 5432
netstat -ano | findstr :5432

# Linux/Mac: Check what's using port 5432
lsof -i :5432

# Option 1: Stop conflicting service
# Option 2: Change PostgreSQL port in docker-compose.yml
# Option 3: Stop existing PostgreSQL instance
```

### Port 8000 Already in Use

**Symptom**: Backend API fails to start with port conflict

**Solution**:
```bash
# Windows: Check what's using port 8000
netstat -ano | findstr :8000

# Linux/Mac: Check what's using port 8000
lsof -i :8000

# Option 1: Stop conflicting service
# Option 2: Change API port in .env
# Option 3: Use different port for uvicorn
```

### Port 3000 Already in Use

**Symptom**: Frontend fails to start with port conflict

**Solution**:
```bash
# Windows: Check what's using port 3000
netstat -ano | findstr :3000

# Linux/Mac: Check what's using port 3000
lsof -i :3000

# Option 1: Stop conflicting service
# Option 2: Change frontend port
```

## PostgreSQL Connection Issues

### Connection Refused

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

# Test connection
PGPASSWORD=resume psql -h localhost -U resume -d resume_ai -c "SELECT 1"
```

### Authentication Failed

**Symptom**: `FATAL: password authentication failed for user "resume"`

**Cause**: Credentials mismatch between docker-compose and .env

**Solution**:
```bash
# Check docker-compose.yml credentials
cat docker-compose.yml | grep -A 3 "postgres:"

# Check .env credentials
cat .env | grep POSTGRES

# Ensure they match
# POSTGRES_USER=resume
# POSTGRES_PASSWORD=resume
# POSTGRES_DB=resume_ai
```

### Database Does Not Exist

**Symptom**: `FATAL: database "resume_ai" does not exist`

**Cause**: Database not created

**Solution**:
```bash
# Connect to PostgreSQL
docker exec -it resume-intelligence-postgres-1 psql -U resume -d postgres

# Create database
CREATE DATABASE resume_ai;

# Exit
\q
```

## Migration Failures

### Migration Failed

**Symptom**: Alembic migration fails with error

**Solution**:
```bash
# Check database connection
cd apps/api
python scripts/validate_env.py

# Check current migration
alembic current

# Reset database (WARNING: deletes data)
docker compose down -v
docker compose up -d postgres
alembic upgrade head
```

### Schema Out of Sync

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

### Migration History Conflicts

**Symptom**: Alembic detects migration conflicts

**Solution**:
```bash
# View migration history
alembic history

# Stamp current state
alembic stamp head

# Create new migration
alembic revision --autogenerate -m "description"
```

## Container Inspection Commands

### View Container Logs

```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs postgres
docker compose logs redis
docker compose logs qdrant
docker compose logs api

# Follow logs in real-time
docker compose logs -f postgres
```

### Execute Commands in Containers

```bash
# PostgreSQL
docker exec -it resume-intelligence-postgres-1 psql -U resume -d resume_ai

# Redis
docker exec -it resume-intelligence-redis-1 redis-cli

# Qdrant
docker exec -it resume-intelligence-qdrant-1 curl http://localhost:6333/healthz

# MinIO
docker exec -it resume-intelligence-minio-1 mc ready local
```

### Inspect Container Status

```bash
# View all containers
docker compose ps

# View detailed container info
docker inspect resume-intelligence-postgres-1

# View container resource usage
docker stats
```

### Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart postgres
docker compose restart api
```

### Rebuild Services

```bash
# Rebuild all services
docker compose up -d --build

# Rebuild specific service
docker compose up -d --build api
```

## Windows-Specific Docker Notes

### Docker Desktop Not Starting

**Symptom**: Docker Desktop fails to start on Windows

**Solution**:
1. Check Windows Subsystem for Linux (WSL) is enabled
2. Check Hyper-V is enabled
3. Restart Docker Desktop
4. Check Docker Desktop logs

### WSL2 Issues

**Symptom**: Docker containers fail to start with WSL2 errors

**Solution**:
```bash
# Restart WSL
wsl --shutdown

# Restart Docker Desktop
```

### Path Mapping Issues

**Symptom**: Volume mounts fail on Windows

**Solution**:
1. Ensure Docker Desktop has access to the project directory
2. Check Docker Desktop settings > Resources > File sharing
3. Add project directory to shared directories

### Performance Issues

**Symptom**: Docker containers are slow on Windows

**Solution**:
1. Increase Docker Desktop memory allocation (recommended: 8GB+)
2. Enable WSL2 backend
3. Use Linux containers instead of Windows containers

## Common Issues and Solutions

### Issue: Backend Fails to Start with PostgreSQL Error

**Symptom**: `OSError: Connect call failed ('127.0.0.1', 5432)`

**Solution**:
```bash
# Start infrastructure first
docker compose up -d postgres redis qdrant minio mlflow

# Wait for services to be healthy
docker compose ps

# Run migrations
cd apps/api
alembic upgrade head

# Start backend
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

### Issue: Authentication Requests Fail

**Symptom**: Login endpoint returns 500 error

**Solution**:
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Check database connection
curl http://localhost:8000/api/v1/health/ready

# Check backend logs
docker compose logs api

# Restart backend
docker compose restart api
```

### Issue: Redis Connection Refused

**Symptom**: `Error connecting to Redis`

**Solution**:
```bash
# Check Redis is running
docker compose ps redis

# Test Redis connection
redis-cli ping

# Start Redis
docker compose up -d redis
```

### Issue: Qdrant Connection Refused

**Symptom**: `Error connecting to Qdrant`

**Solution**:
```bash
# Check Qdrant is running
docker compose ps qdrant

# Test Qdrant connection
curl http://localhost:6333/healthz

# Start Qdrant
docker compose up -d qdrant
```

## Using Troubleshooting Scripts

### Validate Infrastructure

```bash
cd c:\Users\Lenovo\Desktop\mlops-ai
python scripts/validate_local_infra.py
```

This script validates:
- Docker daemon is running
- PostgreSQL container is running
- PostgreSQL connectivity
- Redis container is running
- Redis connectivity
- Qdrant container is running
- Qdrant connectivity
- MinIO container is running
- MinIO connectivity

### Bootstrap Database

```bash
cd c:\Users\Lenovo\Desktop\mlops-ai
.\scripts\bootstrap_database.ps1  # Windows
./scripts/bootstrap_database.sh  # Linux/Mac
```

This script:
- Starts PostgreSQL
- Waits for readiness
- Creates database if missing
- Runs Alembic migrations
- Validates schema health
- Seeds demo data (optional)

### Start Development Environment

```bash
cd c:\Users\Lenovo\Desktop\mlops-ai
.\scripts\dev-up.ps1  # Windows
./scripts/dev-up.sh  # Linux/Mac
```

This script:
- Starts infrastructure services
- Validates service health
- Validates connectivity
- Runs migrations
- Starts backend
- Optionally starts frontend

## Quick Reference

### Start Everything
```bash
docker compose up -d
```

### Stop Everything
```bash
docker compose down
```

### Stop and Remove Data
```bash
docker compose down -v
```

### View Logs
```bash
docker compose logs -f
```

### Restart Service
```bash
docker compose restart <service>
```

### Rebuild Service
```bash
docker compose up -d --build <service>
```

### Execute in Container
```bash
docker exec -it <container> <command>
```

## Next Steps

1. ✅ Local troubleshooting guide complete
2. ⏭️ STEP 8: Final validation

## Conclusion

This guide provides comprehensive troubleshooting for common local development issues. Use the validation and bootstrap scripts for automated infrastructure checks and database setup.
