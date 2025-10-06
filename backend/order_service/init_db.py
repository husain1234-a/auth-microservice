#!/usr/bin/env python3
"""
Database initialization script for the Order Service.
This script creates all necessary database tables.
"""

import asyncio
import logging
from app.core.database import engine
from app.models.base import Base
from app.models.order import Order, OrderItem, OrderTemplate, OrderFeedback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    """Initialize the database tables"""
    try:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())