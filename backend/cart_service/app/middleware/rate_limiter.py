"""
Rate Limiter Middleware

This module provides rate limiting for internal endpoints.
"""

import time
import logging
from typing import Dict
from fastapi import Request, HTTPException, status

logger = logging.getLogger(__name__)

# Simple in-memory store for rate limiting
# In production, use Redis for distributed rate limiting
_rate_limits: Dict[str, list] = {}

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def check_rate_limit(self, client_ip: str, endpoint: str):
        """Check if request should be rate limited."""
        key = f"{client_ip}:{endpoint}"
        now = time.time()
        
        # Clean up old requests
        if key in _rate_limits:
            _rate_limits[key] = [
                req_time for req_time in _rate_limits[key]
                if now - req_time < self.window_seconds
            ]
        else:
            _rate_limits[key] = []
        
        # Check if over limit
        if len(_rate_limits[key]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Add current request
        _rate_limits[key].append(now)