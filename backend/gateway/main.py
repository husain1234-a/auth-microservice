from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os

# Add the current directory to the path to make relative imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routing import router
from app.services import initialize_clients, close_clients
from app.middleware.jwt_auth import JWTAuthMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway",
    description="Modular API Gateway for microservices with proper routing, service communication, and performance optimizations",
    version="2.0.0"
)

# Add CORS middleware first (middleware order matters - last added runs first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify exact origin instead of wildcard
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"], # Expose all headers
)

# Add JWT authentication middleware after CORS
app.add_middleware(JWTAuthMiddleware)

# Include API routes
app.include_router(router)

# Add security middleware
@app.middleware("http")
async def security_headers(request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Add CORS headers explicitly
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Requested-With, Accept, X-Gateway-Forwarded"
    
    return response

@app.on_event("startup")
async def startup_event():
    """Initialize HTTP clients for all services"""
    await initialize_clients()
    logger.info("Gateway started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Close all HTTP clients"""
    await close_clients()
    logger.info("Gateway shutdown completed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)