#!/usr/bin/env python3
"""
Database Connection Test Script

This script tests the database connections for all services to ensure
they can connect to their respective isolated databases.
"""

import asyncio
import sys
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_database_connection(service_name: str, database_url: str) -> bool:
    """Test database connection for a service"""
    try:
        print(f"🔗 Testing {service_name} database connection...")
        
        # Create a simple engine for testing
        engine = create_async_engine(database_url, echo=False)
        
        # Create session factory
        async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
        
        # Test connection
        async with async_session() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
        
        # Clean up
        await engine.dispose()
        
        print(f"✅ {service_name} database connection: SUCCESS")
        return True
        
    except Exception as e:
        print(f"❌ {service_name} database connection: ERROR - {e}")
        return False


async def test_auth_service_db():
    """Test Auth Service database connection"""
    database_url = "postgresql+asyncpg://poc_user:admin123@localhost:5432/auth_db"
    return await test_database_connection("Auth Service", database_url)


async def test_cart_service_db():
    """Test Cart Service database connection"""
    database_url = "postgresql+asyncpg://poc_user:admin123@localhost:5432/cart_db"
    return await test_database_connection("Cart Service", database_url)


async def test_product_service_db():
    """Test Product Service database connection"""
    database_url = "postgresql+asyncpg://poc_user:admin123@localhost:5432/product_db"
    return await test_database_connection("Product Service", database_url)


async def main():
    """Run all database connection tests"""
    print("🚀 Starting database connection tests for all services...\n")
    
    # Test all services
    results = await asyncio.gather(
        test_auth_service_db(),
        test_cart_service_db(),
        test_product_service_db(),
        return_exceptions=True
    )
    
    # Count successful connections
    successful_connections = sum(1 for result in results if result is True)
    total_services = len(results)
    
    print(f"\n📊 Test Results: {successful_connections}/{total_services} services connected successfully")
    
    if successful_connections == total_services:
        print("🎉 All database connections are working properly!")
        return 0
    else:
        print("⚠️  Some database connections failed. Check the logs above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)