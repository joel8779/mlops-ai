# Import Graph Analysis - PHASE 22

## Import Failure Analysis

Based on startup forensics script execution, the following import failures were identified:

---

## Critical Import Failures

### 1. Observability Layer Imports

#### app.logging
- **Error**: `No module named 'structlog'`
- **Dependency**: structlog==24.4.0
- **Status**: Package not installed
- **Impact**: Logging configuration fails, app cannot start

#### app.observability.tracing
- **Error**: `No module named 'structlog'`
- **Dependency**: structlog==24.4.0
- **Status**: Package not installed
- **Impact**: OpenTelemetry tracing fails

#### app.middleware.request_context
- **Error**: `No module named 'structlog'`
- **Dependency**: structlog==24.4.0
- **Status**: Package not installed
- **Impact**: Request context middleware fails

### 2. Prometheus Instrumentation

#### app.main
- **Error**: `No module named 'prometheus_fastapi_instrumentator'`
- **Dependency**: prometheus-fastapi-instrumentator==7.0.0
- **Status**: Package not installed
- **Impact**: FastAPI app creation fails

### 3. Configuration Parsing

#### app.core.config
- **Error**: `error parsing value for field "backend_cors_origins" from source "DotEnvSettingsSource"`
- **Dependency**: pydantic-settings
- **Status**: Package installed, but .env file has malformed value
- **Impact**: Configuration loading fails

#### app.db.database
- **Error**: `error parsing value for field "backend_cors_origins" from source "DotEnvSettingsSource"`
- **Dependency**: pydantic-settings
- **Status**: Package installed, but .env file has malformed value
- **Impact**: Database initialization fails

#### app.api.v1.router
- **Error**: `error parsing value for field "backend_cors_origins" from source "DotEnvSettingsSource"`
- **Dependency**: pydantic-settings
- **Status**: Package installed, but .env file has malformed value
- **Impact**: Router registration fails

---

## Import Graph Structure

### Main Entry Point: app.main

```
app.main
├── app.api.v1.router
│   ├── app.api.v1.routes.health
│   ├── app.api.v1.routes.auth
│   ├── app.api.v1.routes.jobs
│   ├── app.api.v1.routes.ats
│   ├── app.api.v1.routes.ai
│   ├── app.api.v1.routes.analytics
│   ├── app.api.v1.routes.billing
│   ├── app.api.v1.routes.feedback
│   └── app.api.v1.routes.websocket
├── app.core.config
│   └── pydantic-settings
├── app.core.exceptions
│   └── fastapi
├── app.logging
│   └── structlog (MISSING)
├── app.db.database
│   ├── sqlalchemy
│   ├── asyncpg
│   └── pydantic-settings
├── app.middleware.request_context
│   └── structlog (MISSING)
├── app.middleware.security
│   └── fastapi
├── app.middleware.tenant
│   └── fastapi
├── app.observability.tracing
│   ├── opentelemetry-api (MISSING)
│   ├── opentelemetry-sdk (MISSING)
│   ├── opentelemetry-exporter-otlp (MISSING)
│   └── structlog (MISSING)
└── prometheus_fastapi_instrumentator (MISSING)
```

### Service Layer Dependencies

```
app.services.*
├── app.services.embedding_service
│   ├── sentence-transformers (MISSING)
│   ├── torch (MISSING)
│   └── qdrant-client
├── app.services.semantic_search_service
│   ├── sentence-transformers (MISSING)
│   ├── torch (MISSING)
│   └── qdrant-client
├── app.services.gemini_service
│   └── google-generativeai (MISSING)
├── app.services.ocr_service
│   ├── pytesseract (MISSING)
│   ├── Pillow (MISSING)
│   ├── pdfplumber (MISSING)
│   └── pymupdf (MISSING)
└── app.services.recommendation_engine
    ├── xgboost (MISSING)
    ├── scikit-learn (MISSING)
    ├── pandas (MISSING)
    └── numpy
```

### Agent Layer Dependencies

