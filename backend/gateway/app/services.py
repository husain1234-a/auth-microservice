import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time
from .config import SERVICES, CIRCUIT_BREAKER_CONFIG, RATE_LIMIT_CONFIG, SECURITY_CONFIG
from .models import CircuitBreakerState, RateLimitState
from collections import defaultdict
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

# Create HTTP clients for each service
http_clients: Dict[str, httpx.AsyncClient] = {}

# Circuit breaker state tracking
circuit_breaker_state: Dict[str, CircuitBreakerState] = defaultdict(lambda: CircuitBreakerState())

# Rate limiting tracking
rate_limit_storage: Dict[str, RateLimitState] = defaultdict(lambda: RateLimitState())

def is_rate_limited(client_ip: str, service_name: str) -> bool:
    """Check if a client is rate limited for a specific service"""
    # Check if rate limiting is enabled
    if not SECURITY_CONFIG.get("rate_limit_enabled", True):
        return False
        
    key = f"{client_ip}:{service_name}"
    now = time.time()
    
    # Clean up old requests outside the window
    rate_limit_storage[key].requests = [
        req_time for req_time in rate_limit_storage[key].requests
        if now - req_time < RATE_LIMIT_CONFIG["window_seconds"]
    ]
    
    # Check if currently blocked
    blocked_until = rate_limit_storage[key].blocked_until
    if blocked_until is not None:
        if now < blocked_until.timestamp():
            return True
        else:
            # Unblock if time has passed
            rate_limit_storage[key].blocked_until = None
    
    # Check if over rate limit
    if len(rate_limit_storage[key].requests) >= RATE_LIMIT_CONFIG["max_requests"]:
        # Block for the remainder of the window
        rate_limit_storage[key].blocked_until = datetime.utcnow() + timedelta(seconds=RATE_LIMIT_CONFIG["window_seconds"])
        return True
    
    # Add current request
    rate_limit_storage[key].requests.append(now)
    return False

def check_circuit_breaker(service_name: str) -> bool:
    """Check if circuit breaker is open for a service"""
    # Check if circuit breaker is enabled
    if not SECURITY_CONFIG.get("circuit_breaker_enabled", True):
        return True
        
    state = circuit_breaker_state[service_name]
    now = time.time()
    
    # If circuit is open, check if recovery time has passed
    if state.state == "OPEN":
        if state.last_failure_time is not None and now - state.last_failure_time.timestamp() >= CIRCUIT_BREAKER_CONFIG["recovery_timeout"]:
            # Move to half-open state to test service
            state.state = "HALF_OPEN"
            logger.info(f"Circuit breaker for {service_name} moved to HALF_OPEN state")
        elif state.last_failure_time is not None:
            return False  # Circuit still open
    
    return True  # Circuit closed or half-open

def record_success(service_name: str) -> None:
    """Record successful request for circuit breaker"""
    state = circuit_breaker_state[service_name]
    state.failure_count = 0
    state.last_failure_time = None
    if state.state != "CLOSED":
        state.state = "CLOSED"
        logger.info(f"Circuit breaker for {service_name} closed")

def record_failure(service_name: str) -> None:
    """Record failed request for circuit breaker"""
    state = circuit_breaker_state[service_name]
    state.failure_count += 1
    state.last_failure_time = datetime.utcnow()
    
    if state.failure_count >= CIRCUIT_BREAKER_CONFIG["failure_threshold"]:
        state.state = "OPEN"
        logger.warning(f"Circuit breaker for {service_name} opened due to {state.failure_count} failures")

async def initialize_clients():
    """Initialize HTTP clients for all services"""
    for service_name, service_config in SERVICES.items():
        http_clients[service_name] = httpx.AsyncClient(
            base_url=service_config["url"],
            timeout=5.0,  # Reduced from 30s to 5s
            # Increased connection pooling for high load
            limits=httpx.Limits(
                max_keepalive_connections=50,  # Increased from 5
                max_connections=200,           # Increased from 20
                keepalive_expiry=30.0
            )
        )
        logger.info(f"Initialized client for {service_name} service at {service_config['url']}")

async def close_clients():
    """Close all HTTP clients"""
    for client in http_clients.values():
        await client.aclose()
    logger.info("Closed all service clients")

async def health_check_service(service_name: str) -> str:
    """Check health of a specific service"""
    try:
        client = http_clients[service_name]
        service_config = SERVICES[service_name]
        response = await client.get(service_config["health_path"])
        return "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        logger.error(f"Health check failed for {service_name}: {str(e)}")
        return "unreachable"