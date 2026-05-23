# Local Development Startup Script (PowerShell)
# PHASE 19 - STEP 5

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Resume Intelligence - Local Dev Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$API_DIR = Join-Path $PROJECT_ROOT "apps\api"
$WEB_DIR = Join-Path $PROJECT_ROOT "apps\web"
$START_FRONTEND = $false

# Parse arguments
foreach ($arg in $args) {
    if ($arg -eq "--frontend" -or $arg -eq "-f") {
        $START_FRONTEND = $true
    }
}

# Function to wait for service health
function Wait-ForService {
    param(
        [string]$Name,
        [string]$Url,
        [int]$MaxWaitSeconds = 60
    )
    
    Write-Host "Waiting for $Name to be healthy..." -ForegroundColor Yellow
    $elapsed = 0
    $interval = 2
    
    while ($elapsed -lt $MaxWaitSeconds) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✓ $Name is healthy" -ForegroundColor Green
                return $true
            }
        } catch {
            # Service not ready yet
        }
        
        Start-Sleep -Seconds $interval
        $elapsed += $interval
        Write-Host "." -NoNewline
    }
    
    Write-Host ""
    Write-Host "✗ $Name failed to become healthy within ${MaxWaitSeconds}s" -ForegroundColor Red
    return $false
}

# Function to validate PostgreSQL connectivity
function Test-PostgreSQL {
    Write-Host "Validating PostgreSQL connectivity..." -ForegroundColor Yellow
    try {
        $env:PGPASSWORD = "resume"
        $result = psql -h localhost -U resume -d resume_ai -c "SELECT 1" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ PostgreSQL connectivity validated" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ PostgreSQL connectivity failed" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ PostgreSQL connectivity test failed: $_" -ForegroundColor Red
        return $false
    }
}

# Function to validate Redis connectivity
function Test-Redis {
    Write-Host "Validating Redis connectivity..." -ForegroundColor Yellow
    try {
        $result = redis-cli ping 2>&1
        if ($result -eq "PONG") {
            Write-Host "✓ Redis connectivity validated" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ Redis connectivity failed" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ Redis connectivity test failed: $_" -ForegroundColor Red
        return $false
    }
}

# Function to validate Qdrant connectivity
function Test-Qdrant {
    Write-Host "Validating Qdrant connectivity..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:6333/healthz" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Qdrant connectivity validated" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ Qdrant connectivity failed" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ Qdrant connectivity test failed: $_" -ForegroundColor Red
        return $false
    }
}

# Step 1: Start infrastructure services
Write-Host "Step 1: Starting infrastructure services..." -ForegroundColor Cyan
Write-Host ""

Set-Location $PROJECT_ROOT
docker compose up -d postgres redis qdrant minio mlflow

Write-Host ""
Write-Host "Waiting for infrastructure services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 2: Wait for services to be healthy
Write-Host ""
Write-Host "Step 2: Validating service health..." -ForegroundColor Cyan
Write-Host ""

# PostgreSQL health check (special case - use docker exec)
Write-Host "Waiting for PostgreSQL to be healthy..." -ForegroundColor Yellow
$elapsed = 0
$interval = 2
$max_wait = 60
while ($elapsed -lt $max_wait) {
    $result = docker exec resume-intelligence-postgres-1 pg_isready -U resume -d resume_ai 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PostgreSQL is healthy" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds $interval
    $elapsed += $interval
    Write-Host "." -NoNewline
}

if ($elapsed -ge $max_wait) {
    Write-Host ""
    Write-Host "✗ PostgreSQL failed to become healthy within ${max_wait}s" -ForegroundColor Red
    Write-Host "Check logs with: docker compose logs postgres" -ForegroundColor Red
    exit 1
}

# Redis health check
if (-not (Wait-ForService -Name "Redis" -Url "http://localhost:6379" -MaxWaitSeconds 30)) {
    Write-Host "Check logs with: docker compose logs redis" -ForegroundColor Red
    exit 1
}

# Qdrant health check
if (-not (Wait-ForService -Name "Qdrant" -Url "http://localhost:6333/healthz" -MaxWaitSeconds 60)) {
    Write-Host "Check logs with: docker compose logs qdrant" -ForegroundColor Red
    exit 1
}

# Step 3: Validate connectivity
Write-Host ""
Write-Host "Step 3: Validating connectivity..." -ForegroundColor Cyan
Write-Host ""

$pgConnected = Test-PostgreSQL
if (-not $pgConnected) {
    Write-Host "PostgreSQL connectivity validation failed" -ForegroundColor Red
    exit 1
}

$redisConnected = Test-Redis
if (-not $redisConnected) {
    Write-Host "Redis connectivity validation failed" -ForegroundColor Red
    exit 1
}

$qdrantConnected = Test-Qdrant
if (-not $qdrantConnected) {
    Write-Host "Qdrant connectivity validation failed" -ForegroundColor Red
    exit 1
}

# Step 4: Run database migrations
Write-Host ""
Write-Host "Step 4: Running database migrations..." -ForegroundColor Cyan
Write-Host ""

Set-Location $API_DIR
alembic upgrade head

if ($LASTEXITCODE -ne 0) {
    Write-Host "Database migrations failed" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Database migrations completed" -ForegroundColor Green

# Step 5: Start backend
Write-Host ""
Write-Host "Step 5: Starting backend API..." -ForegroundColor Cyan
Write-Host ""

Write-Host "Backend starting on http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the backend" -ForegroundColor Yellow
Write-Host ""

uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload

# Step 6: Start frontend (optional)
if ($START_FRONTEND) {
    Write-Host ""
    Write-Host "Step 6: Starting frontend..." -ForegroundColor Cyan
    Write-Host ""
    
    Set-Location $WEB_DIR
    npm run dev
}
