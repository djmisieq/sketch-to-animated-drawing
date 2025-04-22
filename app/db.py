"""Database module with SQLAlchemy setup."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator

from app.config import settings

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

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
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db() -> None:
    """Initialize the database by creating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
