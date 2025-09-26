from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()

# Dependency to get database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session