#!/bin/bash
# Local Development Startup Script (Bash)
# PHASE 18 - STEP 2

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$PROJECT_ROOT/apps/api"
WEB_DIR="$PROJECT_ROOT/apps/web"
START_FRONTEND=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --frontend|-f)
            START_FRONTEND=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

echo -e "${CYAN}========================================"
echo -e "AI Resume Intelligence - Local Dev Startup"
echo -e "========================================${NC}"
echo ""

# Function to wait for service health
wait_for_service() {
    local name=$1
    local url=$2
    local max_wait=${3:-60}
    
    echo -e "${YELLOW}Waiting for $name to be healthy...${NC}"
    local elapsed=0
    local interval=2
    
    while [ $elapsed -lt $max_wait ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $name is healthy${NC}"
            return 0
        fi
        
        sleep $interval
        elapsed=$((elapsed + interval))
        echo -n "."
    done
    
    echo ""
    echo -e "${RED}✗ $name failed to become healthy within ${max_wait}s${NC}"
    return 1
}

# Function to validate PostgreSQL connectivity
test_postgresql() {
    echo -e "${YELLOW}Validating PostgreSQL connectivity...${NC}"
    if PGPASSWORD=resume psql -h localhost -U resume -d resume_ai -c "SELECT 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL connectivity validated${NC}"
        return 0
    else
        echo -e "${RED}✗ PostgreSQL connectivity failed${NC}"
        return 1
    fi
}

# Function to validate Redis connectivity
test_redis() {
    echo -e "${YELLOW}Validating Redis connectivity...${NC}"
    if redis-cli ping | grep -q "PONG"; then
        echo -e "${GREEN}✓ Redis connectivity validated${NC}"
        return 0
    else
        echo -e "${RED}✗ Redis connectivity failed${NC}"
        return 1
    fi
}

# Function to validate Qdrant connectivity
test_qdrant() {
    echo -e "${YELLOW}Validating Qdrant connectivity...${NC}"
    if curl -s -f http://localhost:6333/healthz > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Qdrant connectivity validated${NC}"
        return 0
    else
        echo -e "${RED}✗ Qdrant connectivity failed${NC}"
        return 1
    fi
}

# Step 1: Start infrastructure services
echo -e "${CYAN}Step 1: Starting infrastructure services...${NC}"
echo ""

cd "$PROJECT_ROOT"
docker compose up -d postgres redis qdrant minio mlflow

echo ""
echo -e "${YELLOW}Waiting for infrastructure services to start...${NC}"
sleep 5

# Step 2: Wait for services to be healthy
echo ""
echo -e "${CYAN}Step 2: Validating service health...${NC}"
echo ""

# PostgreSQL health check (special case - use docker exec)
echo -e "${YELLOW}Waiting for PostgreSQL to be healthy...${NC}"
elapsed=0
interval=2
max_wait=60
while [ $elapsed -lt $max_wait ]; do
    if docker exec resume-intelligence-postgres-1 pg_isready -U resume -d resume_ai > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL is healthy${NC}"
        break
    fi
    sleep $interval
    elapsed=$((elapsed + interval))
    echo -n "."
done

if [ $elapsed -ge $max_wait ]; then
    echo ""
    echo -e "${RED}✗ PostgreSQL failed to become healthy within ${max_wait}s${NC}"
    echo "Check logs with: docker compose logs postgres"
    exit 1
fi

# Redis health check
if ! wait_for_service "Redis" "http://localhost:6379" 30; then
    echo "Check logs with: docker compose logs redis"
    exit 1
fi

# Qdrant health check
if ! wait_for_service "Qdrant" "http://localhost:6333/healthz" 60; then
    echo "Check logs with: docker compose logs qdrant"
    exit 1
fi

# Step 3: Validate connectivity
echo ""
echo -e "${CYAN}Step 3: Validating connectivity...${NC}"
echo ""

if ! test_postgresql; then
    exit 1
fi

if ! test_redis; then
    exit 1
fi

if ! test_qdrant; then
    exit 1
fi

# Step 4: Run database migrations
echo ""
echo -e "${CYAN}Step 4: Running database migrations...${NC}"
echo ""

cd "$API_DIR"
alembic upgrade head

if [ $? -ne 0 ]; then
    echo -e "${RED}Database migrations failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Database migrations completed${NC}"

# Step 5: Start backend
echo ""
echo -e "${CYAN}Step 5: Starting backend API...${NC}"
echo ""

echo -e "${GREEN}Backend starting on http://localhost:8000${NC}"
echo -e "${GREEN}API Docs: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the backend${NC}"
echo ""

uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload

# Step 6: Start frontend (optional)
if [ "$START_FRONTEND" = true ]; then
    echo ""
    echo -e "${CYAN}Step 6: Starting frontend...${NC}"
    echo ""
    
    cd "$WEB_DIR"
    npm run dev
fi
