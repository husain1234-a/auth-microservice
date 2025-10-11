from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_admin_user_dependency
from app.services.order_service import OrderService
from app.schemas.order import OrderAnalyticsResponse, CancellationRateResponse, TopCustomerResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/revenue", response_model=List[OrderAnalyticsResponse])
async def get_revenue_analytics(
    start_date: str,
    end_date: str,
    user: dict = Depends(get_current_admin_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get revenue analytics for a date range"""
    try:
        # Parse date strings to datetime objects
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD")
        
        if start_dt >= end_dt:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date must be before end date")
        
        order_service = OrderService(db)
        analytics = await order_service.get_revenue_analytics(start_dt, end_dt)
        print(f"Revenue analytics result: {analytics}")
        return analytics
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/delivery-performance")
async def get_delivery_performance(
    user: dict = Depends(get_current_admin_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get delivery performance metrics"""
    try:
        order_service = OrderService(db)
        performance = await order_service.get_delivery_performance()
        return performance
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/top-customers", response_model=List[TopCustomerResponse])
async def get_top_customers(
    limit: int = 10,
    user: dict = Depends(get_current_admin_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get top customers by order count and spending"""
    try:
        order_service = OrderService(db)
        top_customers = await order_service.get_top_customers(limit)
        return top_customers
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/cancellation-rate", response_model=CancellationRateResponse)
async def get_cancellation_rate(
    period_days: int = 30,
    user: dict = Depends(get_current_admin_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get order cancellation rate for a period"""
    try:
        order_service = OrderService(db)
        cancellation_rate = await order_service.get_cancellation_rate(period_days)
        return cancellation_rate
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))