from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from sqlalchemy import text
from app.core.config import settings
import logging
from typing import AsyncGenerator, Optional
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from dual_write_config import DualWriteSettings

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

# Dual-write manager (initialized later)
dual_write_manager: Optional['CartDualWriteManager'] = None

# Import all models after Base is defined to ensure they are registered with SQLAlchemy
# This must be done after Base is defined to avoid circular imports
from app.models.user import User
from app.models.cart import Cart, CartItem, Wishlist, WishlistItem, PromoCode, CartPromoCode

# Dependency to get database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
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
            logger.info("Cart Service database health check: OK")
            return True
    except Exception as e:
        logger.error(f"Cart Service database health check failed: {e}")
        return False

# Initialize database
async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Cart Service database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Cart Service database: {e}")
        raise

# Initialize dual-write manager
async def init_dual_write():
    """Initialize dual-write manager if legacy database is configured"""
    global dual_write_manager
    
    if settings.legacy_database_url and settings.dual_write_enabled:
        try:
            from app.core.dual_write_manager import CartDualWriteManager
            
            # Create dual-write settings from configuration
            dual_write_settings = DualWriteSettings(
                enabled=settings.dual_write_enabled,
                write_to_legacy=settings.dual_write_to_legacy,
                write_to_new=settings.dual_write_to_new,
                fail_on_legacy_error=settings.dual_write_fail_on_legacy_error,
                fail_on_new_error=settings.dual_write_fail_on_new_error,
                validate_sync=settings.dual_write_validate_sync,
                sync_validation_interval=settings.dual_write_sync_interval,
                async_legacy_writes=settings.dual_write_async_legacy,
                batch_size=settings.dual_write_batch_size,
                log_all_operations=settings.dual_write_log_all,
                log_errors_only=settings.dual_write_log_errors_only,
                metrics_enabled=settings.dual_write_metrics_enabled
            )
            
            dual_write_manager = CartDualWriteManager(
                new_db_url=settings.database_url,
                legacy_db_url=settings.legacy_database_url,
                settings=dual_write_settings
            )
            
            logger.info("Cart Service dual-write manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize dual-write manager: {e}")
            raise
    else:
        logger.info("Dual-write disabled or legacy database not configured")

def get_dual_write_manager() -> Optional['CartDualWriteManager']:
    """Get the dual-write manager instance"""
    return dual_write_manager

# Close database connections
async def close_db():
    """Close database engine and all connections"""
    try:
        await engine.dispose()
        
        # Close dual-write manager if initialized
        if dual_write_manager:
            await dual_write_manager.close()
        
        logger.info("Cart Service database connections closed")
    except Exception as e:
        logger.error(f"Error closing Cart Service database connections: {e}")
        raise