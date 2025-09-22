from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.services.category_service import CategoryService
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.core.security import verify_admin_token

router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Retrieve all active product categories"""
    categories = await CategoryService.get_categories(db, skip, limit)
    return categories

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific category by its ID"""
    category = await CategoryService.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=CategoryResponse)
async def create_category(
    name: str,
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """Create a new product category (Admin only)"""
    # In a real implementation, you would verify the admin token here
    # For now, we're just creating the category
    
    category_create = CategoryCreate(name=name)
    category = await CategoryService.create_category(db, category_create)
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    name: Optional[str] = None,
    image: Optional[UploadFile] = File(None),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing product category (Admin only)"""
    # In a real implementation, you would verify the admin token here
    # For now, we're just updating the category
    
    # Only include non-None values in the update
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if is_active is not None:
        update_data["is_active"] = is_active
        
    category_update = CategoryUpdate(**update_data)
    category = await CategoryService.update_category(db, category_id, category_update)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category