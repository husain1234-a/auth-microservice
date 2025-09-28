#!/usr/bin/env python3
"""
Database Setup Checker

This script checks if all required databases and users exist before migration.
"""

import asyncio
import logging
import sys
from typing import Dict, List

import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration for checking"""
    
    # PostgreSQL superuser connection (for creating databases/users)
    POSTGRES_ADMIN = {
        'host': 'localhost',
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres',
        'password': 'postgres'  # Default, user should update if different
    }
    
    # Target databases to check/create
    DATABASES = {
        'poc': {
            'database': 'poc',
            'user': 'poc_user',
            'password': 'admin123'
        },
        'auth_db': {
            'database': 'auth_db',
            'user': 'auth_user',
            'password': 'auth_pass123'
        },
        'product_db': {
            'database': 'product_db',
            'user': 'product_user',
            'password': 'product_pass123'
        },
        'cart_db': {
            'database': 'cart_db',
            'user': 'cart_user',
            'password': 'cart_pass123'
        },
        'promotion_db': {
            'database': 'promotion_db',
            'user': 'promotion_user',
            'password': 'promotion_pass123'
        }
    }

class DatabaseChecker:
    """Checks and creates databases if needed"""
    
    def __init__(self):
        self.admin_config = DatabaseConfig.POSTGRES_ADMIN
        self.databases = DatabaseConfig.DATABASES
    
    async def check_all_databases(self):
        """Check all databases and create if needed"""
        logger.info("Checking database setup...")
        
        try:
            # First, test admin connection
            await self.test_admin_connection()
            
            # Check each database
            for db_name, db_config in self.databases.items():
                await self.check_database(db_name, db_config)
            
            logger.info("[SUCCESS] All databases are ready for migration!")
            return True
            
        except Exception as e:
            logger.error(f"Database setup check failed: {e}")
            return False
    
    async def test_admin_connection(self):
        """Test connection to PostgreSQL as admin"""
        try:
            conn = await asyncpg.connect(**self.admin_config)
            await conn.close()
            logger.info("[OK] PostgreSQL admin connection successful")
        except Exception as e:
            logger.error(f"Cannot connect to PostgreSQL as admin: {e}")
            logger.info("Please ensure PostgreSQL is running and update admin credentials in this script")
            raise
    
    async def check_database(self, db_name: str, db_config: Dict):
        """Check if database and user exist, create if needed"""
        logger.info(f"Checking {db_name}...")
        
        admin_conn = await asyncpg.connect(**self.admin_config)
        
        try:
            # Check if user exists
            user_exists = await admin_conn.fetchval(
                "SELECT 1 FROM pg_roles WHERE rolname = $1",
                db_config['user']
            )
            
            if not user_exists:
                logger.info(f"Creating user {db_config['user']}...")
                await admin_conn.execute(f"""
                    CREATE USER "{db_config['user']}" WITH PASSWORD '{db_config['password']}'
                """)
                logger.info(f"[OK] Created user {db_config['user']}")
            else:
                logger.info(f"[OK] User {db_config['user']} exists")
            
            # Check if database exists
            db_exists = await admin_conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1",
                db_config['database']
            )
            
            if not db_exists:
                logger.info(f"Creating database {db_config['database']}...")
                await admin_conn.execute(f"""
                    CREATE DATABASE "{db_config['database']}" OWNER "{db_config['user']}"
                """)
                logger.info(f"[OK] Created database {db_config['database']}")
            else:
                logger.info(f"[OK] Database {db_config['database']} exists")
            
            # Grant privileges
            await admin_conn.execute(f"""
                GRANT ALL PRIVILEGES ON DATABASE "{db_config['database']}" TO "{db_config['user']}"
            """)
            
            # Test connection to the database
            test_config = {
                'host': 'localhost',
                'port': 5432,
                'database': db_config['database'],
                'user': db_config['user'],
                'password': db_config['password']
            }
            
            test_conn = await asyncpg.connect(**test_config)
            await test_conn.close()
            logger.info(f"[OK] {db_name} connection test successful")
            
        finally:
            await admin_conn.close()
    
    async def create_sample_data(self):
        """Create some sample data in the legacy database for testing"""
        logger.info("Creating sample data in legacy database...")
        
        legacy_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'poc',
            'user': 'poc_user',
            'password': 'admin123'
        }
        
        conn = await asyncpg.connect(**legacy_config)
        
        try:
            # Create tables if they don't exist (simplified version)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    uid VARCHAR(255) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE,
                    display_name VARCHAR(255),
                    role VARCHAR(50) DEFAULT 'user',
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    image_url VARCHAR(500),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    price DECIMAL(10,2) NOT NULL,
                    mrp DECIMAL(10,2),
                    category_id INTEGER REFERENCES categories(id),
                    image_url VARCHAR(500),
                    stock_quantity INTEGER DEFAULT 0,
                    unit VARCHAR(20),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Insert sample data if tables are empty
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            if user_count == 0:
                await conn.execute("""
                    INSERT INTO users (uid, email, display_name, role) VALUES
                    ('user1', 'user1@example.com', 'Test User 1', 'user'),
                    ('user2', 'user2@example.com', 'Test User 2', 'user'),
                    ('admin1', 'admin@example.com', 'Admin User', 'admin')
                """)
                logger.info("[OK] Created sample users")
            
            category_count = await conn.fetchval("SELECT COUNT(*) FROM categories")
            if category_count == 0:
                await conn.execute("""
                    INSERT INTO categories (name, is_active) VALUES
                    ('Electronics', true),
                    ('Books', true),
                    ('Clothing', true)
                """)
                logger.info("[OK] Created sample categories")
            
            product_count = await conn.fetchval("SELECT COUNT(*) FROM products")
            if product_count == 0:
                await conn.execute("""
                    INSERT INTO products (name, description, price, mrp, category_id, stock_quantity, unit) VALUES
                    ('Laptop', 'Gaming laptop', 999.99, 1199.99, 1, 10, 'piece'),
                    ('Python Book', 'Learn Python programming', 29.99, 39.99, 2, 50, 'piece'),
                    ('T-Shirt', 'Cotton t-shirt', 19.99, 24.99, 3, 100, 'piece')
                """)
                logger.info("[OK] Created sample products")
            
        finally:
            await conn.close()

async def main():
    """Main entry point"""
    try:
        checker = DatabaseChecker()
        
        # Check and setup databases
        success = await checker.check_all_databases()
        
        if success:
            # Optionally create sample data
            create_sample = input("\nCreate sample data in legacy database for testing? (y/N): ").lower().strip()
            if create_sample == 'y':
                await checker.create_sample_data()
            
            logger.info("\n[SUCCESS] Database setup complete! You can now run the migration.")
        else:
            logger.error("\n[FAILED] Database setup failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Setup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Database Setup Checker")
    print("======================")
    print("This script will check and create the required databases and users.")
    print("Make sure PostgreSQL is running and you have admin access.")
    print()
    
    # Allow user to update admin credentials
    admin_user = input("PostgreSQL admin username (default: postgres): ").strip() or "postgres"
    admin_pass = input("PostgreSQL admin password (default: postgres): ").strip() or "postgres"
    
    DatabaseConfig.POSTGRES_ADMIN['user'] = admin_user
    DatabaseConfig.POSTGRES_ADMIN['password'] = admin_pass
    
    asyncio.run(main())