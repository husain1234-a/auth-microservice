from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.security import (
    get_current_user_dependency, 
    get_current_admin_user_dependency,
    get_current_delivery_partner_dependency,
    get_current_user_id_dependency
)
from app.services.order_service import OrderService
from app.schemas.order import (
    OrderCreate, OrderResponse, OrderStatusUpdate, 
    AssignDeliveryPartnerRequest, OrderCancelResponse,
    OrderItemsUpdate, OrderAnalyticsResponse,
    CancellationRateResponse, TopCustomerResponse,
    BulkStatusUpdate, BulkAssignDelivery
)
from app.models.order import OrderStatus

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Create a new order from the user's cart"""
    try:
        order_service = OrderService(db)
        db_order = await order_service.create_order_from_cart(user["uid"], order_data)
        return db_order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/my-orders", response_model=List[OrderResponse])
async def get_my_orders(
    limit: int = 20,
    offset: int = 0,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve the current user's order history"""
    try:
        order_service = OrderService(db)
        orders = await order_service.get_user_orders(user["uid"], limit, offset)
        return orders
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a specific order by its ID"""
    try:
        order_service = OrderService(db)
        db_order = await order_service.get_order_by_id(order_id, user["uid"])
        if not db_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return db_order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    user: dict = Depends(get_current_admin_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Update the status of an order (Admin/Delivery Partner)"""
    try:
        order_service = OrderService(db)
        db_order = await order_service.update_order_status(order_id, status_update)
        if not db_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return db_order
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[OrderResponse])
async def get_all_orders(
    user_id: str = None,
    status: str = None,
    limit: int = 20,
    offset: int = 0,
    user: dict = Depends(get_current_admin_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all orders with optional filtering (Admin Only)"""
    try:
        order_service = OrderService(db)
        orders = await order_service.get_admin_orders(user_id, status, limit, offset)
        return orders
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{order_id}/assign-delivery", response_model=OrderResponse)
async def assign_delivery_partner(
    order_id: int,
    assign_data: AssignDeliveryPartnerRequest,
    user: dict = Depends(get_current_admin_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Assign a delivery partner to an order (Admin Only)"""
    try:
        order_service = OrderService(db)
        db_order = await order_service.assign_delivery_partner(order_id, assign_data)
        if not db_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return db_order
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{order_id}/cancel", response_model=OrderCancelResponse)
async def cancel_order(
    order_id: int,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Cancel an order if eligible"""
    try:
        order_service = OrderService(db)
        result = await order_service.cancel_order(order_id, user["uid"])
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{order_id}/items", response_model=OrderResponse)
async def update_order_items(
    order_id: int,
    items_update: OrderItemsUpdate,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Update items in an order if eligible"""
    try:
        order_service = OrderService(db)
        db_order = await order_service.update_order_items(order_id, user["uid"], items_update)
        if not db_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return db_order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/bulk-status-update")
async def bulk_update_order_status(
    bulk_update: BulkStatusUpdate,
    user: dict = Depends(get_current_admin_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Bulk update order statuses (Admin Only)"""
    try:
        order_service = OrderService(db)
        result = await order_service.bulk_update_order_status(bulk_update)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/bulk-assign-delivery")
async def bulk_assign_delivery_partner(
    bulk_assign: BulkAssignDelivery,
    user: dict = Depends(get_current_admin_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Bulk assign delivery partner to orders (Admin Only)"""
    try:
        order_service = OrderService(db)
        result = await order_service.bulk_assign_delivery_partner(bulk_assign)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/export")
async def export_orders(
    format: str = "json",
    status: str = None,
    user: dict = Depends(get_current_admin_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Export orders in specified format (Admin Only)"""
    try:
        order_service = OrderService(db)
        orders = await order_service.get_admin_orders(status=status)
        
        if format.lower() == "csv":
            # Convert to CSV format
            import csv
            import io
            from fastapi.responses import Response
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "ID", "User ID", "Total Amount", "Delivery Fee", "Status",
                "Delivery Address", "Created At", "Delivered At"
            ])
            
            # Write data
            for order in orders:
                writer.writerow([
                    order.id, order.user_id, order.total_amount, order.delivery_fee,
                    order.status, order.delivery_address, order.created_at, order.delivered_at
                ])
            
            csv_data = output.getvalue()
            output.close()
            
            return Response(
                content=csv_data,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=orders.csv"}
            )
        else:
            # Return JSON by default
            return orders
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/scheduled", response_model=OrderResponse)
async def create_scheduled_order(
    order_data: OrderCreate,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Create a scheduled order for future delivery"""
    try:
        if not order_data.scheduled_for:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="scheduled_for field is required for scheduled orders"
            )
        
        order_service = OrderService(db)
        db_order = await order_service.create_order_from_cart(user["uid"], order_data)
        return db_order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{order_id}/request-return", response_model=OrderResponse)
async def request_order_return(
    order_id: int,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Request return for a delivered order"""
    try:
        order_service = OrderService(db)
        db_order = await order_service.get_order_by_id(order_id, user["uid"])
        if not db_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
        # Check if order is delivered
        if db_order.status != OrderStatus.DELIVERED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Return can only be requested for delivered orders"
            )
        
        # Update order status to return requested
        db_order.status = OrderStatus.RETURN_REQUESTED
        await db.commit()
        await db.refresh(db_order)
        
        return db_order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/tracking-stream/{order_id}")
async def get_order_tracking_stream(
    order_id: int,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get real-time tracking stream for an order"""
    try:
        # This would typically use Server-Sent Events or WebSockets
        # For now, returning a placeholder response
        return {"message": "Tracking stream not implemented yet", "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/delivery-location/{order_id}")
async def get_delivery_location(
    order_id: int,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get current delivery location for an order"""
    try:
        # This would typically integrate with a GPS tracking system
        # For now, returning a placeholder response
        return {
            "order_id": order_id,
            "latitude": "40.7128",
            "longitude": "-74.0060",
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))