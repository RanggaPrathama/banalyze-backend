from contextlib import asynccontextmanager
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core import settings
from typing import AsyncGenerator


DATABASE_URL = getattr(settings, "database_url", "postgresql+asyncpg://postgres:postgres@localhost/banalyze_db")

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_pre_ping=True,  # Verify connections before use
    connect_args={"statement_cache_size": 0},  # Required for PgBouncer transaction pooling (Supabase)
)

# Session factory
async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False, 
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database sessions.
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    
    Yields:
        AsyncSession: Database session that auto-commits on success
                     and rolls back on exception.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions outside of request lifecycle.
    
    Usage:
        async with get_db_context() as db:
            result = await db.execute(query)
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """
    Initialize database tables.
    
    Creates all tables defined in the models.
    Call this during application startup.
    """
    from .base import Base
    async with engine.begin() as conn:
        print("METADATA TABLES:", list(Base.metadata.tables.keys()))
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.
    
    Call this during application shutdown.
    """
    await engine.dispose()