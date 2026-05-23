# Import + Module Consistency Audit - PHASE 20

**Date**: 2026-05-23
**Phase**: STEP 4 - IMPORT + MODULE CONSISTENCY AUDIT

## Overview

This document audits ALL backend imports to identify invalid imports, stale module paths, renamed exports, circular dependencies, and inconsistent naming.

## Session Module

**File**: `app/db/session.py`

**Status**: FIXED - Compatibility aliases added in PHASE 19

**Exports**:
- engine (original)
- AsyncSessionLocal (original)
- async_engine (compatibility alias)
- async_session_maker (compatibility alias)
- get_db (function)

**Importers**:
- app/db/database.py: `from app.db.session import engine`
- app/api/v1/routes/health.py: `from app.db.session import async_session_maker, async_engine`
- app/workers/job_tasks.py: `from app.db.session import AsyncSessionLocal`
- app/tasks/resume_tasks.py: `from app.db.session import AsyncSessionLocal`

**Consistency**: GOOD - All imports use correct names

---

## Logging Module

**File**: `app/logging/__init__.py`

**Exports**:
- bind_log_context
- clear_log_context
- configure_logging
- get_logger

**Importers**:
- app/main.py: `from app.logging import configure_logging, get_logger`
- app/workers/resume_tasks.py: `from app.logging import configure_logging, get_logger`
- app/workers/job_tasks.py: `from app.logging import configure_logging, get_logger`
- app/workers/celery_app.py: `from app.logging import configure_logging`
- app/tasks/celery_app.py: `from app.logging import configure_logging`

**Consistency**: GOOD - All imports use correct names

---

## Observability Tracing Module

**File**: `app/observability/tracing/__init__.py`

**Exports**:
- CorrelationContext
- bind_correlation
- configure_tracing
- current_trace_context
- enrich_span
- get_tracer
- instrument_celery
- traced_span
- shutdown_tracing

**Importers**:
- app/main.py: `from app.observability.tracing import configure_tracing, shutdown_tracing`
- app/services/embedding_service.py: `from app.observability.tracing import get_tracer`

**Consistency**: GOOD - All imports use correct names

---

## Embedding Service

**File**: `app/services/embedding_service.py`

**Imports**:
- from sentence_transformers import SentenceTransformer (MISSING DEPENDENCY)
- from qdrant_client import QdrantClient
- from qdrant_client.http.models import ...

**Status**: BROKEN - sentence_transformers not installed

**Importers**:
- app/services/semantic_search_service.py: `from app.services.embedding_service import EmbeddingService`
- app/services/retrieval/hybrid_retriever.py: `from app.services.embedding_service import EmbeddingService`
- app/workers/resume_tasks.py: `from app.services.embedding_service import EmbeddingService`

**Consistency**: GOOD - Module path is correct, but dependency missing

---

## Semantic Search Service

**File**: `app/services/semantic_search_service.py`

**Imports**:
- from app.services.embedding_service import EmbeddingService

**Status**: BROKEN - Depends on embedding_service which has missing dependency

**Consistency**: GOOD - Module path is correct

---

## Celery App

**Files**:
- app/workers/celery_app.py
- app/tasks/celery_app.py

**Imports**:
- from celery import Celery

**Status**: HEALTHY

**Consistency**: GOOD

---

## Gemini Provider

**File**: `app/services/llm/providers/gemini_provider.py`

**Imports**:
- import google.generativeai as genai

**Status**: HEALTHY

**Consistency**: GOOD

---

## Summary of Import Issues

### Critical Issues
1. sentence_transformers imported but not installed (blocks embedding service)

### High Issues
1. None

### Medium Issues
1. None

### Low Issues
1. None

---

## Circular Dependency Analysis

No circular dependencies detected in the import graph.

---

## Recommendations

### Immediate Actions
1. Install sentence-transformers to fix embedding service

### Short-term Actions
1. Implement graceful degradation for optional ML dependencies
2. Add try/except blocks around ML imports to allow backend to start without them

### Long-term Actions
1. Create feature flags for ML features
2. Implement optional dependency loading

---

## Next Steps

1. ✅ STEP 1: Full backend forensic audit (COMPLETE)
2. ✅ STEP 2: Python runtime stabilization (COMPLETE)
3. ✅ STEP 3: Dependency graph reconstruction (COMPLETE)
4. ✅ STEP 4: Import + module consistency audit (COMPLETE)
5. ⏭️ STEP 5: Startup sequence hardening
6. ⏭️ STEP 6: AI/ML stack validation
7. ⏭️ STEP 7: Local environment reconstruction
8. ⏭️ STEP 8: Backend validation suite
9. ⏭️ STEP 9: Developer experience hardening
10. ⏭️ STEP 10: Final target validation

---

## Conclusion

The import structure is healthy overall. The only critical issue is the missing sentence_transformers dependency. The session module has been fixed with compatibility aliases. No circular dependencies detected.
