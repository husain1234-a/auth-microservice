import httpx
import logging
from fastapi import HTTPException, status
from app.core.config import settings
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PaymentService:
    """Service for communicating with the Payment microservice"""
    
    @staticmethod
    async def process_payment(user_id: str, order_id: int, amount: float) -> Dict[str, Any]:
        """Process payment for an order"""
        async with httpx.AsyncClient(timeout=5.0) as client:  # 5 second timeout
            try:
                payment_data = {
                    "user_id": user_id,
                    "order_id": order_id,
                    "amount": float(amount)
                }
                response = await client.post(
                    f"{settings.payment_service_url}/payments/process",
                    json=payment_data,
                    headers={"X-Auth-Source": "gateway"}
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to process payment for order {order_id}: {response.status_code}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Payment service unavailable"
                    )
            except httpx.RequestError as e:
                logger.error(f"Network error when calling payment service: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Payment service unavailable"
                )
            except Exception as e:
                logger.error(f"Unexpected error when calling payment service: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )
    
    @staticmethod
    async def initiate_refund(user_id: str, order_id: int, amount: float) -> Dict[str, Any]:
        """Initiate refund for a cancelled order"""
        async with httpx.AsyncClient(timeout=5.0) as client:  # 5 second timeout
            try:
                refund_data = {
                    "user_id": user_id,
                    "order_id": order_id,
                    "amount": float(amount)
                }
                response = await client.post(
                    f"{settings.payment_service_url}/payments/refund",
                    json=refund_data,
                    headers={"X-Auth-Source": "gateway"}
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to initiate refund for order {order_id}: {response.status_code}")
                    return {"success": False, "error": "Refund initiation failed"}
            except httpx.RequestError as e:
                logger.error(f"Network error when calling payment service: {str(e)}")
                return {"success": False, "error": "Payment service unavailable"}
            except Exception as e:
                logger.error(f"Unexpected error when calling payment service: {str(e)}")
                return {"success": False, "error": "Internal server error"}
                