#!/usr/bin/env python3
"""
Simple Database Verification Script

This script verifies the database setup using basic psycopg2
which is more commonly available than asyncpg.
"""

import sys
import subprocess
from typing import Dict, List

# Database configurations
DATABASES = {
    'auth_db': {
        'host': 'localhost',
        'port': 5432,
        'user': 'auth_user',
        'password': 'auth_pass123',
        'database': 'auth_db'
    },
    'product_db': {
        'host': 'localhost',
        'port': 5432,
        'user': 'product_user',
        'password': 'product_pass123',
        'database': 'product_db'
    },
    'cart_db': {
        'host': 'localhost',
        'port': 5432,
        'user': 'cart_user',
        'password': 'cart_pass123',
        'database': 'cart_db'
    },
    'promotion_db': {
        'host': 'localhost',
        'port': 5432,
        'user': 'promotion_user',
        'password': 'promotion_pass123',
        'database': 'promotion_db'
    },
    'legacy_db': {
        'host': 'localhost',
        'port': 5432,
        'user': 'poc_user',
        'password': 'admin123',
        'database': 'poc'
    }
}

def test_psql_connection(db_name: str, config: Dict[str, str]) -> Dict[str, any]:
    """Test connection using psql command."""
    result = {
        'name': db_name,
        'status': 'unknown',
        'error': None,
        'tables': [],
        'connection_string': f"postgresql://{config['user']}@{config['host']}:{config['port']}/{config['database']}"
    }
    
    try:
        # Set PGPASSWORD environment variable for psql
        env = {'PGPASSWORD': config['password']}
        
        # Test connection with a simple query
        cmd = [
            'psql',
            '-h', config['host'],
            '-p', str(config['port']),
            '-U', config['user'],
            '-d', config['database'],
            '-t',  # tuples only
            '-c', 'SELECT version();'
        ]
        
        process = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if process.returncode == 0:
            result['status'] = 'connected'
            result['version'] = process.stdout.strip()
            
            # Get table list
            table_cmd = [
                'psql',
                '-h', config['host'],
                '-p', str(config['port']),
                '-U', config['user'],
                '-d', config['database'],
                '-t',
                '-c', "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
            ]
            
            table_process = subprocess.run(
                table_cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if table_process.returncode == 0:
                tables = [line.strip() for line in table_process.stdout.split('\n') if line.strip()]
                result['tables'] = tables
        else:
            result['status'] = 'failed'
            result['error'] = process.stderr.strip() or process.stdout.strip()
            
    except subprocess.TimeoutExpired:
        result['status'] = 'timeout'
        result['error'] = 'Connection timeout'
    except FileNotFoundError:
        result['status'] = 'no_psql'
        result['error'] = 'psql command not found. Please install PostgreSQL client.'
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
    
    return result

def test_all_databases() -> List[Dict[str, any]]:
    """Test connections to all databases."""
    results = []
    for db_name, config in DATABASES.items():
        print(f"Testing {db_name}...", end=' ')
        result = test_psql_connection(db_name, config)
        
        if result['status'] == 'connected':
            print("✅")
        else:
            print("❌")
            
        results.append(result)
    
    return results

def print_results(results: List[Dict[str, any]]):
    """Print test results in a formatted way."""
    print("\n" + "=" * 80)
    print("DATABASE VERIFICATION RESULTS")
    print("=" * 80)
    
    success_count = 0
    total_count = len(results)
    
    for result in results:
        status_symbol = "✅" if result['status'] == 'connected' else "❌"
        print(f"\n{status_symbol} {result['name'].upper()}")
        print(f"   Connection: {result.get('connection_string', 'N/A')}")
        print(f"   Status: {result['status']}")
        
        if result['status'] == 'connected':
            success_count += 1
            print(f"   Tables: {len(result['tables'])} found")
            if result['tables']:
                print(f"   Table List: {', '.join(result['tables'])}")
        elif result['error']:
            print(f"   Error: {result['error']}")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {success_count}/{total_count} databases connected successfully")
    
    if success_count == total_count:
        print("🎉 All databases are properly configured and accessible!")
        return True
    else:
        print("⚠️  Some databases failed to connect. Check the errors above.")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure PostgreSQL is running")
        print("   2. Run the setup script: database/start_databases.bat")
        print("   3. Check if psql is in your PATH")
        print("   4. Verify database credentials")
        return False

def main():
    """Main function."""
    print("🔍 Verifying database setup...")
    print("Make sure PostgreSQL is running and databases are created.")
    print()
    
    results = test_all_databases()
    success = print_results(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nVerification interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)