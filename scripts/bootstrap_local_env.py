"""Bootstrap local development environment.

This script:
1. Validates database connectivity
2. Runs Alembic migrations
3. Optionally seeds demo data
4. Validates the bootstrap process

Usage:
    cd apps/api
    python scripts/bootstrap_local_env.py [--seed]
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import async_session_maker, async_engine
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def validate_database():
    """Validate database connectivity."""
    logger.info("Validating database connectivity...")
    
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✓ Database connectivity validated")
        return True
    except Exception as e:
        logger.error(f"✗ Database connectivity failed: {e}")
        return False


async def run_migrations():
    """Run Alembic migrations."""
    logger.info("Running Alembic migrations...")
    
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("✓ Alembic migrations completed")
        if result.stdout:
            logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Alembic migrations failed: {e}")
        if e.stderr:
            logger.error(e.stderr)
        return False


async def seed_demo_data():
    """Seed demo data."""
    logger.info("Seeding demo data...")
    
    try:
        result = subprocess.run(
            ["python", "scripts/setup_demo_environment.py"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("✓ Demo data seeded successfully")
        if result.stdout:
            logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Demo data seeding failed: {e}")
        if e.stderr:
            logger.error(e.stderr)
        return False


async def validate_schema():
    """Validate that schema was created correctly."""
    logger.info("Validating schema...")
    
    try:
        async with async_session_maker() as db:
            # Check for key tables
            result = await db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            expected_tables = [
                "organizations",
                "users",
                "candidates",
                "resumes",
                "job_descriptions",
                "candidate_matches",
                "candidate_pipeline_stages",
                "recruiter_notes",
                "recruiter_activities",
                "ranking_feedback",
            ]
            
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                logger.warning(f"Missing tables: {missing_tables}")
                return False
            
            logger.info(f"✓ Schema validated ({len(tables)} tables)")
            return True
    except Exception as e:
        logger.error(f"✗ Schema validation failed: {e}")
        return False


async def bootstrap(seed=False):
    """Bootstrap the local environment."""
    logger.info("=" * 60)
    logger.info("Bootstrapping Local Development Environment")
    logger.info("=" * 60)
    logger.info("")
    
    # Step 1: Validate database connectivity
    if not await validate_database():
        logger.error("Database connectivity validation failed. Exiting.")
        return False
    
    # Step 2: Run migrations
    if not await run_migrations():
        logger.error("Migration execution failed. Exiting.")
        return False
    
    # Step 3: Validate schema
    if not await validate_schema():
        logger.error("Schema validation failed. Exiting.")
        return False
    
    # Step 4: Seed demo data (optional)
    if seed:
        if not await seed_demo_data():
            logger.warning("Demo data seeding failed. Continuing anyway.")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✓ Local environment bootstrap completed successfully")
    logger.info("=" * 60)
    logger.info("")
    logger.info("You can now start the backend with:")
    logger.info("  uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload")
    logger.info("")
    
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Bootstrap local development environment")
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed demo data after migrations"
    )
    
    args = parser.parse_args()
    
    try:
        success = asyncio.run(bootstrap(seed=args.seed))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nBootstrap interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Bootstrap failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
