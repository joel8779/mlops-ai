"""Development-only data reset utility.

Truncates application tables while preserving schema, indexes, constraints, and
the Alembic version table. It also clears Qdrant collections used for embeddings.
This script is intentionally gated behind ``--confirm`` and refuses to run in production.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect, text

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.core.config import settings  # noqa: E402
from app.models.base import Base  # noqa: E402
import app.models.domain  # noqa: F401, E402


PRESERVED_TABLES = {"alembic_version"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Truncate local development application data.")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required confirmation flag. Without this, no data is removed.",
    )
    return parser.parse_args()


def clear_qdrant_embeddings() -> None:
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(
            url=str(settings.qdrant_url),
            api_key=settings.qdrant_api_key,
            timeout=settings.qdrant_timeout_seconds,
        )
        existing = {collection.name for collection in client.get_collections().collections}
        collections_to_delete = [
            settings.qdrant_collection,
            settings.qdrant_job_collection,
            settings.qdrant_memory_collection,
            settings.qdrant_recommendation_collection,
        ]
        deleted_any = False
        for collection_name in collections_to_delete:
            if collection_name in existing:
                client.delete_collection(collection_name=collection_name)
                print(f"Cleared Qdrant collection: {collection_name}")
                deleted_any = True
        if not deleted_any:
            print("No matching Qdrant collections found to clear.")
    except Exception as exc:
        print(f"Warning: Could not clear Qdrant embeddings because Qdrant is offline or not configured: {exc}")


def main() -> int:
    args = parse_args()
    if not args.confirm:
        print("Refusing to reset data without --confirm.")
        return 2

    if settings.environment == "production":
        print("Refusing to reset data when ENVIRONMENT=production.")
        return 3

    # Reset Qdrant embeddings first
    clear_qdrant_embeddings()

    # Reset database tables
    engine = create_engine(settings.sync_database_url)
    model_tables = {table.name for table in Base.metadata.sorted_tables}
    with engine.begin() as connection:
        existing_tables = set(inspect(connection).get_table_names())
        tables = sorted((model_tables & existing_tables) - PRESERVED_TABLES)
        if not tables:
            print("No application tables found to truncate.")
            return 0

        if engine.dialect.name == "postgresql":
            quoted_tables = ", ".join(f'public."{table}"' for table in tables)
            connection.execute(text(f"TRUNCATE TABLE {quoted_tables} RESTART IDENTITY CASCADE"))
        elif engine.dialect.name == "sqlite":
            connection.execute(text("PRAGMA foreign_keys = OFF;"))
            for table in tables:
                connection.execute(text(f'DELETE FROM "{table}"'))
            connection.execute(text("PRAGMA foreign_keys = ON;"))
        else:
            print(f"Refusing to truncate data for unsupported dialect: {engine.dialect.name}.")
            return 4

        # Validate that all counts become 0
        validation_failed = False
        for table in tables:
            count = connection.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar()
            if count != 0:
                print(f"Validation FAILED: Table '{table}' still contains {count} records.")
                validation_failed = True
            else:
                print(f"Table '{table}': count is 0 (verified)")

        if validation_failed:
            print("Validation FAILED: Some tables were not completely cleared.")
            return 5

    print(f"Successfully truncated {len(tables)} application tables.")
    print("Preserved schema, indexes, constraints, migrations, and alembic_version.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