```
app.agents.*
├── app.agents.orchestrator.copilot_orchestrator
│   ├── google-generativeai (MISSING)
│   └── transformers (MISSING)
├── app.agents.recruiter_agent.agent
│   ├── google-generativeai (MISSING)
│   └── sentence-transformers (MISSING)
└── app.agents.reasoning.intent
    ├── transformers (MISSING)
    └── torch (MISSING)
```

---

## Circular Import Analysis

### No Circular Imports Detected
The import graph is acyclic. Dependencies flow in one direction:
- Main → Router → Routes → Services
- Main → Middleware
- Main → Core
- Services → ML/AI SDKs

---

## Lazy Import Failures

### Potential Lazy Import Issues
The following modules may use lazy imports that could fail at runtime:

1. **app.services.embedding_service**
   - Lazy imports: sentence-transformers, torch
   - Failure point: When embedding is first requested
   - Status: Will fail at runtime if ML layer not installed

2. **app.services.gemini_service**
   - Lazy imports: google-generativeai
   - Failure point: When Gemini API is first called
   - Status: Will fail at runtime if AI layer not installed

3. **app.services.ocr_service**
   - Lazy imports: pytesseract, Pillow, pdfplumber, pymupdf
   - Failure point: When OCR is first requested
   - Status: Will fail at runtime if ML layer not installed

---

## Import-Time Side Effects

### app.main
- **Side effect**: Calls `configure_logging()` at module level
- **Impact**: Fails immediately if structlog is missing
- **Status**: BLOCKS startup

### app.core.config
- **Side effect**: Loads environment variables at module level
- **Impact**: Fails if .env has malformed values
- **Status**: BLOCKS startup

### app.observability.tracing
- **Side effect**: Configures OpenTelemetry at module level
- **Impact**: Fails if opentelemetry packages are missing
- **Status**: BLOCKS startup

---

## Stale Module Paths

### No Stale Module Paths Detected
All module paths are correct and aligned with the package structure.

---

## Broken Package Initialization

### grpcio
- **Issue**: grpcio-status and grpcio-tools are installed, but grpcio is missing
- **Impact**: Any code using grpcio will fail
- **Status**: BROKEN DEPENDENCY STATE
- **Resolution**: Reinstall grpcio==1.76.0

---

## Shadowed Packages

### No Shadowed Packages Detected
No packages are shadowed by local modules or conflicting installations.

---

## Recursive Module Chains

### No Excessive Recursion Detected
Import depth is reasonable (< 10 levels). No infinite recursion detected.

---

## Import Order Dependencies

### Critical Import Order
The following imports must occur in this order:

1. **app.core.config** (must be first - loads settings)
2. **app.logging** (depends on config)
3. **app.observability.tracing** (depends on logging)
4. **app.db.database** (depends on config)
5. **app.main** (depends on all above)

### Current State
app.main follows the correct import order. No issues detected.

---

## Root Cause Summary

### Primary Import Failures
1. **Missing structlog** - Blocks logging, middleware, tracing
2. **Missing prometheus_fastapi_instrumentator** - Blocks app creation
3. **Missing opentelemetry packages** - Blocks tracing
4. **Malformed backend_cors_origins** - Blocks configuration loading
5. **Missing ML packages** - Will block service layer at runtime
6. **Missing AI packages** - Will block agent layer at runtime
7. **Broken grpcio installation** - Will block GRPC functionality

### Secondary Import Issues
1. **Lazy import failures** - Will fail at runtime when services are called
2. **Missing OCR packages** - Will fail when OCR is requested

---

## Remediation Priority

### Critical (Blocks Startup)
1. Install structlog (observability layer)
2. Install prometheus packages (observability layer)
3. Install opentelemetry packages (observability layer)
4. Fix backend_cors_origins in .env
5. Fix grpcio installation

### High (Blocks Features)
1. Install google-generativeai (AI layer)
2. Install sentence-transformers (ML layer)
3. Install torch (ML layer)
4. Install transformers (ML layer)

### Medium (Blocks Specific Features)
1. Install OCR packages (ML layer)
2. Install remaining ML packages (pandas, scikit-learn, xgboost, etc.)
