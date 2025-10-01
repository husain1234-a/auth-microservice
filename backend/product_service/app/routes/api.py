from fastapi import APIRouter
from app.routes import categories, products, internal

api_router = APIRouter()
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(internal.router)