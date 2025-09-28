#!/usr/bin/env python3
"""
Install Dependencies Script

This script installs the required Python packages for database testing
and management without Docker.
"""

import subprocess
import sys

def install_package(package):
    """Install a Python package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Main function to install required packages."""
    print("🔧 Installing required Python packages for database management...")
    print("=" * 60)
    
    # Required packages
    packages = [
        "asyncpg",  # PostgreSQL async driver
        "psycopg2-binary",  # PostgreSQL sync driver (backup)
        "python-dotenv",  # Environment variable management
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for package in packages:
        print(f"\nInstalling {package}...")
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Installation Summary: {success_count}/{total_count} packages installed successfully")
    
    if success_count == total_count:
        print("🎉 All dependencies installed successfully!")
        print("\nYou can now run:")
        print("  - database/start_databases.bat (Windows)")
        print("  - database/start_databases.sh (Linux/Mac)")
        print("  - python database/test_connections.py")
    else:
        print("⚠️  Some packages failed to install. Please check the errors above.")
        print("You may need to install PostgreSQL development headers:")
        print("  - Ubuntu/Debian: sudo apt-get install libpq-dev python3-dev")
        print("  - CentOS/RHEL: sudo yum install postgresql-devel python3-devel")
        print("  - macOS: brew install postgresql")
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nInstallation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)