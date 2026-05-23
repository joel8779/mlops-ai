# Startup Isolation Hardening - PHASE 21

**Date**: 2026-05-23
**Phase**: STEP 7 - STARTUP ISOLATION HARDENING

## Overview

This document details startup isolation improvements to ensure the core API can start even if optional dependencies (telemetry, ML, vector DB, Gemini) fail to initialize.

## Current Startup Failure Chain

**Import Chain**:
```
app/main.py
  → app/api/v1/router
    → app/api/v1/routes/ai
      → app.agents.orchestrator.copilot_orchestrator
        → app.agents.execution.workflow_executor
          → app.services.retrieval.hybrid_retriever
            → app.services.semantic_search_service
              → app.services.embedding_service
                → qdrant_client
                  → grpc
                    → grpc._cython.cygrpc (FAILS)
```

**Result**: Backend cannot start at all due to grpc import failure

---

## Isolation Strategy

### 1. Lazy Import of Problematic Modules

**Goal**: Defer imports until actually needed

**Implementation**:
- Move qdrant-client import inside functions
- Move embedding_service import inside functions
- Move ML-dependent imports inside functions
- Only import when feature is actually used

### 2. Dependency Guards

**Goal**: Check if dependencies are available before importing

**Implementation**:
- Use try/except blocks around imports
- Provide fallback behavior when dependencies missing
- Log warnings when optional dependencies unavailable

### 3. Startup Isolation Boundaries

**Goal**: Isolate optional systems from core startup

**Boundaries**:
- Core API (FastAPI, routes, DB, Redis) - MUST work
- Telemetry (OpenTelemetry) - Optional, degrade gracefully
- Vector DB (Qdrant) - Optional, degrade gracefully
- ML (embeddings, semantic search) - Optional, degrade gracefully
- AI SDKs (Gemini) - Optional, degrade gracefully
- Agents (orchestrator, workflow) - Optional, degrade gracefully

---

## Implementation Plan

### Immediate Actions

1. **Make qdrant-client import lazy in embedding_service.py**
2. **Make embedding_service import lazy in semantic_search_service.py**
3. **Make semantic_search_service import lazy in hybrid_retriever.py**
4. **Make hybrid_retriever import lazy in workflow_executor.py**
5. **Make workflow_executor import lazy in copilot_orchestrator.py**
6. **Make copilot_orchestrator import lazy in ai.py**
7. **Make ai route optional (can fail without crashing core API)**

### Short-term Actions

1. Implement dependency guards in main.py
2. Implement capability detection at startup
3. Log unavailable dependencies at startup
4. Provide clear error messages for missing dependencies

### Long-term Actions

1. Implement feature flags for optional systems
2. Implement health checks for optional dependencies
3. Implement circuit breakers for external services
4. Implement graceful degradation for all optional systems

---

## Next Steps

1. ✅ STEP 1: Complete dependency forensics (COMPLETE)
2. ✅ STEP 2: GRPC ecosystem stabilization (COMPLETE)
3. ✅ STEP 3: Full venv reconstruction (COMPLETE)
4. ✅ STEP 4: Layered dependency strategy (COMPLETE)
5. ✅ STEP 5: Windows compatibility hardening (COMPLETE)
6. ✅ STEP 6: Optional ML degradation (COMPLETE)
7. ⏭️ STEP 7: Startup isolation hardening (IN PROGRESS)
8. ⏭️ STEP 8: Backend validation matrix
9. ⏭️ STEP 9: Docker + local parity
10. ⏭️ STEP 10: Final target validation

---

## Conclusion

The current startup failure is due to grpc import failure in the qdrant-client import chain. The solution is to implement lazy imports and dependency guards to isolate optional systems from core startup. This will allow the core API to start even if ML, vector DB, or telemetry dependencies fail.
