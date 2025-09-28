from fastapi import FastAPI
from .routers import auth
from .middleware.cors import setup_cors
from .database import init_db
from config.firebase import initialize_firebase

# Initialize Firebase
initialize_firebase()

app = FastAPI(
    title="Authentication Microservice",
    description="Secure authentication service with Firebase integration",
    version="1.0.0"
)

# Setup CORS
setup_cors(app)

# Include routers
app.include_router(auth.router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    from .database import close_db
    await close_db()

@app.get("/")
async def root():
    return {"message": "Authentication Microservice", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Basic health check including database connectivity"""
    from .database import check_database_health
    
    db_healthy = await check_database_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "auth-service",
        "version": "1.0.0",
        "database": {
            "status": "connected" if db_healthy else "disconnected",
            "database_name": "auth_db"
        }
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with connection pool and database metrics"""
    from .utils.db_monitor import comprehensive_health_check
    
    return await comprehensive_health_check()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)