from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import time
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

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify gateway is working"""
    return {"message": "Gateway is working", "timestamp": datetime.utcnow().isoformat()}

@router.api_route("/debug/headers", methods=["GET", "POST", "OPTIONS"])
async def debug_headers(request: Request):
    """Debug endpoint to check what headers are being received"""
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "has_auth": "Authorization" in request.headers,
        "has_token_state": hasattr(request.state, 'token'),
        "token_preview": getattr(request.state, 'token', 'None')[:20] + "..." if hasattr(request.state, 'token') else None
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

@router.api_route("/auth/{path:path}", methods=["OPTIONS"])
async def auth_cors_handler(request: Request, path: str):
    """Handle CORS preflight requests for auth service"""
    logger.info(f"Handling CORS preflight for auth service: {path}")
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Requested-With, Accept, X-Gateway-Forwarded",
            "Access-Control-Max-Age": "86400",  # Cache preflight for 24 hours
        }
    )

@router.api_route("/api/{path:path}", methods=["OPTIONS"])
async def api_cors_handler(request: Request, path: str):
    """Handle CORS preflight requests for product/api service"""
    logger.info(f"Handling CORS preflight for API service: {path}")
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Requested-With, Accept, X-Gateway-Forwarded",
            "Access-Control-Max-Age": "86400",  # Cache preflight for 24 hours
        }
    )

@router.api_route("/api/v1/cart/{path:path}", methods=["OPTIONS"])
async def cart_cors_handler(request: Request, path: str):
    """Handle CORS preflight requests for cart service"""
    logger.info(f"Handling CORS preflight for cart service: {path}")
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Requested-With, Accept, X-Gateway-Forwarded",
            "Access-Control-Max-Age": "86400",  # Cache preflight for 24 hours
        }
    )

@router.api_route("/api/v1/wishlist/{path:path}", methods=["OPTIONS"])
async def wishlist_cors_handler(request: Request, path: str):
    """Handle CORS preflight requests for wishlist endpoints"""
    logger.info(f"Handling CORS preflight for wishlist service: {path}")
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Requested-With, Accept, X-Gateway-Forwarded",
            "Access-Control-Max-Age": "86400",  # Cache preflight for 24 hours
        }
    )

@router.api_route("/api/v1/orders/{path:path}", methods=["OPTIONS"])
async def orders_cors_handler(request: Request, path: str):
    """Handle CORS preflight requests for order service"""
    logger.info(f"Handling CORS preflight for order service: {path}")
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Requested-With, Accept, X-Gateway-Forwarded",
            "Access-Control-Max-Age": "86400",  # Cache preflight for 24 hours
        }
    )

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
    
    # Handle CORS preflight requests
    if request.method == "OPTIONS":
        # For OPTIONS requests, return a simple response with CORS headers
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Requested-With, Accept, X-Gateway-Forwarded",
                "Access-Control-Max-Age": "86400",  # Cache preflight for 24 hours
            }
        )
    
    # Match the path to a service
    target_service: Optional[str] = None
    service_config: Optional[Dict[str, Any]] = None
    
    logger.info(f"Routing request for path: '{path}', method: {request.method}, full URL: {request.url}, query params: {request.query_params}")
    logger.info(f"Request headers: Authorization present: {'Authorization' in request.headers}, has token state: {hasattr(request.state, 'token')}")
    
    # Explicit path matching to avoid conflicts (order matters - most specific first)
    if path.startswith("api/v1/cart") or path.startswith("api/v1/wishlist"):
        target_service = "cart"
        service_config = SERVICES["cart"]
        logger.info(f"Matched cart service for path: {path}")
    elif path.startswith("api/v1/orders") or path.startswith("api/v1/templates") or path.startswith("api/v1/analytics"):
        target_service = "order"
        service_config = SERVICES["order"]
        logger.info(f"Matched order service for path: {path}")
    elif path.startswith("api/products") or path.startswith("api/categories"):
        target_service = "product"
        service_config = SERVICES["product"]
        logger.info(f"Matched product service for path: {path}")
    elif path.startswith("auth"):
        target_service = "auth"
        service_config = SERVICES["auth"]
        logger.info(f"Matched auth service for path: {path}")
    else:
        logger.warning(f"No explicit match found for path: {path}, trying generic matching")
        # Fallback to generic matching
        for service_name, config in SERVICES.items():
            prefix = config["prefix"].lstrip("/")
            logger.info(f"Checking service {service_name} with prefix '{prefix}' against path '{path}'")
            if path == prefix or path.startswith(prefix + "/") or path.startswith(prefix + "?"):
                target_service = service_name
                service_config = config
                logger.info(f"Matched service {service_name} for path: {path}")
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
    
    # Fix path forwarding logic to correctly forward to services
    if target_service == "product":
        # For product service, ensure trailing slash for endpoints that need it
        if path == "api/products" or path == "api/categories":
            target_path = "/" + path + "/"
        else:
            target_path = "/" + path
    elif target_service == "cart":
        # For cart service, forward the full path as-is since it expects /api/v1/cart/* or /api/v1/wishlist/*
        target_path = "/" + path
    elif target_service == "order":
        # For order service, forward the full path as-is since it expects /api/v1/orders/* etc.
        target_path = "/" + path
    elif target_service == "auth":
        # For auth service, forward the full path as-is since it expects /auth/*
        target_path = "/" + path
    else:
        # For other cases, use the existing logic
        if path.startswith(service_prefix + "/"):
            # Remove the service prefix to get the target path
            target_path = "/" + path
        elif path == service_prefix:
            # If path exactly matches prefix, target path should include the prefix
            target_path = "/" + service_prefix + "/"
        else:
            # For other cases, use the path as is with leading slash
            target_path = "/" + path
    
    # Get the HTTP client for the target service
    client = http_clients[target_service]
    
    # Prepare headers (excluding hop-by-hop headers)
    headers = dict(request.headers)
    headers.pop("host", None)
    
    # Add gateway tracking headers
    headers["X-Gateway-Forwarded"] = "true"
    headers["X-Gateway-Timestamp"] = str(datetime.utcnow().isoformat())
    headers["X-Forwarded-For"] = client_ip
    headers["X-Auth-Source"] = "gateway"
    
    # Prepare cookies for forwarding
    cookies_to_forward = {}
    
    # Forward authentication token if present
    if hasattr(request.state, 'token'):
        # Forward the token stored by JWT middleware as Authorization header
        headers["Authorization"] = f"Bearer {request.state.token}"
        auth_source = getattr(request.state, 'auth_source', 'unknown')
        logger.info(f"Forwarding {auth_source} token to {target_service} service")
        
        # Also forward as session cookie for services that expect it
        if auth_source == "session":
            # Keep the original session cookie for services that might need it
            session_cookie = request.cookies.get("auth_session")
            if session_cookie:
                cookies_to_forward["auth_session"] = session_cookie
                logger.info(f"Also forwarding session cookie to {target_service} service")
    else:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            # Forward the original Authorization header directly
            headers["Authorization"] = auth_header
            logger.info(f"Forwarding original Authorization header to {target_service} service: {auth_header[:20]}...")
        else:
            logger.warning(f"No authentication found for {target_service} service request")
    
    # Add security headers
    headers["X-Content-Type-Options"] = "nosniff"
    headers["X-Frame-Options"] = "DENY"
    headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    try:
        # Forward the request to the target service
        logger.info(f"Forwarding {request.method} request to {target_service} service: {target_path}")
        
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            request_body = await request.body()
        
        # Prepare query parameters
        query_params = dict(request.query_params) if request.query_params else None
        if query_params:
            logger.info(f"Forwarding query parameters: {query_params}")
        
        if request.method == "GET":
            response = await client.get(target_path, headers=headers, cookies=cookies_to_forward, params=query_params)
        elif request.method == "POST":
            response = await client.post(target_path, headers=headers, content=request_body, cookies=cookies_to_forward, params=query_params)
        elif request.method == "PUT":
            response = await client.put(target_path, headers=headers, content=request_body, cookies=cookies_to_forward, params=query_params)
        elif request.method == "DELETE":
            response = await client.delete(target_path, headers=headers, cookies=cookies_to_forward, params=query_params)
        elif request.method == "PATCH":
            response = await client.patch(target_path, headers=headers, content=request_body, cookies=cookies_to_forward, params=query_params)
        elif request.method == "OPTIONS":
            response = await client.options(target_path, headers=headers, cookies=cookies_to_forward, params=query_params)
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")
        
        # Record success for circuit breaker
        record_success(target_service)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log successful request
        logger.info(f"Successfully forwarded {request.method} {path} to {target_service} in {response_time:.3f}s")
        
        # Add security headers to response
        response_headers = dict(response.headers)
        response_headers["X-Content-Type-Options"] = "nosniff"
        response_headers["X-Frame-Options"] = "DENY"
        response_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Ensure CORS headers are present
        response_headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response_headers["Access-Control-Allow-Credentials"] = "true"
        response_headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response_headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Requested-With, Accept, X-Gateway-Forwarded"
        
        # Return the response from the target service
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.headers.get("content-type", "application/json")
        )
        
    except httpx.TimeoutException:
        # Record failure for circuit breaker
        record_failure(target_service)
        
        logger.error(f"Timeout when calling {target_service} service")
        # Create error response with CORS headers
        error_response = JSONResponse(
            status_code=504,
            content={"detail": "Gateway timeout"},
            headers={
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Requested-With, Accept, X-Gateway-Forwarded",
            }
        )
        return error_response
    except httpx.RequestError as e:
        # Record failure for circuit breaker
        record_failure(target_service)
        
        logger.error(f"Network error when calling {target_service} service: {str(e)}")
        # Create error response with CORS headers
        error_response = JSONResponse(
            status_code=503,
            content={"detail": "Service temporarily unavailable"},
            headers={
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Requested-With, Accept, X-Gateway-Forwarded",
            }
        )
        return error_response
    except Exception as e:
        # Record failure for circuit breaker
        record_failure(target_service)
        
        logger.error(f"Unexpected error when calling {target_service} service: {str(e)}")
        # Create error response with CORS headers
        error_response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
            headers={
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "Authorization, Content-Type, X-Requested-With, Accept, X-Gateway-Forwarded",
            }
        )
        return error_response