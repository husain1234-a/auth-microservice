from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.api import api_router
from app.core.config import settings
from app.core.database import init_db

app = FastAPI(
    title=settings.app_name,
    description="Product microservice for managing products and categories",
    version="1.0.0",
    redirect_slashes=False  # Disable automatic trailing slash redirects
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

# Include API routes
app.include_router(api_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)