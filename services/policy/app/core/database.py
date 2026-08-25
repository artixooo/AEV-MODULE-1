"""
Policy Service Database Infrastructure Module.

Provides SQLAlchemy database engine initialization, ORM session factory management,
and dependency injection helpers for database connections.

Author: Utkarsh Pratham (Squad Leader) & Narayanan Varadarajan
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

# Determine Database Connection URL (Supports SQLite for Testing & Postgres for Prod)
DATABASE_URL = os.getenv("TEST_DATABASE_URL") or settings.DATABASE_URL

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
elif settings.APP_ENV == "development":
    # In development only: fall back to an in-memory DB rather than blocking
    # local work on a missing Postgres instance. Never do this outside dev —
    # it would silently lose all data on every restart.
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
    except Exception as e:
        logger.warning(f"Failed to initialize PostgreSQL connection pool ({e}). Falling back to in-memory SQLite (development only).")
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
else:
    # Staging/production: fail loudly rather than silently degrading to a
    # throwaway in-memory database.
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI Dependency Generator for Database Sessions.

    Yields:
        Session: Active SQLAlchemy Database Session.

    Ensure:
        The database session is safely closed after handling the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
