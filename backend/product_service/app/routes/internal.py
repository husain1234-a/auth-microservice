"""
Internal Routes for Product Service

This module provides internal endpoints for service-to-service communication.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.product_service import ProductService

router = APIRouter(prefix="/internal")
logger = logging.getLogger(__name__)

class EventRequest(BaseModel):
    event_type: str
    payload: Dict[Any, Any]
    timestamp: float

@router.post("/events")
async def handle_event(event: EventRequest, db: AsyncSession = Depends(get_db)):
    """Handle incoming events from other services.
    
    This endpoint processes events to maintain data consistency.
    """
    try:
        logger.info(f"Received event: {event.event_type}")
        
        if event.event_type == "category.updated":
            # Update all products that reference this category
            category_id = event.payload.get("category_id")
            category_name = event.payload.get("name")
            
            if category_id and category_name:
                # Update all products with this category_id
                logger.info(f"Updating products for category {category_id} to name '{category_name}'")
                updated_count = await ProductService.update_products_category_name(db, category_id, category_name)
                logger.info(f"Updated {updated_count} products for category {category_id}")
                
        return {"message": "Event processed successfully"}
        
    except Exception as e:
        logger.error(f"Error processing event {event.event_type}: {e}")
        raise HTTPException(status_code=500, detail="Error processing event")

@router.get("/health")
async def health_check():
    """Health check endpoint for internal service monitoring."""
    return {
        "status": "healthy",
        "service": "product-service",
        "timestamp": asyncio.get_event_loop().time()
    }