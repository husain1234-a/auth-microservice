from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# Create async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
    echo=True if settings.environment == "development" else False,
    # Connection pooling for high load
    pool_size=20,          # Base pool size
    max_overflow=50,       # Additional connections when needed
    pool_timeout=30,       # Timeout waiting for connection
    pool_recycle=3600,     # Recycle connections every hour
    pool_pre_ping=True,    # Validate connections before use
    future=True
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Dependency to get database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Initialize database
async def init_db():
    from .models.user import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)