import os
from typing import Dict, Any

# Service configuration
SERVICES: Dict[str, Dict[str, Any]] = {
    "auth": {
        "url": os.getenv("AUTH_SERVICE_URL", "http://localhost:8001"),
        "prefix": "/auth",
        "health_path": "/health"
    },
    "product": {
        "url": os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002"),
        "prefix": "/api",
        "health_path": "/health"
    },
    "cart": {
        "url": os.getenv("CART_SERVICE_URL", "http://localhost:8003"),
        "prefix": "/api/v1",
        "health_path": "/health"
    },
    "order": {
        "url": os.getenv("ORDER_SERVICE_URL", "http://localhost:8004"),
        "prefix": "/api/v1",
        "health_path": "/health"
    }
}

# Circuit breaker configuration
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 20,  # Increased from 5 to handle load spikes
    "recovery_timeout": 10,   # Reduced from 30s to 10s for faster recovery
    "expected_exception": (TimeoutError, ConnectionError)
}

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "max_requests": 100,
    "window_seconds": 60
}

# Security configuration
SECURITY_CONFIG = {
    "jwt_cache_duration": 3600,  # 1 hour
    "allowed_origins": ["*"],  # In production, specify exact origins
    "rate_limit_enabled": True,
    "circuit_breaker_enabled": True
}