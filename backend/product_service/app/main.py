from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.api import api_router
from app.core.config import settings
from app.core.init_db import init_db

app = FastAPI(
    title=settings.app_name,
    description="Product microservice for managing products and categories",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    from app.core.database import close_db
    await close_db()

# Include API routes
app.include_router(api_router)

@app.get("/health")
async def health_check():
    """Basic health check including database connectivity"""
    from app.core.database import check_database_health
    
    db_healthy = await check_database_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "product-service",
        "version": "1.0.0",
        "database": {
            "status": "connected" if db_healthy else "disconnected",
            "database_name": "product_db"
        }
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with connection pool and database metrics"""
    from app.utils.db_monitor import comprehensive_health_check
    
    return await comprehensive_health_check()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)