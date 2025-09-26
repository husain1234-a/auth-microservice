"""
Database table creation script for Cart Service
This script creates the necessary tables for the cart service using SQLAlchemy.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.database import Base
from app.models.user import User
from app.models.cart import Cart, CartItem, Wishlist, WishlistItem, PromoCode, CartPromoCode

async def create_tables():
    # Create async engine
    engine = create_async_engine(settings.database_url)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ All tables created successfully")

if __name__ == "__main__":
    asyncio.run(create_tables())