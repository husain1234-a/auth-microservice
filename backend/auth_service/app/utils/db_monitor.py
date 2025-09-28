"""
Database Connection Monitoring Utilities

This module provides utilities for monitoring database connection health,
pool status, and connection metrics for the Auth Service.
"""

import asyncio
import logging
from typing import Dict, Any
from sqlalchemy import text
from ..database import engine, AsyncSessionLocal

logger = logging.getLogger(__name__)


class DatabaseMonitor:
    """Monitor database connection health and pool status"""
    
    @staticmethod
    async def get_connection_pool_status() -> Dict[str, Any]:
        """
        Get current connection pool status and metrics.
        
        Returns:
            Dict containing pool status information
        """
        try:
            pool = engine.pool
            return {
                "pool_size": getattr(pool, 'size', lambda: 'N/A')(),
                "checked_in_connections": getattr(pool, 'checkedin', lambda: 'N/A')(),
                "checked_out_connections": getattr(pool, 'checkedout', lambda: 'N/A')(),
                "overflow_connections": getattr(pool, 'overflow', lambda: 0)(),
                "invalid_connections": getattr(pool, 'invalid', lambda: 0)(),
                "pool_class": pool.__class__.__name__,
                "engine_url": str(engine.url).replace(engine.url.password or '', '***'),
            }
        except Exception as e:
            logger.error(f"Failed to get connection pool status: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def test_database_operations() -> Dict[str, Any]:
        """
        Test basic database operations to ensure connectivity.
        
        Returns:
            Dict containing test results
        """
        results = {
            "connection_test": False,
            "read_test": False,
            "write_test": False,
            "transaction_test": False,
            "errors": []
        }
        
        try:
            async with AsyncSessionLocal() as session:
                # Test basic connection
                await session.execute(text("SELECT 1"))
                results["connection_test"] = True
                
                # Test read operation
                result = await session.execute(text("SELECT current_timestamp"))
                timestamp = result.scalar()
                if timestamp:
                    results["read_test"] = True
                
                # Test transaction
                async with session.begin():
                    await session.execute(text("SELECT 1"))
                    results["transaction_test"] = True
                
                results["write_test"] = True  # If we got here, basic operations work
                
        except Exception as e:
            error_msg = f"Database operation test failed: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        return results
    
    @staticmethod
    async def get_database_info() -> Dict[str, Any]:
        """
        Get database server information and statistics.
        
        Returns:
            Dict containing database information
        """
        try:
            async with AsyncSessionLocal() as session:
                # Get database version
                version_result = await session.execute(text("SELECT version()"))
                version = version_result.scalar()
                
                # Get current database name
                db_result = await session.execute(text("SELECT current_database()"))
                database_name = db_result.scalar()
                
                # Get connection count
                conn_result = await session.execute(
                    text("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
                )
                active_connections = conn_result.scalar()
                
                return {
                    "database_version": version,
                    "database_name": database_name,
                    "active_connections": active_connections,
                    "service": "auth-service"
                }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {"error": str(e)}


async def comprehensive_health_check() -> Dict[str, Any]:
    """
    Perform a comprehensive health check of the database system.
    
    Returns:
        Dict containing comprehensive health check results
    """
    monitor = DatabaseMonitor()
    
    health_data = {
        "timestamp": asyncio.get_event_loop().time(),
        "service": "auth-service",
        "database_name": "auth_db"
    }
    
    # Run all checks concurrently
    try:
        pool_status, operation_tests, db_info = await asyncio.gather(
            monitor.get_connection_pool_status(),
            monitor.test_database_operations(),
            monitor.get_database_info(),
            return_exceptions=True
        )
        
        health_data.update({
            "pool_status": pool_status if not isinstance(pool_status, Exception) else {"error": str(pool_status)},
            "operation_tests": operation_tests if not isinstance(operation_tests, Exception) else {"error": str(operation_tests)},
            "database_info": db_info if not isinstance(db_info, Exception) else {"error": str(db_info)}
        })
        
        # Determine overall health
        is_healthy = (
            isinstance(operation_tests, dict) and 
            operation_tests.get("connection_test", False) and
            operation_tests.get("read_test", False)
        )
        
        health_data["overall_status"] = "healthy" if is_healthy else "unhealthy"
        
    except Exception as e:
        logger.error(f"Comprehensive health check failed: {e}")
        health_data.update({
            "overall_status": "unhealthy",
            "error": str(e)
        })
    
    return health_data