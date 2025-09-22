from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from fastapi import UploadFile
from app.schemas.category import CategoryResponse

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    mrp: Optional[float] = None
    category_id: int
    stock_quantity: int = 0
    unit: Optional[str] = None

class ProductCreate(ProductBase):
    image: Optional[UploadFile] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    mrp: Optional[float] = None
    category_id: Optional[int] = None
    image: Optional[UploadFile] = None
    stock_quantity: Optional[int] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True