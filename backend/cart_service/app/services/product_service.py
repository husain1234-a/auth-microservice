"""
Product Service Client Module

This module provides a client for communicating with the Product microservice.
It handles HTTP requests to fetch product information needed for cart operations.
"""

import aiohttp
import logging
from typing import Optional
from cachetools import TTLCache
from app.core.config import settings
from app.schemas.product import ProductResponse
from app.utils.circuit_breaker import circuit_breakers

logger = logging.getLogger(__name__)

# Create a TTL cache that expires items after 5 minutes
_product_cache = TTLCache(maxsize=1000, ttl=300)

async def get_product(product_id: int) -> Optional[ProductResponse]:
    """Fetch a product by its ID from the Product service with caching and circuit breaker."""
    # Check cache first
    cache_key = f"product_{product_id}"
    if cache_key in _product_cache:
        logger.info(f"Cache hit for product {product_id}")
        return _product_cache[cache_key]
    
    # Use circuit breaker for service call
    circuit_breaker = circuit_breakers["product_service"]
    
    async def _fetch_product():
        async with aiohttp.ClientSession() as session:
            try:
                logger.info(f"Fetching product {product_id} from product service")
                async with session.get(f"{settings.product_service_url}/api/products/{product_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        product = ProductResponse(**data)
                        # Cache the result
                        _product_cache[cache_key] = product
                        return product
                    elif response.status == 404:
                        logger.warning(f"Product {product_id} not found")
                        return None
                    else:
                        logger.error(f"Product service error: {response.status}")
                        raise Exception(f"Product service returned status {response.status}")
            except aiohttp.ClientError as e:
                logger.error(f"Failed to connect to product service: {e}")
                raise e
    
    try:
        return await circuit_breaker.call_async(_fetch_product)
    except Exception as e:
        logger.error(f"Circuit breaker prevented call to product service: {e}")
        return None

def invalidate_product_cache(product_id: int):
    """Invalidate a specific product in the cache."""
    cache_key = f"product_{product_id}"
    _product_cache.pop(cache_key, None)
    logger.info(f"Invalidated cache for product {product_id}")

# Call this function when products are updated
def notify_product_update(product_id: int):
    """Notify that a product has been updated and invalidate cache."""
    invalidate_product_cache(product_id)