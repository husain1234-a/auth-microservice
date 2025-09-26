"""
Cart Service Application Entry Point

This module initializes the FastAPI application for the Cart microservice.
It sets up routes, middleware, and application-level configurations.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import api

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Cart Service",
    description="Microservice for managing user shopping carts in the e-commerce platform",
    version="1.0.0",
    contact={
        "name": "Development Team",
        "email": "dev-team@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000","http://localhost:8001","http://localhost:8002","http://localhost:8003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include API routes with version prefix
app.include_router(api.router, prefix="/api/v1")

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for basic service health check.
    
    Returns:
        dict: Simple message indicating the service is running
    """
    return {"message": "Cart Service is running"}

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for service monitoring.
    
    Returns:
        dict: Status information about the service
    """
    return {
        "status": "healthy",
        "service": "cart-service",
        "version": "1.0.0"
    }