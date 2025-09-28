"""
Dual-Write Management API Endpoints

Provides endpoints for monitoring and controlling dual-write behavior
during the database migration process.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging

from app.services.cart_service import CartService
from app.core.database import get_dual_write_manager
from app.core.dual_write_manager import CartDualWriteManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dual-write", tags=["dual-write"])


@router.get("/status")
async def get_dual_write_status() -> Dict[str, Any]:
    """
    Get dual-write status and configuration.
    
    Returns information about dual-write configuration,
    database health, and synchronization status.
    """
    try:
        cart_service = CartService()
        status = await cart_service.get_dual_write_status()
        return status
    except Exception as e:
        logger.error(f"Error getting dual-write status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_dual_write_health() -> Dict[str, Any]:
    """
    Get detailed health information for both databases.
    
    Returns connection status, pool metrics, and operational tests
    for both new and legacy databases.
    """
    try:
        dual_write_manager = get_dual_write_manager()
        
        if not dual_write_manager:
            return {
                "dual_write_enabled": False,
                "message": "Dual-write not configured"
            }
        
        health_status = await dual_write_manager.health_check()
        return {
            "dual_write_enabled": True,
            "health_check": health_status,
            "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
        }
    except Exception as e:
        logger.error(f"Error getting dual-write health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-sync/{user_id}")
async def validate_user_cart_sync(user_id: str) -> Dict[str, Any]:
    """
    Validate synchronization of a user's cart between databases.
    
    Args:
        user_id: User ID to validate cart synchronization for
        
    Returns:
        Validation results including any differences found
    """
    try:
        dual_write_manager = get_dual_write_manager()
        
        if not dual_write_manager:
            raise HTTPException(
                status_code=400, 
                detail="Dual-write not enabled"
            )
        
        # Validate cart synchronization
        cart_sync_result = await dual_write_manager.validate_cart_sync(user_id)
        
        return {
            "user_id": user_id,
            "cart_synchronized": cart_sync_result,
            "validation_timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error validating cart sync for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-user")
async def sync_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manually sync user data to cart service database.
    
    This endpoint can be used to synchronize user data changes
    from the auth service to the cart service database.
    
    Args:
        user_data: User data to synchronize
        
    Returns:
        Synchronization result
    """
    try:
        if "uid" not in user_data:
            raise HTTPException(
                status_code=400,
                detail="User data must include 'uid' field"
            )
        
        cart_service = CartService()
        result = await cart_service.sync_user_data(user_data)
        
        return {
            "success": result["success"],
            "user_id": user_data["uid"],
            "sync_result": result
        }
    except Exception as e:
        logger.error(f"Error syncing user data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_dual_write_metrics() -> Dict[str, Any]:
    """
    Get dual-write operation metrics.
    
    Returns metrics about dual-write operations including
    success rates, error counts, and performance data.
    """
    try:
        dual_write_manager = get_dual_write_manager()
        
        if not dual_write_manager:
            return {
                "dual_write_enabled": False,
                "message": "Dual-write not configured"
            }
        
        # This would return actual metrics in a real implementation
        # For now, return placeholder data
        return {
            "dual_write_enabled": True,
            "metrics": {
                "total_operations": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "success_rate": 0.0,
                "average_operation_time_ms": 0.0,
                "last_operation_time": None
            },
            "database_metrics": {
                "new_db": {
                    "connection_pool_size": 10,
                    "active_connections": 0,
                    "idle_connections": 10
                },
                "legacy_db": {
                    "connection_pool_size": 10,
                    "active_connections": 0,
                    "idle_connections": 10
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting dual-write metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-operation")
async def test_dual_write_operation() -> Dict[str, Any]:
    """
    Test dual-write functionality with a simple operation.
    
    This endpoint performs a test operation to verify that
    dual-write is working correctly between databases.
    
    Returns:
        Test operation results
    """
    try:
        dual_write_manager = get_dual_write_manager()
        
        if not dual_write_manager:
            raise HTTPException(
                status_code=400,
                detail="Dual-write not enabled"
            )
        
        # Perform a simple test operation
        test_user_id = "test_user_dual_write"
        
        # Test cart creation
        result = await dual_write_manager.create_cart(test_user_id)
        
        return {
            "test_operation": "create_cart",
            "test_user_id": test_user_id,
            "success": result.success,
            "new_db_success": result.new_db_success,
            "legacy_db_success": result.legacy_db_success,
            "sync_validated": result.sync_validated,
            "errors": {
                "new_db_error": str(result.new_db_error) if result.new_db_error else None,
                "legacy_db_error": str(result.legacy_db_error) if result.legacy_db_error else None
            }
        }
    except Exception as e:
        logger.error(f"Error testing dual-write operation: {e}")
        raise HTTPException(status_code=500, detail=str(e))