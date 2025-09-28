from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from sqlalchemy import text
from app.core.config import settings
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# Create a shared Base class for all models
Base = declarative_base()

# Create async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,  # Validates connections before use
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get DB session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

# Database health check
async def check_database_health() -> bool:
    """
    Check if the database connection is healthy.
    Returns True if healthy, False otherwise.
    """
    try:
        async with AsyncSessionLocal() as session:
            # Execute a simple query to test connection
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            logger.info("Product Service database health check: OK")
            return True
    except Exception as e:
        logger.error(f"Product Service database health check failed: {e}")
        return False

# Initialize database
async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Product Service database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Product Service database: {e}")
        raise

# Close database connections
async def close_db():
    """Close database engine and all connections"""
    try:
        await engine.dispose()
        logger.info("Product Service database connections closed")
    except Exception as e:
        logger.error(f"Error closing Product Service database connections: {e}")
        raise