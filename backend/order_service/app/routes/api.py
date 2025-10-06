from fastapi import APIRouter
from app.routes import orders, templates, feedback, analytics

api_router = APIRouter()

api_router.include_router(orders.router)
api_router.include_router(templates.router)
api_router.include_router(feedback.router)
api_router.include_router(analytics.router)

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "order-service"}