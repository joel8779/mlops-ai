"""Seed demo data for development and testing."""

import asyncio
from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.domain import Candidate, JobDescription, Organization, User
from app.core.security import get_password_hash


async def seed_demo_data(db: AsyncSession) -> None:
    """Seed demo data for development.

    Args:
        db: Database session
    """
    print("Seeding demo data...")

    # Create demo organization
    org = Organization(
        id=uuid4(),
        name="Demo Company",
        slug="demo-company",
        plan="enterprise",
        created_at=datetime.now(timezone.utc),
    )
    db.add(org)
    await db.flush()

    # Create demo user
    user = User(
        id=uuid4(),
        email="demo@resume-intelligence.com",
        hashed_password=get_password_hash("demo123"),
        full_name="Demo User",
        organization_id=org.id,
        role="admin",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()

    # Create demo job descriptions
    jobs = [
        JobDescription(
            id=uuid4(),
            title="Senior Software Engineer",
            description="We are looking for a senior software engineer with experience in Python, FastAPI, and machine learning.",
            required_skills=["Python", "FastAPI", "Machine Learning", "Docker", "Kubernetes"],
            organization_id=org.id,
            created_by=user.id,
            created_at=datetime.now(timezone.utc),
        ),
        JobDescription(
            id=uuid4(),
            title="ML Engineer",
            description="Join our ML team to build production-grade machine learning systems.",
            required_skills=["Python", "TensorFlow", "PyTorch", "MLOps", "Data Engineering"],
            organization_id=org.id,
            created_by=user.id,
            created_at=datetime.now(timezone.utc),
        ),
    ]
    for job in jobs:
        db.add(job)
    await db.flush()

    # Create demo candidates
    candidates = [
        Candidate(
            id=uuid4(),
            full_name="John Doe",
            headline="Senior Software Engineer",
            location="San Francisco, CA",
            organization_id=org.id,
            created_by=user.id,
            created_at=datetime.now(timezone.utc),
        ),
        Candidate(
            id=uuid4(),
            full_name="Jane Smith",
            headline="ML Engineer",
            location="New York, NY",
            organization_id=org.id,
            created_by=user.id,
            created_at=datetime.now(timezone.utc),
        ),
        Candidate(
            id=uuid4(),
            full_name="Bob Johnson",
            headline="Data Scientist",
            location="Austin, TX",
            organization_id=org.id,
            created_by=user.id,
            created_at=datetime.now(timezone.utc),
        ),
    ]
    for candidate in candidates:
        db.add(candidate)

    await db.commit()
    print("Demo data seeded successfully!")
    print(f"Organization: {org.name} ({org.id})")
    print(f"User: {user.email} (password: demo123)")
    print(f"Jobs: {len(jobs)}")
    print(f"Candidates: {len(candidates)}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/app")

    from app.core.database import get_db

    async def main():
        async for db in get_db():
            await seed_demo_data(db)

    asyncio.run(main())
