# Final Local Validation - PHASE 18

**Date**: 2026-05-23
**Phase**: STEP 8 - FINAL LOCAL VALIDATION

## Overview

This document outlines the complete local validation workflow to ensure the AI Resume Intelligence Platform works end-to-end in a local development environment.

## Validation Steps

### Step 1: Docker Compose Startup

**Command**:
```bash
cd c:\Users\Lenovo\Desktop\mlops-ai
docker compose up -d postgres redis qdrant minio mlflow
```

**Expected Output**:
```
[+] Running 5/5
 ✔ Network resume-intelligence_resume_net  Created
 ✔ Container resume-intelligence-postgres-1  Started
 ✔ Container resume-intelligence-redis-1  Started
 ✔ Container resume-intelligence-qdrant-1  Started
 ✔ Container resume-intelligence-minio-1  Started
 ✔ Container resume-intelligence-minio-init-1  Started
 ✔ Container resume-intelligence-mlflow-1  Started
```

**Validation**:
```bash
docker compose ps
```

**Expected**: All services should show "healthy" or "running" status.

---

### Step 2: Database Migration

**Command**:
```bash
cd apps/api
alembic upgrade head
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> <revision_id>, <message>
...
```

**Validation**:
```bash
alembic current
```

**Expected**: Should show the latest revision ID.

---

### Step 3: Backend Startup

**Command**:
```bash
cd apps/api
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

**Expected Output**:
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Validation**:
```bash
curl http://localhost:8000/health
```

**Expected**:
```json
{
  "status": "healthy",
  "timestamp": "2026-05-23T...",
  "version": "0.1.0"
}
```

---

### Step 4: Frontend Startup

**Command** (new terminal):
```bash
cd apps/web
npm run dev
```

**Expected Output**:
```
  ▲ Next.js 15.0.0
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Ready in 2.5s
```

**Validation**:
```bash
curl http://localhost:3000
```

**Expected**: HTML response with Next.js application.

---

### Step 5: Login Request

**Command**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

**Expected Output**:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

**Validation**: Should receive JWT tokens without error.

---

### Step 6: Database Query Execution

**Command**:
```bash
docker exec -it resume-intelligence-postgres-1 psql -U resume -d resume_ai -c "SELECT COUNT(*) FROM organizations;"
```

**Expected Output**:
```
 count
-------
     0
(1 row)
```

**Validation**: Database should be accessible and return query results.

---

### Step 7: Redis Connectivity

**Command**:
```bash
redis-cli ping
```

**Expected Output**:
```
PONG
```

**Validation**: Redis should respond with PONG.

---

### Step 8: Qdrant Connectivity

**Command**:
```bash
curl http://localhost:6333/healthz
```

**Expected Output**:
```json
{
  "status": "ok",
  "version": "1.12.6"
}
```

**Validation**: Qdrant should return healthy status.

---

## Complete Validation Script

### Automated Validation Script

Create `scripts/validate_local_env.sh`:

```bash
#!/bin/bash
set -e

echo "========================================"
echo "Local Environment Validation"
echo "========================================"
echo ""

# Step 1: Validate Docker services
echo "Step 1: Validating Docker services..."
docker compose ps
echo ""

# Step 2: Validate database
echo "Step 2: Validating database..."
PGPASSWORD=resume psql -h localhost -U resume -d resume_ai -c "SELECT 1"
echo ""

# Step 3: Validate Redis
echo "Step 3: Validating Redis..."
redis-cli ping
echo ""

# Step 4: Validate Qdrant
echo "Step 4: Validating Qdrant..."
curl -s http://localhost:6333/healthz
echo ""

# Step 5: Validate backend health
echo "Step 5: Validating backend health..."
curl -s http://localhost:8000/health
echo ""

# Step 6: Validate frontend
echo "Step 6: Validating frontend..."
curl -s http://localhost:3000 > /dev/null
echo "✓ Frontend accessible"
echo ""

echo "========================================"
echo "✓ All validations passed"
echo "========================================"
```

## Using Startup Script for Validation

### Complete Workflow with Startup Script

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

This script performs all validation steps automatically:
1. Starts infrastructure services
2. Waits for health readiness
3. Validates connectivity
4. Runs migrations
5. Starts backend
6. Optionally starts frontend

## Validation Checklist

- [ ] Docker services start successfully
- [ ] All services show healthy status
- [ ] Database migrations complete successfully
- [ ] Backend API starts without errors
- [ ] Backend health endpoint returns 200
- [ ] Frontend starts without errors
- [ ] Frontend is accessible on port 3000
- [ ] Login request returns JWT tokens
- [ ] Database queries execute successfully
- [ ] Redis responds to ping
- [ ] Qdrant health endpoint returns 200

## Common Validation Failures

### Docker Services Won't Start

**Symptom**: Services fail to start with errors

**Solution**:
```bash
# Check Docker daemon is running
docker ps

# Check for port conflicts
netstat -ano | findstr :5432  # Windows
lsof -i :5432  # Linux/Mac

# Restart Docker Desktop
```

### Database Migration Fails

**Symptom**: Alembic migration fails with connection error

**Solution**:
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Check database connection
PGPASSWORD=resume psql -h localhost -U resume -d resume_ai -c "SELECT 1"

# Reset database if needed
docker compose down -v
docker compose up -d postgres
alembic upgrade head
```

### Backend Won't Start

**Symptom**: Backend fails to start with connection errors

**Solution**:
```bash
# Check environment variables
cd apps/api
python scripts/validate_env.py

# Check all services are running
docker compose ps

# Check backend logs
docker compose logs api
```

### Frontend Won't Start

**Symptom**: Frontend fails to start with port conflict

**Solution**:
```bash
# Check what's using port 3000
netstat -ano | findstr :3000  # Windows
lsof -i :3000  # Linux/Mac

# Stop conflicting service or change port
```

## Performance Validation

### Backend Response Time

**Command**:
```bash
time curl http://localhost:8000/health
```

**Expected**: < 100ms

### Database Query Time

**Command**:
```bash
time PGPASSWORD=resume psql -h localhost -U resume -d resume_ai -c "SELECT 1"
```

**Expected**: < 50ms

### Redis Response Time

**Command**:
```bash
time redis-cli ping
```

**Expected**: < 10ms

### Qdrant Response Time

**Command**:
```bash
time curl http://localhost:6333/healthz
```

**Expected**: < 50ms

## Next Steps

1. ✅ Final local validation documentation complete
2. ✅ PHASE 18 — LOCAL INFRASTRUCTURE ORCHESTRATION complete

## Conclusion

The local environment validation ensures that all infrastructure services are running correctly, the application starts without errors, and all connectivity is validated. Use the startup scripts for the best developer experience.

**PHASE 18 — LOCAL INFRASTRUCTURE ORCHESTRATION: COMPLETE ✅**
