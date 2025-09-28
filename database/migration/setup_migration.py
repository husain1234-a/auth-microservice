#!/usr/bin/env python3
"""
Migration Setup Script

This script sets up the environment for database migration.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install required Python dependencies"""
    print("Installing migration dependencies...")
    
    requirements_file = Path(__file__).parent / 'requirements.txt'
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ])
        print("[OK] Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install dependencies: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories for migration"""
    print("Creating migration directories...")
    
    migration_dir = Path(__file__).parent
    directories = [
        migration_dir / 'migration_data',
        migration_dir / 'backups'
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"[OK] Created directory: {directory}")

def check_postgresql():
    """Check if PostgreSQL client tools are available"""
    print("Checking PostgreSQL client tools...")
    
    tools = ['psql', 'pg_dump']
    
    for tool in tools:
        try:
            subprocess.run([tool, '--version'], check=True, capture_output=True)
            print(f"[OK] {tool} is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"[ERROR] {tool} not found. Please install PostgreSQL client tools.")
            return False
    
    return True

def main():
    """Main setup function"""
    print("Setting up migration environment...")
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Check PostgreSQL tools
    if not check_postgresql():
        print("\nPlease install PostgreSQL client tools and run this script again.")
        sys.exit(1)
    
    print("\n[SUCCESS] Migration environment setup completed!")
    print("\nNext steps:")
    print("1. Check/create databases: python check_databases.py")
    print("2. Run migration: python migrate_data.py")
    print("3. Validate: python validate_migration.py")

if __name__ == "__main__":
    main()