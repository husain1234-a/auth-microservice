"""
Event Publisher Service

This service publishes events when data changes to keep services synchronized.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class EventPublisher:
    """Service for publishing events to other services."""
    
    @staticmethod
    async def publish_event(event_type: str, payload: Dict[Any, Any]):
        """Publish an event to all interested services.
        
        Args:
            event_type: Type of event (e.g., "category.updated")
            payload: Event data
        """
        # In production, you would use a message queue like Redis Pub/Sub or Kafka
        # For this implementation, we'll use direct HTTP calls with proper error handling
        
        services = [
            {"name": "cart_service", "url": settings.cart_service_url}
        ]
        
        tasks = []
        for service in services:
            task = EventPublisher._notify_service(service, event_type, payload)
            tasks.append(task)
        
        # Execute all notifications concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log results
        for i, result in enumerate(results):
            service_name = services[i]["name"]
            if isinstance(result, Exception):
                logger.error(f"Failed to notify {service_name}: {result}")
            else:
                logger.info(f"Successfully notified {service_name}")
    
    @staticmethod
    async def _notify_service(service: Dict[str, str], event_type: str, payload: Dict[Any, Any]):
        """Notify a specific service about an event."""
        try:
            async with aiohttp.ClientSession() as session:
                event_data = {
                    "event_type": event_type,
                    "payload": payload,
                    "timestamp": asyncio.get_event_loop().time()
                }
                async with session.post(
                    f"{service['url']}/internal/events",
                    json=event_data
                ) as response:
                    if response.status not in [200, 202]:
                        raise Exception(f"Service {service['name']} returned status {response.status}")
        except Exception as e:
            logger.error(f"Error notifying {service['name']}: {e}")
            raise e