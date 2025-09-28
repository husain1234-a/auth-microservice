#!/usr/bin/env python3
"""
Database Connection Test Script

This script tests connections to all the microservice databases
to verify they are properly configured and accessible.
"""

import asyncio
import asyncpg
import sys
from typing import Dict, List

# Database configurations (Local PostgreSQL)
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

async def test_database_connection(db_name: str, config: Dict[str, str]) -> Dict[str, any]:
    """Test connection to a single database."""
    result = {
        'name': db_name,
        'status': 'unknown',
        'error': None,
        'tables': [],
        'connection_string': f"postgresql://{config['user']}@{config['host']}:{config['port']}/{config['database']}"
    }
    
    try:
        # Create connection
        conn = await asyncpg.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        
        # Test basic query
        version = await conn.fetchval('SELECT version()')
        
        # Get table list
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        result['status'] = 'connected'
        result['tables'] = [table['table_name'] for table in tables]
        result['version'] = version
        
        await conn.close()
        
    except Exception as e:
        result['status'] = 'failed'
        result['error'] = str(e)
    
    return result

async def test_all_databases() -> List[Dict[str, any]]:
    """Test connections to all databases."""
    tasks = []
    for db_name, config in DATABASES.items():
        tasks.append(test_database_connection(db_name, config))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle any exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            db_name = list(DATABASES.keys())[i]
            processed_results.append({
                'name': db_name,
                'status': 'error',
                'error': str(result),
                'tables': []
            })
        else:
            processed_results.append(result)
    
    return processed_results

def print_results(results: List[Dict[str, any]]):
    """Print test results in a formatted way."""
    print("=" * 80)
    print("DATABASE CONNECTION TEST RESULTS")
    print("=" * 80)
    
    success_count = 0
    total_count = len(results)
    
    for result in results:
        status_symbol = "✓" if result['status'] == 'connected' else "✗"
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
        return False

async def main():
    """Main function."""
    print("Testing database connections...")
    print("Make sure PostgreSQL is running and databases are created.")
    print("Run 'database/start_databases.bat' first if you haven't already.")
    print()
    
    results = await test_all_databases()
    success = print_results(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)