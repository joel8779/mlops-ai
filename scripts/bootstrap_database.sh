#!/bin/bash
# Database Bootstrap Script (Bash)
# PHASE 19 - STEP 4

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
SEED_DEMO=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --seed|-s)
            SEED_DEMO=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

echo -e "${CYAN}========================================"
echo -e "Database Bootstrap"
echo -e "========================================${NC}"
echo ""

# Function to wait for PostgreSQL
wait_for_postgresql() {
    local max_wait=${1:-60}
    
    echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
    local elapsed=0
    local interval=2
    
    while [ $elapsed -lt $max_wait ]; do
        if PGPASSWORD=resume psql -h localhost -U resume -d resume_ai -c "SELECT 1" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
            return 0
        fi
        
        sleep $interval
        elapsed=$((elapsed + interval))
        echo -n "."
    done
    
    echo ""
    echo -e "${RED}✗ PostgreSQL failed to become ready within ${max_wait}s${NC}"
    return 1
}

# Step 1: Start PostgreSQL
echo -e "${CYAN}Step 1: Starting PostgreSQL...${NC}"
echo ""

cd "$PROJECT_ROOT"
docker compose up -d postgres

echo ""
echo -e "${YELLOW}Waiting for PostgreSQL to start...${NC}"
sleep 5

# Step 2: Wait for PostgreSQL readiness
echo ""
echo -e "${CYAN}Step 2: Waiting for PostgreSQL readiness...${NC}"
echo ""

if ! wait_for_postgresql; then
    echo -e "${RED}PostgreSQL readiness check failed. Check logs with: docker compose logs postgres${NC}"
    exit 1
fi

# Step 3: Create database if missing
echo ""
echo -e "${CYAN}Step 3: Validating database exists...${NC}"
echo ""

DB_EXISTS=$(PGPASSWORD=resume psql -h localhost -U resume -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='resume_ai'" 2>/dev/null || echo "")

if [ -z "$DB_EXISTS" ]; then
    echo -e "${YELLOW}Database 'resume_ai' does not exist. Creating...${NC}"
    PGPASSWORD=resume psql -h localhost -U resume -d postgres -c "CREATE DATABASE resume_ai"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Database 'resume_ai' created${NC}"
    else
        echo -e "${RED}✗ Failed to create database${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Database 'resume_ai' exists${NC}"
fi

# Step 4: Run Alembic migrations
echo ""
echo -e "${CYAN}Step 4: Running Alembic migrations...${NC}"
echo ""

cd "$API_DIR"
alembic upgrade head

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Alembic migrations failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Alembic migrations completed${NC}"

# Step 5: Validate schema health
echo ""
echo -e "${CYAN}Step 5: Validating schema health...${NC}"
echo ""

PGPASSWORD=resume psql -h localhost -U resume -d resume_ai -c "\dt" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Schema is healthy${NC}"
else
    echo -e "${RED}✗ Schema validation failed${NC}"
    exit 1
fi

# Step 6: Seed demo data (optional)
if [ "$SEED_DEMO" = true ]; then
    echo ""
    echo -e "${CYAN}Step 6: Seeding demo data...${NC}"
    echo ""
    
    python scripts/setup_demo_environment.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Demo data seeded successfully${NC}"
    else
        echo -e "${YELLOW}⚠ Demo data seeding failed (non-critical)${NC}"
    fi
fi

echo ""
echo -e "${CYAN}========================================"
echo -e "✓ Database bootstrap completed successfully"
echo -e "========================================${NC}"
echo ""
echo -e "${GREEN}You can now start the backend with:${NC}"
echo -e "${GREEN}  cd apps/api${NC}"
echo -e "${GREEN}  uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload${NC}"
echo ""
