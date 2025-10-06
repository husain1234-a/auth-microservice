from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user_dependency
from app.services.order_service import OrderService
from app.schemas.order import OrderFeedbackCreate, OrderFeedbackResponse

router = APIRouter(prefix="/orders", tags=["feedback"])

@router.post("/{order_id}/feedback", response_model=OrderFeedbackResponse)
async def submit_order_feedback(
    order_id: int,
    feedback_data: OrderFeedbackCreate,
    user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback for an order"""
    try:
        order_service = OrderService(db)
        db_feedback = await order_service.submit_order_feedback(order_id, user["uid"], feedback_data)
        return db_feedback
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))