from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os

# Add the current directory to the path to make relative imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routing import router
from app.services import initialize_clients, close_clients

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway",
    description="Modular API Gateway for microservices with proper routing, service communication, and performance optimizations",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

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