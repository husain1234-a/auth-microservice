import httpx
import logging
from fastapi import HTTPException, status
from app.core.config import settings
from typing import Dict, Any

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for communicating with the Notification microservice"""
    
    @staticmethod
    async def send_order_notification(user_id: str, order_id: int, status: str) -> bool:
        """Send order status notification to user"""
        async with httpx.AsyncClient(timeout=5.0) as client:  # 5 second timeout
            try:
                notification_data = {
                    "user_id": user_id,
                    "order_id": order_id,
                    "status": status
                }
                response = await client.post(
                    f"{settings.notification_service_url}/notifications/order-status",
                    json=notification_data,
                    headers={"X-Auth-Source": "gateway"}
                )
                if response.status_code == 200:
                    logger.info(f"Order notification sent for order {order_id}")
                    return True
                else:
                    logger.error(f"Failed to send notification for order {order_id}: {response.status_code}")
                    return False
            except httpx.RequestError as e:
                logger.error(f"Network error when calling notification service: {str(e)}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error when calling notification service: {str(e)}")
                return False
    
    @staticmethod
    async def send_order_confirmation_email(user_id: str, order_id: int, total_amount: float) -> bool:
        """Send order confirmation email to user"""
        async with httpx.AsyncClient() as client:
            try:
                email_data = {
                    "user_id": user_id,
                    "order_id": order_id,
                    "total_amount": float(total_amount)
                }
                response = await client.post(
                    f"{settings.notification_service_url}/notifications/order-confirmation",
                    json=email_data,
                    headers={"X-Auth-Source": "gateway"}
                )
                if response.status_code == 200:
                    logger.info(f"Order confirmation email sent for order {order_id}")
                    return True
                else:
                    logger.error(f"Failed to send confirmation email for order {order_id}: {response.status_code}")
                    return False
            except httpx.RequestError as e:
                logger.error(f"Network error when calling notification service: {str(e)}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error when calling notification service: {str(e)}")
                return False