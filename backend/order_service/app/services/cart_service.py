import httpx
import logging
from fastapi import HTTPException, status
from app.core.config import settings
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CartService:
    """Service for communicating with the Cart microservice"""
    
    @staticmethod
    async def get_cart_items(user_id: str, auth_headers: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Retrieve cart items for a user from the Cart service"""
        async with httpx.AsyncClient() as client:
            try:
                # Prepare headers
                headers = {
                    "X-Auth-Source": "gateway",
                    "X-Gateway-Forwarded": "true"
                }
                
                # Prepare cookies
                cookies = {}
                
                # Add authentication headers if provided
                if auth_headers:
                    # Add Authorization header if present
                    if "Authorization" in auth_headers:
                        headers["Authorization"] = auth_headers["Authorization"]
                    
                    # Extract session cookie if present
                    if "Cookie" in auth_headers:
                        cookie_header = auth_headers["Cookie"]
                        # Parse the cookie header to extract auth_session
                        if "auth_session=" in cookie_header:
                            # Extract the session token value
                            session_token = cookie_header.split("auth_session=")[1].split(";")[0]
                            cookies["auth_session"] = session_token
                
                response = await client.get(
                    f"{settings.gateway_url}/api/v1/cart",
                    headers=headers,
                    cookies=cookies if cookies else None
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
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
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
    async def clear_cart(user_id: str, auth_headers: Optional[Dict[str, str]] = None) -> bool:
        """Clear cart after successful order creation"""
        async with httpx.AsyncClient() as client:
            try:
                # Prepare headers
                headers = {
                    "X-Auth-Source": "gateway",
                    "X-Gateway-Forwarded": "true"
                }
                
                # Prepare cookies
                cookies = {}
                
                # Add authentication headers if provided
                if auth_headers:
                    # Add Authorization header if present
                    if "Authorization" in auth_headers:
                        headers["Authorization"] = auth_headers["Authorization"]
                    
                    # Extract session cookie if present
                    if "Cookie" in auth_headers:
                        cookie_header = auth_headers["Cookie"]
                        # Parse the cookie header to extract auth_session
                        if "auth_session=" in cookie_header:
                            # Extract the session token value
                            session_token = cookie_header.split("auth_session=")[1].split(";")[0]
                            cookies["auth_session"] = session_token
                
                response = await client.delete(
                    f"{settings.gateway_url}/api/v1/cart",
                    headers=headers,
                    cookies=cookies if cookies else None
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