from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway",
    description="API Gateway for microservices with proper routing and service communication",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service configuration
SERVICES = {
    "auth": {
        "url": os.getenv("AUTH_SERVICE_URL", "http://localhost:8001"),
        "prefix": "/auth"
    },
    "product": {
        "url": os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002"),
        "prefix": "/api"
    }
}

# Create HTTP clients for each service
http_clients: Dict[str, httpx.AsyncClient] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize HTTP clients for all services"""
    for service_name, service_config in SERVICES.items():
        http_clients[service_name] = httpx.AsyncClient(
            base_url=service_config["url"],
            timeout=30.0
        )
        logger.info(f"Initialized client for {service_name} service at {service_config['url']}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close all HTTP clients"""
    for client in http_clients.values():
        await client.aclose()
    logger.info("Closed all service clients")

@app.get("/health")
async def health_check():
    """Health check endpoint that verifies all services are reachable"""
    service_status = {}
    
    for service_name, client in http_clients.items():
        try:
            response = await client.get("/health")
            service_status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {str(e)}")
            service_status[service_name] = "unreachable"
    
    overall_status = "healthy" if all(status == "healthy" for status in service_status.values()) else "degraded"
    
    return {
        "status": overall_status,
        "services": service_status
    }

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_request(request: Request, path: str):
    """
    Main proxy route that forwards requests to appropriate services
    based on the path prefix
    """
    # Match the path to a service
    target_service: Optional[str] = None
    service_config: Optional[Dict[str, Any]] = None
    
    for service_name, config in SERVICES.items():
        if path.startswith(config["prefix"].lstrip("/")):
            target_service = service_name
            service_config = config
            break
    
    # If no service matches, return 404
    if not target_service or not service_config:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Prepare the path for the target service
    # Remove the service prefix from the path
    service_prefix = service_config["prefix"].lstrip("/")
    if path.startswith(service_prefix):
        target_path = path[len(service_prefix):]
        if not target_path.startswith("/"):
            target_path = "/" + target_path
    else:
        target_path = "/" + path
    
    # Get the HTTP client for the target service
    client = http_clients[target_service]
    
    # Prepare headers (excluding hop-by-hop headers)
    headers = dict(request.headers)
    headers.pop("host", None)
    
    try:
        # Forward the request to the target service
        logger.info(f"Forwarding {request.method} request to {target_service} service: {target_path}")
        
        if request.method == "GET":
            response = await client.get(target_path, headers=headers)
        elif request.method == "POST":
            response = await client.post(target_path, headers=headers, content=await request.body())
        elif request.method == "PUT":
            response = await client.put(target_path, headers=headers, content=await request.body())
        elif request.method == "DELETE":
            response = await client.delete(target_path, headers=headers)
        elif request.method == "PATCH":
            response = await client.patch(target_path, headers=headers, content=await request.body())
        elif request.method == "OPTIONS":
            response = await client.options(target_path, headers=headers)
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")
        
        # Return the response from the target service
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except httpx.TimeoutException:
        logger.error(f"Timeout when calling {target_service} service")
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except httpx.RequestError as e:
        logger.error(f"Error when calling {target_service} service: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error when calling {target_service} service: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)