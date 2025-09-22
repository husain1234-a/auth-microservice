from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.config import settings
import asyncio

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

async def init_db():
    """Initialize the database tables"""
    # Import models after engine creation to avoid circular imports
    from app.core.database import Base
    
    # Create all tables with proper dependency order
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.models import category, product
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Dependency to get DB session"""
    async with AsyncSessionLocal() as session:
        yield session