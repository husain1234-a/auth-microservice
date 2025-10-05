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

@app.get("/")
async def root():
    return {"message": "Authentication Microservice", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)