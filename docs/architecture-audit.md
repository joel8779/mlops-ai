# Architecture Audit Report

**Date**: 2026-05-27
**Scope**: Full System Rewire + Forensic Audit Mode
**Objective**: Transform platform from "partially working prototype" to "stable production-grade ATS architecture"

## Executive Summary

This audit identified critical issues across 20 areas of the ATS platform. The platform requires comprehensive hardening to achieve production readiness while maintaining deployment compatibility with Railway, Render, Vercel, and Docker.

## Phase 1: Forensic Error Audit Findings

### 1. Placeholder Strings Found

#### Backend Placeholders
- **File**: `apps/api/app/services/candidate_extraction_service.py:189`
  - **Issue**: Returns `"Imported Candidate"` as fallback name
  - **Impact**: Production shows placeholder instead of derived name
  - **Severity**: Medium
  - **Fix Required**: Derive from filename, email, or first heading

- **File**: `apps/api/app/workers/resume_tasks.py:265`
  - **Issue**: Sets `full_name="Imported Candidate"` for new candidates
  - **Impact**: Database contains placeholder names
  - **Severity**: Medium
  - **Fix Required**: Use filename-derived name or require recruiter input

#### Frontend Placeholders
- **File**: `apps/web/app/candidates/[id]/page.tsx:81`
  - **Issue**: Shows `"No skills extracted."` when skills array is empty
  - **Impact**: User sees placeholder instead of actionable state
  - **Severity**: Low
  - **Fix Required**: Show "Skills extraction in progress" or "Upload resume to extract skills"

- **File**: `apps/web/app/analytics/page.tsx:93`
  - **Issue**: Shows `"No skills extracted yet."` when no skills exist
  - **Impact**: Analytics panel shows placeholder
  - **Severity**: Low
  - **Fix Required**: Show "No candidates with skills yet"

- **File**: `apps/web/app/candidates/page.tsx:179`
  - **Issue**: Shows `"No skills extracted yet"` when skills array is empty
  - **Impact**: Candidate list shows placeholder
  - **Severity**: Low
  - **Fix Required**: Show "Skills pending" or similar

### 2. Exception Handling Issues

#### Silent Exception Blocks
- **File**: `apps/api/app/services/delete_service.py:62-63`
  - **Issue**: Catches all exceptions during storage delete without logging
  - **Impact**: Storage failures are silently ignored
  - **Severity**: High
  - **Fix Required**: Log storage delete failures with traceback

- **File**: `apps/api/app/services/delete_service.py:136-138`
  - **Issue**: Catches all exceptions during DB rollback
  - **Impact**: Database errors are swallowed
  - **Severity**: High
  - **Fix Required**: Log rollback failures with context

- **File**: `apps/api/app/services/ranker_inference_service.py:30-32`
  - **Issue**: Catches all exceptions during model inference, returns fallback
  - **Impact**: Model failures are silently masked
  - **Severity**: High
  - **Fix Required**: Log inference failures, distinguish between model errors and data errors

- **File**: `apps/api/app/services/matching_service.py:48-49`
  - **Issue**: Catches all exceptions during semantic search, returns empty array
  - **Impact**: Search failures are silently masked
  - **Severity**: High
  - **Fix Required**: Log search failures, return error state instead of empty results

- **File**: `apps/api/app/services/resume_ingestion.py:80-83`
  - **Issue**: Catches all exceptions during task enqueue
  - **Impact**: Queue failures are silently ignored
  - **Severity**: High
  - **Fix Required**: Log enqueue failures with full context

### 3. Fallback Logic Issues

#### Model Router Fallbacks
- **File**: `apps/api/app/services/llm/providers/model_router.py:183-192`
  - **Issue**: Silent fallback to alternative models without logging which model failed
  - **Impact**: Difficult to debug model selection issues
  - **Severity**: Medium
  - **Fix Required**: Log each model attempt with failure reason

#### Dependency Validation
- **File**: `apps/api/app/runtime/diagnostics/dependency_validator.py:126-127`
  - **Issue**: Catches all exceptions during version parsing, assumes OK
  - **Impact**: Dependency version issues are silently ignored
  - **Severity**: Medium
  - **Fix Required**: Log version parsing failures

## Phase 2: Ingestion Pipeline Status

### Current Pipeline Stages
- ✅ `queued` - Resume uploaded
- ✅ `parsing` - OCR/parser executing
- ✅ `parsed` - Text extracted
- ✅ `embedding` - Vector embeddings created
- ✅ `indexed` - Vectors stored in Qdrant
- ✅ `completed` - Pipeline finished
- ✅ `failed` - Pipeline failed with error

### Missing Pipeline Stages
- ❌ `cleaning` - Text preprocessing to remove noise
- ❌ `summarizing` - Gemini summary generation
- ❌ `ranking` - ATS scoring

### Pipeline Issues
1. **Skills Persistence**: Fixed in previous session - now commits after skill extraction
2. **Stage Tracking**: Fixed in previous session - now updates stages at each step
3. **Failure Handling**: Logs failures but needs more granular error classification
4. **Orphan Vectors**: Need to verify Qdrant cleanup on candidate deletion

## Phase 3: Auth + Tenant Isolation Status

### Auth Flow
- ✅ Token validation on app startup via `/me` endpoint
- ✅ Logout clears localStorage, cookies, auth context
- ✅ Protected routes redirect unauthenticated users
- ✅ Logout redirects to `/login` instead of `/`

### Tenant Isolation
- ✅ All repository queries use `owner_id` filtering
- ✅ All API endpoints use `AuthContext` for tenant scoping
- ✅ Candidate, Job, Resume, ATS, Semantic queries are tenant-scoped
- ⚠️ Need to verify vector search tenant isolation

