#!/usr/bin/env python3
"""
Performance indexes migration script.

This script adds performance-optimizing indexes to the database.
Run this after the initial database setup.
"""

import logging
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db_session, create_database
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_performance_migration():
    """Run the performance indexes migration."""

    logger.info("Starting performance indexes migration...")

    # Create database tables if they don't exist
    logger.info("Ensuring database tables exist...")
    create_database()

    # Read and execute the migration SQL
    migration_file = Path(__file__).parent.parent / "app" / "database" / "migrations" / "001_performance_indexes.sql"

    if not migration_file.exists():
        logger.error(f"Migration file not found: {migration_file}")
        return False

    try:
        with open(migration_file, 'r') as f:
            migration_sql = f.read()

        # Split into individual statements (basic approach)
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]

        session = next(get_db_session())

        for statement in statements:
            if statement:
                logger.info(f"Executing: {statement[:50]}...")
                try:
                    session.execute(text(statement))
                    session.commit()
                except Exception as e:
                    logger.warning(f"Statement failed (might already exist): {e}")
                    session.rollback()

        session.close()

        logger.info("Performance indexes migration completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = run_performance_migration()
    sys.exit(0 if success else 1)