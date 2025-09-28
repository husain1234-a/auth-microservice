"""
Cart Service Application Entry Point

This module initializes the FastAPI application for the Cart microservice.
It sets up routes, middleware, and application-level configurations.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routes import api
import time

# Import models to ensure they're registered with SQLAlchemy
from app.models import user, cart

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

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    print(f"🌐 {request.method} {request.url}")
    print(f"📋 Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    print(f"⏱️ Request completed in {process_time:.4f}s with status {response.status_code}")
    
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000","http://localhost:8001","http://localhost:8002","http://localhost:8003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Database lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    from app.core.database import init_db
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    from app.core.database import close_db
    await close_db()

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
    """Basic health check including database connectivity.
    
    Returns:
        dict: Status information about the service including database health
    """
    from app.core.database import check_database_health
    
    db_healthy = await check_database_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "cart-service",
        "version": "1.0.0",
        "database": {
            "status": "connected" if db_healthy else "disconnected",
            "database_name": "cart_db"
        }
    }

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with connection pool and database metrics.
    
    Returns:
        dict: Comprehensive health information including pool status
    """
    from app.utils.db_monitor import comprehensive_health_check
    
    return await comprehensive_health_check()

@app.post("/test-auth", tags=["Health"])
async def test_auth(request: Request):
    """Test endpoint to check Firebase token verification.
    
    Returns:
        dict: Token verification result
    """
    try:
        from app.core.security import get_current_user_id
        from fastapi import Header
        
        # Get authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header:
            return {"error": "No authorization header provided", "headers": dict(request.headers)}
        
        # Try to verify the token
        user_id = await get_current_user_id(auth_header)
        return {"success": True, "user_id": user_id}
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "headers": dict(request.headers)}