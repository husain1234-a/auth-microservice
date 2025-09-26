"""
Database initialization script for Cart Service
This script creates the necessary tables for the cart service in the shared database.
"""

import asyncio
import asyncpg
from app.core.config import settings

async def init_db():
    # Connect to the shared database
    db_url = settings.database_url.replace('postgresql+asyncpg://', 'postgresql://')
    conn = await asyncpg.connect(db_url)
    
    # Read and execute the database schema
    with open('database_schema.sql', 'r') as f:
        schema = f.read()
    
    # Split schema into individual statements (simple approach)
    statements = [stmt.strip() for stmt in schema.split(';') if stmt.strip()]
    
    for statement in statements:
        try:
            await conn.execute(statement)
            print(f"✅ Executed: {statement[:50]}...")
        except Exception as e:
            if "already exists" in str(e):
                print(f"ℹ️ Skipping (already exists): {statement[:50]}...")
            else:
                print(f"❌ Error executing: {statement[:50]}... - {e}")
    
    await conn.close()
    print("✅ Database initialization completed")

if __name__ == "__main__":
    asyncio.run(init_db())