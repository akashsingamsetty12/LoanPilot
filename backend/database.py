"""
LoanPilot Database Layer
=========================
Async SQLAlchemy engine and session management.
Supports SQLite (MVP) and PostgreSQL (production) via DATABASE_URL.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db():
    """
    FastAPI dependency that provides an async database session.
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables on application startup."""
    async with engine.begin() as conn:
        # Import all models so they are registered with Base.metadata
        import models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Dispose the engine on application shutdown."""
    await engine.dispose()
