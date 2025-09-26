from fastapi import APIRouter
from app.routes import cart

router = APIRouter()

router.include_router(cart.router)