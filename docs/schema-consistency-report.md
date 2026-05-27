# Schema Consistency Report

**Date**: 2026-05-27
**Status**: Production-Ready After Fixes

## Database Schema Overview

The platform uses PostgreSQL with SQLAlchemy ORM. The schema is managed via Alembic migrations.

## Migration Status

### Current Migration
- **Latest Migration**: 0006_owner_isolation (head)
- **Status**: ✅ Applied
- **Verification**: `alembic current` confirms 0006_owner_isolation at head

### Migration History
1. 0001_initial_schema - Base schema creation
2. 0002_ai_intelligence_workflow - AI workflow tables
3. 0003_enterprise_scale - Enterprise scaling features
4. 0004_job_context_ats - Job context and ATS tables
5. 0005_pipeline_stage_contract - Pipeline stage tracking
6. 0006_owner_isolation - Owner scoping for tenant isolation

## Relationship Consistency

### Foreign Key Constraints

All foreign keys are properly defined with:
- ✅ Explicit `ForeignKey` references
- ✅ Proper `back_populates` on relationships
- ✅ Cascade deletes configured at database level
- ✅ Indexes on foreign key columns for performance

### Relationship Fixes Applied

#### domain.py Fixes
- ✅ Fixed ambiguous foreign keys with explicit `foreign_keys` parameter
- ✅ Fixed type hint syntax for `Optional` types
- ✅ Added proper `back_populates` on all relationships
- ✅ Fixed circular import issues

#### Migration 0006_owner_isolation
- ✅ Added `owner_id` column to all tenant-scoped tables
- ✅ Created foreign key constraints with `ondelete="CASCADE"`
- ✅ Created indexes on `owner_id` columns
- ✅ Added composite index on `candidates(owner_id, created_at)`

## Table Consistency

### Core Tables

#### users
- ✅ Primary key: id (UUID)
- ✅ Foreign key: organization_id → organizations.id
- ✅ Unique constraint: email
- ✅ Indexes: email, organization_id
- ✅ Cascade deletes: Not applicable (parent table)

#### organizations
- ✅ Primary key: id (UUID)
- ✅ Unique constraint: slug
- ✅ Indexes: name, slug
- ✅ Cascade deletes: Not applicable (parent table)

#### candidates
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id → users.id
- ✅ Indexes: owner_id, owner_id + created_at
- ✅ Cascade deletes: owner_id → CASCADE

#### resumes
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id, candidate_id, uploaded_by_user_id → users.id
- ✅ Unique constraint: checksum_sha256
- ✅ Indexes: owner_id, candidate_id, checksum_sha256
- ✅ Cascade deletes: owner_id → CASCADE

#### job_descriptions
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id, created_by_user_id → users.id
- ✅ Indexes: owner_id, status
- ✅ Cascade deletes: owner_id → CASCADE

### Supporting Tables

#### candidate_embeddings
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id, candidate_id, resume_id
- ✅ Unique constraint: qdrant_point_id
- ✅ Indexes: owner_id, candidate_id, resume_id, qdrant_point_id
- ✅ Cascade deletes: owner_id → CASCADE

#### job_description_embeddings
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id, job_description_id
- ✅ Unique constraint: qdrant_point_id
- ✅ Indexes: owner_id, job_description_id, qdrant_point_id
- ✅ Cascade deletes: owner_id → CASCADE

#### candidate_skills
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id, candidate_id
- ✅ Unique constraint: candidate_id + skill
- ✅ Indexes: owner_id, candidate_id, skill
- ✅ Cascade deletes: owner_id → CASCADE

#### ats_scores
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id, candidate_id, job_description_id, resume_id
- ✅ Unique constraint: candidate_id + job_description_id
- ✅ Indexes: owner_id, candidate_id, job_description_id, job_description_id + ats_score
- ✅ Cascade deletes: owner_id → CASCADE

#### candidate_matches
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id, candidate_id, job_description_id
- ✅ Unique constraint: candidate_id + job_description_id
- ✅ Indexes: owner_id, candidate_id, job_description_id, job_description_id + overall_score
- ✅ Cascade deletes: owner_id → CASCADE

#### candidate_pipeline_stages
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id, candidate_id, job_description_id
- ✅ Indexes: owner_id, candidate_id, job_description_id, stage
- ✅ Cascade deletes: owner_id → CASCADE

#### recruiter_notes
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id, candidate_id, user_id
- ✅ Indexes: owner_id, candidate_id, user_id
- ✅ Cascade deletes: owner_id → CASCADE

#### candidate_bookmarks
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id, candidate_id, user_id
- ✅ Unique constraint: candidate_id + user_id
- ✅ Indexes: owner_id, candidate_id, user_id
- ✅ Cascade deletes: owner_id → CASCADE