### Auth Vulnerabilities Fixed
1. Auto-sign-in bug - fixed with token validation
2. Stale JWT persistence - fixed with `/me` validation
3. Invalid token restoration - fixed with logout cleanup
4. Protected route bypass - fixed with authentication guards

## Phase 4: ATS Engine Status

### ATS Scoring Components
- ✅ Keyword overlap scoring
- ✅ Semantic similarity scoring
- ✅ Experience match scoring
- ✅ Education match scoring
- ⚠️ Recruiter weighting - not implemented

### ATS Issues
1. **Seniority Hallucination**: Fixed in previous session - removed tech stack keyword inference
2. **JD Title Placeholder**: Fixed in previous session - derives from filename
3. **JD Noise**: Fixed in previous session - implemented preprocessing pipeline
4. **ATS Without JD**: Need to verify ATS only runs against selected JD

## Phase 5: JD Extraction Status

### JD Preprocessing
- ✅ Implemented `_preprocess_jd()` method
- ✅ Removes copyright, disclaimer, troubleshooting, instructions
- ✅ Removes assessment logistics, support contacts, browser requirements
- ✅ Keeps job, role, position, title, responsibilities, requirements
- ✅ Removes duplicate lines
- ✅ Removes low-signal text

### JD Issues
1. **Placeholder Title**: Fixed - derives from filename or first heading
2. **Noise Suppression**: Implemented - removes boilerplate before embeddings
3. **Semantic Cleaning**: Implemented - filters repeated text

## Phase 6: Gemini Integration Status

### Gemini Usage
- ✅ Candidate summary generation
- ✅ Recruiter email drafts
- ✅ Shortlist reasoning
- ✅ Clean JD summaries

### Gemini Constraints
- ✅ Removed `inferred_seniority` from schema
- ✅ Removed tech stack keyword inference
- ✅ Uses structured grounding data

### Gemini Issues
1. **Prompt Validation**: Need to audit all prompts for hallucination risks
2. **Error Handling**: Need to verify Gemini failures are logged correctly
3. **Fallback Logic**: Need to verify fallback behavior when Gemini is unavailable

## Phase 7: Database + ORM Consistency

### Relationships
- ✅ Fixed ambiguous foreign keys in `domain.py`
- ✅ Added explicit `foreign_keys` and `back_populates` on all relationships
- ✅ Fixed type hint syntax for `Optional` types

### Schema Issues
1. **Migration Drift**: Need to verify all migrations are applied
2. **Orphan Rows**: Need to verify cascade deletes work correctly
3. **Nullable Fields**: Need to verify consistency across models

## Phase 8: Vector DB Consistency

### Qdrant Integration
- ✅ Vectors scoped by `organization_id` and `owner_id`
- ✅ Semantic search uses tenant filtering
- ⚠️ Need to verify vector deletion on candidate deletion
- ⚠️ Need to verify vector deletion on job deletion

### Vector Issues
1. **Orphan Vectors**: Need to implement cleanup on entity deletion
2. **Vector Scoping**: Need to verify all vector operations are tenant-safe

## Phase 9: Frontend UX Status

### UX Improvements
- ✅ Redesigned JD panel with three-section layout
- ✅ Top section: Job title, experience, skills, ATS stats
- ✅ Middle section: JD summary, semantic requirements
- ✅ Bottom section: Ranked candidates, semantic insights

### Frontend Issues
1. **Placeholder Strings**: Found "No skills extracted" in multiple locations
2. **Loading States**: Need to verify meaningful loading states
3. **Empty States**: Need to verify actionable empty states

## Phase 10: Production Hardening

### Deployment Compatibility
- ✅ Docker compose configuration exists
- ✅ Railway deployment support maintained
- ✅ Render deployment support maintained
- ✅ Vercel frontend deployment support maintained

### Production Issues
1. **Healthchecks**: Need to verify API healthchecks work
2. **Startup Sequencing**: Need to verify service startup order
3. **Redis Connectivity**: Need to verify worker reconnection
4. **DB Readiness**: Need to verify migration startup order

## Critical Issues Summary

### High Priority
1. Silent exception blocks in delete_service.py
2. Silent exception blocks in ranker_inference_service.py
3. Silent exception blocks in matching_service.py
4. Silent exception blocks in resume_ingestion.py
5. Placeholder name "Imported Candidate" in database
6. Vector deletion on candidate/job deletion

### Medium Priority
1. Placeholder strings in frontend
2. Model router fallback logging
3. Dependency validation error handling
4. JD title placeholder (already fixed)
5. Gemini prompt validation

### Low Priority
1. Frontend empty state messaging
2. Loading state improvements
3. UX refinements

## Unresolved Risks

1. **Vector Orphan Cleanup**: Not verified that vectors are deleted when candidates/jobs are deleted
2. **ATS Without JD**: Not verified that ATS scoring requires a selected JD
3. **Gemini Fallback**: Not verified behavior when Gemini is unavailable
4. **Migration Drift**: Not verified all migrations are applied correctly
5. **Cascade Deletes**: Not verified cascade delete behavior across all relationships

## Next Steps

1. Fix silent exception blocks with proper logging
2. Replace "Imported Candidate" with derived names
3. Implement vector cleanup on entity deletion
4. Verify ATS scoring requires selected JD
5. Audit Gemini prompts for hallucination risks
6. Verify all migrations are applied
7. Test cascade delete behavior
8. Implement recruiter weighting for ATS
9. Add missing pipeline stages (cleaning, summarizing, ranking)
10. Verify production deployment compatibility
