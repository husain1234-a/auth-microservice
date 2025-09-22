from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from fastapi import UploadFile

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    image_url: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: int
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True