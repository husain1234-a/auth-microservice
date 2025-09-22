from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.config import settings
from app.models.category import Base as CategoryBase
from app.models.product import Base as ProductBase
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
    # For SQLite, we need to create all tables
    async with engine.begin() as conn:
        await conn.run_sync(CategoryBase.metadata.create_all)
        await conn.run_sync(ProductBase.metadata.create_all)

async def get_db():
    """Dependency to get DB session"""
    async with AsyncSessionLocal() as session:
        yield session