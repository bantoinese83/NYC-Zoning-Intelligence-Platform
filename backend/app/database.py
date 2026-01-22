"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .config import settings

# Create SQLAlchemy engine
if settings.is_testing:
    # Use in-memory SQLite for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.debug,
    )
else:
    # Use PostgreSQL with PostGIS for development/production
    engine = create_engine(
        settings.database_url,
        echo=settings.debug,
        # Connection pooling for scalability
        pool_size=10,  # Maximum number of persistent connections
        max_overflow=20,  # Maximum number of connections that can be created above pool_size
        pool_timeout=30,  # Timeout for getting connection from pool
        pool_recycle=300,  # Recycle connections after 5 minutes
        pool_pre_ping=True,  # Verify connections before use
        # Performance optimizations
        connect_args={
            "connect_timeout": 10,  # Connection timeout
            "options": "-c statement_timeout=30000",  # Query timeout (30 seconds)
        } if "postgresql" in settings.database_url else {},
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency to get database session.

    Yields a database session that is automatically closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database():
    """
    Create all database tables.

    This function creates all tables defined in the models.
    Should only be called during development or initial setup.
    """
    Base.metadata.create_all(bind=engine)


def reset_database():
    """
    Drop and recreate all database tables.

    WARNING: This will delete all data in the database.
    Only use during development or when you want to start fresh.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_database_url() -> str:
    """
    Get the database URL for the current environment.

    Returns a masked version for security in logs.
    """
    if settings.is_testing:
        return "sqlite:///:memory:"

    # Mask password in URL for logging
    url = settings.database_url
    if "://" in url and "@" in url:
        protocol, rest = url.split("://", 1)
        auth, host = rest.split("@", 1)
        if ":" in auth:
            user, _ = auth.split(":", 1)
            return f"{protocol}://{user}:***@{host}"

    return url
