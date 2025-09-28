#!/usr/bin/env python3
"""
Data Migration Script for Microservices Database Separation

This script orchestrates the migration from a monolithic database to 
separate service databases with proper validation and rollback capabilities.
"""

import os
import sys
import asyncio
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import asyncpg
import psycopg2
from psycopg2 import sql

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration for migration"""
    
    # Legacy monolithic database
    LEGACY_DB = {
        'host': 'localhost',
        'port': 5432,
        'database': 'poc',
        'user': 'poc_user',
        'password': 'admin123'
    }
    
    # New service databases
    AUTH_DB = {
        'host': 'localhost',
        'port': 5432,
        'database': 'auth_db',
        'user': 'auth_user',
        'password': 'auth_pass123'
    }
    
    PRODUCT_DB = {
        'host': 'localhost',
        'port': 5432,
        'database': 'product_db',
        'user': 'product_user',
        'password': 'product_pass123'
    }
    
    CART_DB = {
        'host': 'localhost',
        'port': 5432,
        'database': 'cart_db',
        'user': 'cart_user',
        'password': 'cart_pass123'
    }
    
    PROMOTION_DB = {
        'host': 'localhost',
        'port': 5432,
        'database': 'promotion_db',
        'user': 'promotion_user',
        'password': 'promotion_pass123'
    }

class MigrationOrchestrator:
    """Main migration orchestrator"""
    
    def __init__(self):
        self.migration_dir = Path(__file__).parent
        self.data_dir = self.migration_dir / 'migration_data'
        self.backup_dir = self.migration_dir / 'backups'
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        self.migration_steps = [
            ('auth', 'Auth Service Migration'),
            ('product', 'Product Service Migration'),
            ('cart', 'Cart Service Migration'),
            ('promotion', 'Promotion Service Migration')
        ]
    
    async def run_migration(self):
        """Run the complete migration process"""
        logger.info("Starting database migration process...")
        
        try:
            # Step 1: Validate prerequisites
            await self.validate_prerequisites()
            
            # Step 2: Create backups
            await self.create_backups()
            
            # Step 3: Extract data from legacy database
            await self.extract_data()
            
            # Step 4: Migrate data to new databases
            await self.migrate_data()
            
            # Step 5: Validate migration
            await self.validate_migration()
            
            logger.info("Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            logger.info("Starting rollback process...")
            await self.rollback_migration()
            raise
    
    async def validate_prerequisites(self):
        """Validate that all prerequisites are met"""
        logger.info("Validating prerequisites...")
        
        # Check if all databases are accessible
        databases = [
            ('Legacy', DatabaseConfig.LEGACY_DB),
            ('Auth', DatabaseConfig.AUTH_DB),
            ('Product', DatabaseConfig.PRODUCT_DB),
            ('Cart', DatabaseConfig.CART_DB),
            ('Promotion', DatabaseConfig.PROMOTION_DB)
        ]
        
        for name, config in databases:
            try:
                conn = await asyncpg.connect(**config)
                await conn.close()
                logger.info(f"[OK] {name} database connection successful")
            except Exception as e:
                raise Exception(f"Cannot connect to {name} database: {e}")
        
        # Check if psql is available
        try:
            subprocess.run(['psql', '--version'], check=True, capture_output=True)
            logger.info("[OK] psql command available")
        except subprocess.CalledProcessError:
            raise Exception("psql command not found. Please install PostgreSQL client.")
    
    async def create_backups(self):
        """Create backups of all databases before migration"""
        logger.info("Creating database backups...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup legacy database
        backup_file = self.backup_dir / f"legacy_db_backup_{timestamp}.sql"
        await self.create_database_backup(DatabaseConfig.LEGACY_DB, backup_file)
        
        # Backup new databases (in case they have existing data)
        for service, config in [
            ('auth', DatabaseConfig.AUTH_DB),
            ('product', DatabaseConfig.PRODUCT_DB),
            ('cart', DatabaseConfig.CART_DB),
            ('promotion', DatabaseConfig.PROMOTION_DB)
        ]:
            backup_file = self.backup_dir / f"{service}_db_backup_{timestamp}.sql"
            await self.create_database_backup(config, backup_file)
    
    async def create_database_backup(self, db_config: Dict, backup_file: Path):
        """Create a backup of a specific database"""
        try:
            cmd = [
                'pg_dump',
                '-h', db_config['host'],
                '-p', str(db_config['port']),
                '-U', db_config['user'],
                '-d', db_config['database'],
                '-f', str(backup_file),
                '--no-password'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['password']
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"[OK] Backup created: {backup_file}")
            else:
                raise Exception(f"Backup failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Failed to create backup for {db_config['database']}: {e}")
            raise
    
    async def extract_data(self):
        """Extract data from legacy database"""
        logger.info("Extracting data from legacy database...")
        
        extraction_scripts = [
            'extract_auth_data.sql',
            'extract_product_data.sql',
            'extract_cart_data.sql',
            'extract_promotion_data.sql'
        ]
        
        for script in extraction_scripts:
            script_path = self.migration_dir / script
            if script_path.exists():
                await self.run_sql_script(DatabaseConfig.LEGACY_DB, script_path)
                logger.info(f"[OK] Executed {script}")
            else:
                logger.warning(f"Script not found: {script}")
    
    async def run_sql_script(self, db_config: Dict, script_path: Path):
        """Run a SQL script against a database"""
        try:
            cmd = [
                'psql',
                '-h', db_config['host'],
                '-p', str(db_config['port']),
                '-U', db_config['user'],
                '-d', db_config['database'],
                '-f', str(script_path),
                '--no-password'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['password']
            
            # Change to migration directory for relative paths in SQL scripts
            result = subprocess.run(
                cmd, 
                env=env, 
                capture_output=True, 
                text=True,
                cwd=self.migration_dir
            )
            
            if result.returncode != 0:
                raise Exception(f"Script execution failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Failed to run script {script_path}: {e}")
            raise
    
    async def migrate_data(self):
        """Migrate extracted data to new databases"""
        logger.info("Migrating data to new databases...")
        
        # Migration mappings: (csv_files, target_db_config)
        migrations = [
            (['users.csv', 'user_profiles.csv'], DatabaseConfig.AUTH_DB),
            (['categories.csv', 'products.csv', 'product_inventory.csv'], DatabaseConfig.PRODUCT_DB),
            (['carts.csv', 'cart_items.csv', 'wishlists.csv', 'wishlist_items.csv'], DatabaseConfig.CART_DB),
            (['promo_codes.csv', 'promo_usage.csv'], DatabaseConfig.PROMOTION_DB)
        ]
        
        for csv_files, db_config in migrations:
            await self.load_csv_data(csv_files, db_config)
    
    async def load_csv_data(self, csv_files: List[str], db_config: Dict):
        """Load CSV data into a database"""
        conn = await asyncpg.connect(**db_config)
        
        try:
            for csv_file in csv_files:
                csv_path = self.data_dir / csv_file
                
                if not csv_path.exists():
                    logger.warning(f"CSV file not found: {csv_file}")
                    continue
                
                # Determine table name from CSV file name
                table_name = csv_file.replace('.csv', '')
                
                # Read CSV and insert data
                await self.insert_csv_data(conn, csv_path, table_name)
                logger.info(f"[OK] Loaded {csv_file} into {table_name}")
                
        finally:
            await conn.close()
    
    async def insert_csv_data(self, conn: asyncpg.Connection, csv_path: Path, table_name: str):
        """Insert CSV data into a specific table"""
        try:
            # Use COPY command for efficient bulk insert
            with open(csv_path, 'r') as f:
                # Skip header line
                header = f.readline().strip()
                columns = [col.strip() for col in header.split(',')]
                
                # Create COPY command
                copy_sql = f"COPY {table_name} ({','.join(columns)}) FROM STDIN WITH CSV HEADER"
                
                # Reset file pointer to beginning
                f.seek(0)
                
                # Execute COPY
                await conn.copy_from_table(table_name, source=f, format='csv', header=True)
                
        except Exception as e:
            logger.error(f"Failed to insert data from {csv_path}: {e}")
            raise
    
    async def validate_migration(self):
        """Validate that migration was successful"""
        logger.info("Validating migration...")
        
        # Run validation script
        validation_script = self.migration_dir / 'validate_migration.py'
        if validation_script.exists():
            result = subprocess.run([sys.executable, str(validation_script)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("[OK] Migration validation passed")
            else:
                raise Exception(f"Migration validation failed: {result.stderr}")
        else:
            logger.warning("Validation script not found, skipping validation")
    
    async def rollback_migration(self):
        """Rollback migration in case of failure"""
        logger.info("Rolling back migration...")
        
        # Run rollback script
        rollback_script = self.migration_dir / 'rollback_migration.py'
        if rollback_script.exists():
            result = subprocess.run([sys.executable, str(rollback_script)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("[OK] Rollback completed")
            else:
                logger.error(f"Rollback failed: {result.stderr}")
        else:
            logger.warning("Rollback script not found")

async def main():
    """Main entry point"""
    try:
        orchestrator = MigrationOrchestrator()
        await orchestrator.run_migration()
        
    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())