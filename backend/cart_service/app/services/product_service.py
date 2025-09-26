"""
Product Service Client Module

This module provides a client for communicating with the Product microservice.
It handles HTTP requests to fetch product information needed for cart operations.
"""

import aiohttp
from fastapi import HTTPException
from app.core.config import settings
from app.schemas.product import ProductResponse

class ProductService:
    """Service class for communicating with the Product microservice.
    
    This service provides methods for fetching product information from
    the Product microservice via HTTP requests. It handles error cases
    and translates them to appropriate HTTP exceptions.
    """
    
    @staticmethod
    async def get_product(product_id: int) -> ProductResponse:
        """Fetch a product by its ID from the Product service.
        
        This method makes an HTTP GET request to the Product service to
        retrieve information about a specific product. It handles various
        error cases and translates them to appropriate HTTP exceptions.
        
        Args:
            product_id: The ID of the product to fetch
            
        Returns:
            ProductResponse: The product information
            
        Raises:
            HTTPException: If the product is not found (404) or if there
                          is a service communication error (503)
        """
        async with aiohttp.ClientSession() as session:
            try:
                # Make HTTP request to Product service
                async with session.get(f"{settings.product_service_url}/api/products/{product_id}") as response:
                    if response.status == 200:
                        # Parse successful response
                        data = await response.json()
                        return ProductResponse(**data)
                    elif response.status == 404:
                        # Product not found
                        raise HTTPException(status_code=404, detail="Product not found")
                    else:
                        # Other error from Product service
                        raise HTTPException(status_code=response.status, detail="Product service error")
            except aiohttp.ClientError:
                # Network error or service unavailable
                raise HTTPException(status_code=503, detail="Product service unavailable")