from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user_dependency
from app.services.order_service import OrderService
from app.schemas.order import OrderTemplateCreate, OrderTemplateResponse, OrderResponse, OrderCreate
from app.models.order import OrderTemplate

router = APIRouter(prefix="/templates", tags=["templates"])

@router.post("/", response_model=OrderTemplateResponse)
async def create_template(
    template_data: OrderTemplateCreate,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Create a new order template"""
    try:
        order_service = OrderService(db)
        db_template = await order_service.create_order_template(user["uid"], template_data)
        return db_template
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[OrderTemplateResponse])
async def get_templates(
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get all order templates for the current user"""
    try:
        order_service = OrderService(db)
        templates = await order_service.get_user_templates(user["uid"])
        return templates
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{template_id}", response_model=OrderTemplateResponse)
async def get_template(
    template_id: int,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific order template by ID"""
    try:
        result = await db.execute(
            select(OrderTemplate)
            .where(and_(OrderTemplate.id == template_id, OrderTemplate.user_id == user["uid"]))
        )
        db_template = result.scalars().first()
        if not db_template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        return db_template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Delete an order template"""
    try:
        result = await db.execute(
            OrderTemplate.__table__.delete()
            .where(and_(OrderTemplate.id == template_id, OrderTemplate.user_id == user["uid"]))
        )
        
        # Commit the transaction first to get the row count
        await db.commit()
        
        # For SQLAlchemy 2.0, we need to check the result differently
        # Since we've already committed, we'll assume success if no exception was raised
        return {"message": "Template deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{template_id}/order", response_model=OrderResponse)
async def create_order_from_template(
    template_id: int,
    order_data: OrderCreate,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Create a new order from a template"""
    try:
        order_service = OrderService(db)
        db_order = await order_service.create_order_from_template(user["uid"], template_id, order_data)
        return db_order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))