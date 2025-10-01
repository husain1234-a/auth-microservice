"""
Circuit Breaker Implementation

This module provides a circuit breaker pattern to prevent cascade failures.
"""

import time
import logging
from enum import Enum
from typing import Dict, Callable, Awaitable, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, 
                 name: str,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 30,
                 expected_exception: tuple = (Exception,)):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED
        
    def call(self, func: Callable, *args, **kwargs):
        """Call a function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self.last_failure_time and time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker {self.name} moved to HALF_OPEN state")
            else:
                raise Exception(f"Circuit breaker {self.name} is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    async def call_async(self, func: Callable[..., Awaitable], *args, **kwargs):
        """Call an async function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self.last_failure_time and time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker {self.name} moved to HALF_OPEN state")
            else:
                raise Exception(f"Circuit breaker {self.name} is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.last_failure_time = None
        if self.state != CircuitState.CLOSED:
            self.state = CircuitState.CLOSED
            logger.info(f"Circuit breaker {self.name} closed")
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker {self.name} opened after {self.failure_count} failures")

# Global circuit breakers for services
circuit_breakers: Dict[str, CircuitBreaker] = {
    "product_service": CircuitBreaker("product_service", failure_threshold=3, recovery_timeout=60),
    "auth_service": CircuitBreaker("auth_service", failure_threshold=3, recovery_timeout=60)
}