#### ranking_feedback
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id, candidate_id, job_description_id, user_id
- ✅ Indexes: owner_id, candidate_id, job_description_id, user_id
- ✅ Cascade deletes: owner_id → CASCADE

#### recruiter_activities
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id, candidate_id, job_description_id, user_id
- ✅ Indexes: owner_id, user_id, candidate_id, job_description_id
- ✅ Cascade deletes: owner_id → CASCADE

#### resume_processing_events
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id, resume_id
- ✅ Indexes: owner_id, resume_id, event_type
- ✅ Cascade deletes: owner_id → CASCADE

#### analytics_snapshots
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id
- ✅ Indexes: owner_id, snapshot_date
- ✅ Cascade deletes: owner_id → CASCADE

#### llm_usage_logs
- ✅ Primary key: id (UUID)
- ✅ Foreign keys: organization_id, owner_id (nullable)
- ✅ Indexes: owner_id, feature, created_at
- ✅ Cascade deletes: owner_id → SET NULL

## Nullable Field Consistency

### Critical Fields
- ✅ All primary keys are non-nullable
- ✅ All foreign keys in tenant-scoped tables are non-nullable
- ✅ `llm_usage_logs.owner_id` is nullable (SET NULL cascade)
- ✅ Optional fields properly typed as `Optional[T]`

### Soft Delete Fields
- ✅ `deleted_at` is nullable on all soft-deletable tables
- ✅ Soft delete queries filter on `deleted_at.is_(None)`
- ✅ Cascade deletes handle soft-deleted parent rows correctly

## Index Consistency

### Performance Indexes
- ✅ All foreign key columns have indexes
- ✅ All unique constraints have indexes
- ✅ Composite indexes for common query patterns
- ✅ Index naming follows convention: `ix_{table}_{columns}`

### Query Optimization
- ✅ Owner-scoped queries use `owner_id` index
- ✅ Candidate lookups use `candidate_id` index
- ✅ Job lookups use `job_description_id` index
- ✅ Resume lookups use `checksum_sha256` index

## Cascade Delete Behavior

### Database-Level Cascades
- ✅ All `owner_id` foreign keys have `ondelete="CASCADE"`
- ✅ Deleting a user cascades to all owned data
- ✅ Deleting an organization cascades to all users and their data

### ORM-Level Cascades
- ✅ No cascade delete configured at ORM level
- ✅ Cascade deletes handled by database constraints
- ✅ ORM relationships use proper `back_populates`

### Soft Delete Behavior
- ✅ Soft deletes use `deleted_at` timestamp
- ✅ Soft-deleted records excluded from queries
- ✅ Hard deletes cascade through database constraints

## Schema Drift

### Migration Verification
- ✅ All migrations applied (0006 at head)
- ✅ No pending migrations
- ✅ No migration conflicts
- ✅ No schema drift detected

### ORM-DB Alignment
- ✅ SQLAlchemy models match database schema
- ✅ No missing columns in models
- ✅ No extra columns in database
- ✅ Type annotations match database types

## Data Integrity

### Unique Constraints
- ✅ User email uniqueness enforced
- ✅ Organization slug uniqueness enforced
- ✅ Resume checksum uniqueness enforced
- ✅ Qdrant point ID uniqueness enforced
- ✅ Candidate-skill uniqueness enforced
- ✅ ATS score uniqueness enforced
- ✅ Candidate match uniqueness enforced
- ✅ Candidate bookmark uniqueness enforced

### Referential Integrity
- ✅ All foreign keys validated
- ✅ No orphan rows possible
- ✅ Cascade deletes prevent orphan rows
- ✅ Soft deletes maintain referential integrity

## Production Readiness

The schema is production-ready with:
- ✅ All migrations applied
- ✅ No schema drift
- ✅ Proper foreign key constraints
- ✅ Cascade deletes configured
- ✅ Indexes for performance
- ✅ Unique constraints for data integrity
- ✅ ORM-DB alignment verified
- ✅ Tenant isolation enforced at database level

## Recommendations

### High Priority
- None identified

### Medium Priority
1. Consider adding composite indexes for complex query patterns
2. Monitor index usage and add missing indexes as needed
3. Consider partitioning large tables (resumes, candidate_embeddings) for scale

### Low Priority
1. Add database-level check constraints for business rules
2. Consider adding triggers for audit logging
3. Implement database-level row-level security for defense in depth

## Conclusion

The database schema is consistent, well-structured, and production-ready. All migrations are applied, foreign key constraints are properly configured, and cascade deletes are enforced at the database level. The schema supports tenant isolation and data integrity requirements.
