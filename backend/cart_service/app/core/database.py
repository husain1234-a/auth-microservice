from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Create a shared Base class for all models
Base = declarative_base()

# Create async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    # Connection pooling for high load
    pool_size=20,          # Base pool size
    max_overflow=50,       # Additional connections when needed
    pool_timeout=30,       # Timeout waiting for connection
    pool_recycle=3600,     # Recycle connections every hour
    pool_pre_ping=True,    # Validate connections before use
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

# Import all models after Base is defined to ensure they are registered with SQLAlchemy
# This must be done after Base is defined to avoid circular imports
from app.models.user import User
from app.models.cart import Cart, CartItem, Wishlist, WishlistItem, PromoCode, CartPromoCode

# Dependency to get database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session