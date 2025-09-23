from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import httpx
import logging
from typing import Dict, Any, Optional
import time
from datetime import datetime
from .config import SERVICES
from .services import (
    http_clients, 
    is_rate_limited, 
    check_circuit_breaker, 
    record_success, 
    record_failure,
    health_check_service
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Enhanced health check endpoint that verifies all services are reachable"""
    service_status = {}
    
    for service_name in http_clients.keys():
        service_status[service_name] = await health_check_service(service_name)
    
    overall_status = "healthy" if all(status == "healthy" for status in service_status.values()) else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "services": service_status
    }

@router.get("/gateway/stats")
async def gateway_stats():
    """Gateway statistics endpoint"""
    # This would need to import the actual state from services module
    # For now, returning a basic structure
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Gateway statistics endpoint - implementation pending"
    }

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_request(request: Request, path: str):
    """
    Enhanced main proxy route that forwards requests to appropriate services
    based on the path prefix with circuit breaker and rate limiting
    """
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    # Special handling for root path health check
    if path == "" or path == "/":
        return await health_check()
    
    # Match the path to a service
    target_service: Optional[str] = None
    service_config: Optional[Dict[str, Any]] = None
    
    # Match path to service
    for service_name, config in SERVICES.items():
        prefix = config["prefix"].lstrip("/")
        if path == prefix or path.startswith(prefix + "/") or path.startswith(prefix + "?"):
            target_service = service_name
            service_config = config
            break
    
    # If no service matches, return 404
    if not target_service or not service_config:
        logger.warning(f"No service found for path: {path}")
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Check rate limiting
    if is_rate_limited(client_ip, target_service):
        logger.warning(f"Rate limit exceeded for {client_ip} on {target_service}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Check circuit breaker
    if not check_circuit_breaker(target_service):
        logger.warning(f"Circuit breaker open for {target_service}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    
    # Prepare the path for the target service
    service_prefix = service_config["prefix"].lstrip("/")
    if path.startswith(service_prefix):
        target_path = path[len(service_prefix):]
        if not target_path.startswith("/") and target_path:
            target_path = "/" + target_path
        elif not target_path:
            target_path = "/"
    else:
        target_path = "/" + path if not path.startswith("/") else path
    
    # Get the HTTP client for the target service
    client = http_clients[target_service]
    
    # Prepare headers (excluding hop-by-hop headers)
    headers = dict(request.headers)
    headers.pop("host", None)
    
    # Add gateway tracking headers
    headers["X-Gateway-Forwarded"] = "true"
    headers["X-Gateway-Timestamp"] = str(datetime.utcnow().isoformat())
    headers["X-Forwarded-For"] = client_ip
    
    try:
        # Forward the request to the target service
        logger.info(f"Forwarding {request.method} request to {target_service} service: {target_path}")
        
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            request_body = await request.body()
        
        if request.method == "GET":
            response = await client.get(target_path, headers=headers)
        elif request.method == "POST":
            response = await client.post(target_path, headers=headers, content=request_body)
        elif request.method == "PUT":
            response = await client.put(target_path, headers=headers, content=request_body)
        elif request.method == "DELETE":
            response = await client.delete(target_path, headers=headers)
        elif request.method == "PATCH":
            response = await client.patch(target_path, headers=headers, content=request_body)
        elif request.method == "OPTIONS":
            response = await client.options(target_path, headers=headers)
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")
        
        # Record success for circuit breaker
        record_success(target_service)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log successful request
        logger.info(f"Successfully forwarded {request.method} {path} to {target_service} in {response_time:.3f}s")
        
        # Return the response from the target service
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except httpx.TimeoutException:
        # Record failure for circuit breaker
        record_failure(target_service)
        
        logger.error(f"Timeout when calling {target_service} service")
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except httpx.RequestError as e:
        # Record failure for circuit breaker
        record_failure(target_service)
        
        logger.error(f"Network error when calling {target_service} service: {str(e)}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        # Record failure for circuit breaker
        record_failure(target_service)
        
        logger.error(f"Unexpected error when calling {target_service} service: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")