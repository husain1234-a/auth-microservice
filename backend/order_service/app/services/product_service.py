import httpx
import logging
from fastapi import HTTPException, status
from app.core.config import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ProductService:
    """Service for communicating with the Product microservice"""
    
    @staticmethod
    async def get_product(product_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve product details from the Product service"""
        async with httpx.AsyncClient(timeout=5.0) as client:  # 5 second timeout
            try:
                response = await client.get(
                    f"{settings.product_service_url}/api/products/{product_id}",
                    headers={"X-Auth-Source": "gateway"}
                )
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"Product not found: {product_id}")
                    return None
                else:
                    logger.error(f"Failed to retrieve product {product_id}: {response.status_code}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Product service unavailable"
                    )
            except httpx.RequestError as e:
                logger.error(f"Network error when calling product service: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Product service unavailable"
                )
            except Exception as e:
                logger.error(f"Unexpected error when calling product service: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )
    
    @staticmethod
    async def check_product_availability(product_id: int, quantity: int) -> bool:
        """Check if a product has sufficient stock"""
        product = await ProductService.get_product(product_id)
        if not product:
            return False
        
        stock_quantity = product.get("stock_quantity", 0)
        return stock_quantity >= quantity
    
    @staticmethod
    async def get_product_price(product_id: int) -> Optional[float]:
        """Get the current price of a product"""
        product = await ProductService.get_product(product_id)
        if not product:
            return None
        
        return product.get("price")