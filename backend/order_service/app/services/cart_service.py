import httpx
import logging
from fastapi import HTTPException, status
from app.core.config import settings
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class CartService:
    """Service for communicating with the Cart microservice"""
    
    @staticmethod
    async def get_cart_items(user_id: str) -> List[Dict[str, Any]]:
        """Retrieve cart items for a user from the Cart service"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.cart_service_url}/api/v1/cart/{user_id}",
                    headers={"X-Auth-Source": "gateway"}
                )
                if response.status_code == 200:
                    cart_data = response.json()
                    return cart_data.get("items", [])
                elif response.status_code == 404:
                    # Empty cart is not an error
                    return []
                else:
                    logger.error(f"Failed to retrieve cart for user {user_id}: {response.status_code}")
                    raise HTTPException(
                        status_code=status.HTTP_503_UNAVAILABLE,
                        detail="Cart service unavailable"
                    )
            except httpx.RequestError as e:
                logger.error(f"Network error when calling cart service: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Cart service unavailable"
                )
            except Exception as e:
                logger.error(f"Unexpected error when calling cart service: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )
    
    @staticmethod
    async def clear_cart(user_id: str) -> bool:
        """Clear cart after successful order creation"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{settings.cart_service_url}/api/v1/cart/{user_id}/clear",
                    headers={"X-Auth-Source": "gateway"}
                )
                if response.status_code == 200:
                    return True
                else:
                    logger.error(f"Failed to clear cart for user {user_id}: {response.status_code}")
                    return False
            except httpx.RequestError as e:
                logger.error(f"Network error when calling cart service: {str(e)}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error when calling cart service: {str(e)}")
                return False