# Database Bootstrap Script (PowerShell)
# PHASE 19 - STEP 4

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Database Bootstrap" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$API_DIR = Join-Path $PROJECT_ROOT "apps\api"
$SEED_DEMO = $false

# Parse arguments
foreach ($arg in $args) {
    if ($arg -eq "--seed" -or $arg -eq "-s") {
        $SEED_DEMO = $true
    }
}

# Function to wait for PostgreSQL
function Wait-ForPostgreSQL {
    param([int]$MaxWaitSeconds = 60)
    
    Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
    $elapsed = 0
    $interval = 2
    
    while ($elapsed -lt $MaxWaitSeconds) {
        try {
            $env:PGPASSWORD = "resume"
            $result = psql -h localhost -U resume -d resume_ai -c "SELECT 1" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ PostgreSQL is ready" -ForegroundColor Green
                return $true
            }
        } catch {
            # Not ready yet
        }
        
        Start-Sleep -Seconds $interval
        $elapsed += $interval
        Write-Host "." -NoNewline
    }
    
    Write-Host ""
    Write-Host "✗ PostgreSQL failed to become ready within ${MaxWaitSeconds}s" -ForegroundColor Red
    return $false
}

# Step 1: Start PostgreSQL
Write-Host "Step 1: Starting PostgreSQL..." -ForegroundColor Cyan
Write-Host ""

Set-Location $PROJECT_ROOT
docker compose up -d postgres

Write-Host ""
Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 2: Wait for PostgreSQL readiness
Write-Host ""
Write-Host "Step 2: Waiting for PostgreSQL readiness..." -ForegroundColor Cyan
Write-Host ""

if (-not (Wait-ForPostgreSQL)) {
    Write-Host "PostgreSQL readiness check failed. Check logs with: docker compose logs postgres" -ForegroundColor Red
    exit 1
}

# Step 3: Create database if missing
Write-Host ""
Write-Host "Step 3: Validating database exists..." -ForegroundColor Cyan
Write-Host ""

$env:PGPASSWORD = "resume"
$result = psql -h localhost -U resume -d postgres -c "SELECT 1 FROM pg_database WHERE datname='resume_ai'" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Database 'resume_ai' does not exist. Creating..." -ForegroundColor Yellow
    psql -h localhost -U resume -d postgres -c "CREATE DATABASE resume_ai" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Database 'resume_ai' created" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create database" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ Database 'resume_ai' exists" -ForegroundColor Green
}

# Step 4: Run Alembic migrations
Write-Host ""
Write-Host "Step 4: Running Alembic migrations..." -ForegroundColor Cyan
Write-Host ""

Set-Location $API_DIR
alembic upgrade head

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Alembic migrations failed" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Alembic migrations completed" -ForegroundColor Green

# Step 5: Validate schema health
Write-Host ""
Write-Host "Step 5: Validating schema health..." -ForegroundColor Cyan
Write-Host ""

$env:PGPASSWORD = "resume"
$result = psql -h localhost -U resume -d resume_ai -c "\dt" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Schema is healthy" -ForegroundColor Green
} else {
    Write-Host "✗ Schema validation failed" -ForegroundColor Red
    exit 1
}

# Step 6: Seed demo data (optional)
if ($SEED_DEMO) {
    Write-Host ""
    Write-Host "Step 6: Seeding demo data..." -ForegroundColor Cyan
    Write-Host ""
    
    python scripts/setup_demo_environment.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Demo data seeded successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠ Demo data seeding failed (non-critical)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Database bootstrap completed successfully" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now start the backend with:" -ForegroundColor Green
Write-Host "  cd apps/api" -ForegroundColor Green
Write-Host "  uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload" -ForegroundColor Green
Write-Host ""
