#!/usr/bin/env python3
"""
Migration Rollback Script

This script provides rollback capabilities for the database migration process.
It can restore databases from backups and clean up migration artifacts.
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration for rollback"""
    
    LEGACY_DB = {
        'host': 'localhost',
        'port': 5432,
        'database': 'poc',
        'user': 'poc_user',
        'password': 'admin123'
    }
    
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

class MigrationRollback:
    """Handles migration rollback operations"""
    
    def __init__(self):
        self.migration_dir = Path(__file__).parent
        self.backup_dir = self.migration_dir / 'backups'
        self.data_dir = self.migration_dir / 'migration_data'
        
    async def run_rollback(self, rollback_type: str = 'full'):
        """Run rollback process"""
        logger.info(f"Starting {rollback_type} rollback process...")
        
        try:
            if rollback_type == 'full':
                await self.full_rollback()
            elif rollback_type == 'data_only':
                await self.data_rollback()
            elif rollback_type == 'cleanup_only':
                await self.cleanup_migration_artifacts()
            else:
                raise ValueError(f"Unknown rollback type: {rollback_type}")
            
            logger.info("Rollback completed successfully!")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise
    
    async def full_rollback(self):
        """Complete rollback including database restoration"""
        logger.info("Performing full rollback...")
        
        # Step 1: Find latest backups
        backup_files = await self.find_latest_backups()
        
        # Step 2: Restore databases from backups
        await self.restore_databases(backup_files)
        
        # Step 3: Clean up migration artifacts
        await self.cleanup_migration_artifacts()
        
        # Step 4: Validate rollback
        await self.validate_rollback()
    
    async def data_rollback(self):
        """Rollback only migrated data, keep schema changes"""
        logger.info("Performing data-only rollback...")
        
        # Clear migrated data from new databases
        await self.clear_migrated_data()
        
        # Clean up migration artifacts
        await self.cleanup_migration_artifacts()
    
    async def find_latest_backups(self) -> Dict[str, Path]:
        """Find the latest backup files for each database"""
        logger.info("Finding latest backup files...")
        
        backup_files = {}
        
        if not self.backup_dir.exists():
            raise Exception("Backup directory not found. Cannot perform rollback.")
        
        # Find latest backup for each database
        for db_name in ['legacy_db', 'auth_db', 'product_db', 'cart_db', 'promotion_db']:
            pattern = f"{db_name}_backup_*.sql"
            matching_files = list(self.backup_dir.glob(pattern))
            
            if matching_files:
                # Sort by modification time and get the latest
                latest_backup = max(matching_files, key=lambda f: f.stat().st_mtime)
                backup_files[db_name] = latest_backup
                logger.info(f"Found backup for {db_name}: {latest_backup.name}")
            else:
                logger.warning(f"No backup found for {db_name}")
        
        return backup_files
    
    async def restore_databases(self, backup_files: Dict[str, Path]):
        """Restore databases from backup files"""
        logger.info("Restoring databases from backups...")
        
        # Database mapping
        db_configs = {
            'legacy_db': DatabaseConfig.LEGACY_DB,
            'auth_db': DatabaseConfig.AUTH_DB,
            'product_db': DatabaseConfig.PRODUCT_DB,
            'cart_db': DatabaseConfig.CART_DB,
            'promotion_db': DatabaseConfig.PROMOTION_DB
        }
        
        for db_name, backup_file in backup_files.items():
            if db_name in db_configs:
                await self.restore_single_database(db_configs[db_name], backup_file)
    
    async def restore_single_database(self, db_config: Dict, backup_file: Path):
        """Restore a single database from backup"""
        logger.info(f"Restoring {db_config['database']} from {backup_file.name}...")
        
        try:
            # Drop and recreate database
            await self.recreate_database(db_config)
            
            # Restore from backup
            cmd = [
                'psql',
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
                logger.info(f"[OK] Restored {db_config['database']}")
            else:
                raise Exception(f"Restore failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Failed to restore {db_config['database']}: {e}")
            raise
    
    async def recreate_database(self, db_config: Dict):
        """Drop and recreate a database"""
        # Connect to postgres database to drop/create target database
        postgres_config = db_config.copy()
        postgres_config['database'] = 'postgres'
        
        conn = await asyncpg.connect(**postgres_config)
        
        try:
            # Terminate existing connections
            await conn.execute(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{db_config['database']}'
                AND pid <> pg_backend_pid()
            """)
            
            # Drop database
            await conn.execute(f'DROP DATABASE IF EXISTS "{db_config["database"]}"')
            
            # Create database
            await conn.execute(f'CREATE DATABASE "{db_config["database"]}" OWNER "{db_config["user"]}"')
            
            logger.info(f"[OK] Recreated database {db_config['database']}")
            
        finally:
            await conn.close()
    
    async def clear_migrated_data(self):
        """Clear migrated data from new databases"""
        logger.info("Clearing migrated data...")
        
        # Clear auth database
        await self.clear_database_data(DatabaseConfig.AUTH_DB, [
            'user_sessions', 'user_profiles', 'users'
        ])
        
        # Clear product database
        await self.clear_database_data(DatabaseConfig.PRODUCT_DB, [
            'product_inventory', 'product_images', 'product_variants', 'products', 'categories'
        ])
        
        # Clear cart database
        await self.clear_database_data(DatabaseConfig.CART_DB, [
            'cart_view', 'saved_carts', 'reference_validation_log',
            'wishlist_items', 'wishlists', 'cart_items', 'carts'
        ])
        
        # Clear promotion database
        await self.clear_database_data(DatabaseConfig.PROMOTION_DB, [
            'promo_suggestions', 'promo_analytics', 'user_promo_eligibility',
            'campaign_promo_codes', 'promotion_campaigns', 'promo_usage', 'promo_codes'
        ])
    
    async def clear_database_data(self, db_config: Dict, tables: List[str]):
        """Clear data from specific tables in a database"""
        conn = await asyncpg.connect(**db_config)
        
        try:
            # Disable foreign key checks temporarily
            await conn.execute("SET session_replication_role = replica")
            
            for table in tables:
                try:
                    await conn.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
                    logger.info(f"[OK] Cleared table {table} in {db_config['database']}")
                except Exception as e:
                    logger.warning(f"Could not clear table {table}: {e}")
            
            # Re-enable foreign key checks
            await conn.execute("SET session_replication_role = DEFAULT")
            
        finally:
            await conn.close()
    
    async def cleanup_migration_artifacts(self):
        """Clean up migration artifacts and temporary files"""
        logger.info("Cleaning up migration artifacts...")
        
        # Remove CSV data files
        if self.data_dir.exists():
            for csv_file in self.data_dir.glob('*.csv'):
                try:
                    csv_file.unlink()
                    logger.info(f"[OK] Removed {csv_file.name}")
                except Exception as e:
                    logger.warning(f"Could not remove {csv_file.name}: {e}")
        
        # Remove log files older than current session
        log_files = list(self.migration_dir.glob('migration_*.log'))
        if len(log_files) > 1:
            # Keep only the most recent log file
            log_files.sort(key=lambda f: f.stat().st_mtime)
            for old_log in log_files[:-1]:
                try:
                    old_log.unlink()
                    logger.info(f"[OK] Removed old log {old_log.name}")
                except Exception as e:
                    logger.warning(f"Could not remove {old_log.name}: {e}")
    
    async def validate_rollback(self):
        """Validate that rollback was successful"""
        logger.info("Validating rollback...")
        
        # Check if databases are accessible
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
                
                # Check if database has expected structure
                tables = await conn.fetch("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                
                table_count = len(tables)
                await conn.close()
                
                logger.info(f"[OK] {name} database accessible with {table_count} tables")
                
            except Exception as e:
                logger.error(f"[ERROR] {name} database validation failed: {e}")
                raise Exception(f"Rollback validation failed for {name} database")

def print_usage():
    """Print usage information"""
    print("""
Usage: python rollback_migration.py [rollback_type]

Rollback Types:
  full        - Complete rollback including database restoration (default)
  data_only   - Rollback only migrated data, keep schema changes
  cleanup_only - Clean up migration artifacts only

Examples:
  python rollback_migration.py
  python rollback_migration.py full
  python rollback_migration.py data_only
  python rollback_migration.py cleanup_only
""")

async def main():
    """Main entry point"""
    rollback_type = 'full'
    
    if len(sys.argv) > 1:
        rollback_type = sys.argv[1]
        
        if rollback_type in ['-h', '--help', 'help']:
            print_usage()
            sys.exit(0)
        
        if rollback_type not in ['full', 'data_only', 'cleanup_only']:
            print(f"Error: Unknown rollback type '{rollback_type}'")
            print_usage()
            sys.exit(1)
    
    try:
        rollback = MigrationRollback()
        await rollback.run_rollback(rollback_type)
        
        logger.info("Rollback completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Rollback interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())