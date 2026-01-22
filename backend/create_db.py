#!/usr/bin/env python3
"""
Script to create database tables directly.
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import *  # Import all models

# Database URL for Docker
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/zoning_dev"

def create_tables():
    """Create all database tables."""
    print("Creating database tables...")

    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)

    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")

        # Create a session to test
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        db.close()
        print("✅ Database connection test successful!")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_tables()