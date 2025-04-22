"""Database module with SQLAlchemy setup."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator, Optional
import sqlite3
import os

from app.config import settings

logger = logging.getLogger(__name__)

# Check if PostgreSQL is available
try:
    # Create async engine with PostgreSQL
    engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
    logger.info(f"Using PostgreSQL database: {settings.POSTGRES_DB} on {settings.POSTGRES_SERVER}")
    using_sqlite = False
except Exception as e:
    # Fallback to SQLite for development
    logger.warning(f"PostgreSQL connection failed: {e}")
    logger.warning("Using SQLite database for development")
    
    # Create SQLite file in temp directory
    sqlite_file = "sketch_app_dev.db"
    sqlite_url = f"sqlite+aiosqlite:///{sqlite_file}"
    
    # Create engine with SQLite
    engine = create_async_engine(sqlite_url, echo=True, future=True, connect_args={"check_same_thread": False})
    using_sqlite = True

# Create async session
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Base class for all models
Base = declarative_base()


async def get_db() -> Generator[AsyncSession, None, None]:
    """Get DB session.

    Yields:
        Generator[AsyncSession, None, None]: DB session
    """
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db() -> None:
    """Initialize the database by creating all tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise
