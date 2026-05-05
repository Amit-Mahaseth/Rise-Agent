"""
Database connection and session management for RiseAgent AI.
Supports both SQLite for development and PostgreSQL for production.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# SQLAlchemy base class for models
Base = declarative_base()

# Global engine instance
engine = None

# Async session factory
async_session = None


async def create_engine():
    """
    Create and configure the database engine.

    Returns:
        AsyncEngine: Configured SQLAlchemy async engine
    """
    global engine

    if engine is not None:
        return engine

    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True,  # Test connections before using them
        pool_recycle=300,    # Recycle connections after 5 minutes
    )

    logger.info("Database engine created", url=settings.database_url)
    return engine


async def create_session_factory():
    """
    Create async session factory.

    Returns:
        sessionmaker: Configured async session factory
    """
    global async_session

    if async_session is not None:
        return async_session

    engine = await create_engine()

    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return async_session


async def get_db() -> AsyncSession:
    """
    Dependency function to get database session.

    Yields:
        AsyncSession: Database session
    """
    session_factory = await create_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """
    Create all database tables defined in models.
    """
    from app.models import lead, conversation, call, scoring  # Import all models

    engine = await create_engine()

    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created successfully")


async def drop_tables():
    """
    Drop all database tables (for testing/cleanup).
    """
    engine = await create_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    logger.info("Database tables dropped successfully")


async def check_connection() -> bool:
    """
    Check database connection health.

    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        engine = await create_engine()
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error("Database connection check failed", error=str(e))
        return False


async def close_engine():
    """
    Close the database engine gracefully.
    """
    global engine
    if engine is not None:
        await engine.dispose()
        engine = None
        logger.info("Database engine closed")