#!/usr/bin/env python3
"""
Health Check Test Script

This script tests the health check functionality for all services.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add auth service to path
auth_path = Path(__file__).parent / "auth_service"
sys.path.insert(0, str(auth_path))

async def test_auth_health_check():
    """Test Auth Service health check function"""
    try:
        # Change to auth service directory
        os.chdir(auth_path)
        
        from app.database import check_database_health
        
        print("🔐 Testing Auth Service health check function...")
        is_healthy = await check_database_health()
        
        if is_healthy:
            print("✅ Auth Service health check: SUCCESS")
            return True
        else:
            print("❌ Auth Service health check: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Auth Service health check: ERROR - {e}")
        return False

async def main():
    """Run health check test"""
    print("🚀 Testing health check functionality...\n")
    
    result = await test_auth_health_check()
    
    if result:
        print("\n🎉 Health check functionality is working!")
        return 0
    else:
        print("\n⚠️ Health check functionality failed.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)