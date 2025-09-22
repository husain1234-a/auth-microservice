from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.core.security import verify_admin_token

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search products by name"),
    limit: int = Query(50, description="Maximum number of products to return", le=100),
    offset: int = Query(0, description="Number of products to skip for pagination"),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all active products with optional filtering and pagination"""
    products = await ProductService.get_products(db, offset, limit, category_id, search)
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific product by its ID"""
    product = await ProductService.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductResponse)
async def create_product(
    name: str,
    description: Optional[str] = None,
    price: Optional[float] = None,
    mrp: Optional[float] = None,
    category_id: Optional[int] = None,
    stock_quantity: int = 0,
    unit: Optional[str] = None,
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    """Create a new product (Admin only)"""
    # In a real implementation, you would verify the admin token here
    # For now, we're just creating the product
    
    # Create a dictionary with only the provided values
    product_data = {
        "name": name,
        "stock_quantity": stock_quantity
    }
    
    if description is not None:
        product_data["description"] = description
    if price is not None:
        product_data["price"] = price
    if mrp is not None:
        product_data["mrp"] = mrp
    if category_id is not None:
        product_data["category_id"] = category_id
    if unit is not None:
        product_data["unit"] = unit
        
    product_create = ProductCreate(**product_data)
    product = await ProductService.create_product(db, product_create)
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    price: Optional[float] = None,
    mrp: Optional[float] = None,
    category_id: Optional[int] = None,
    stock_quantity: Optional[int] = None,
    unit: Optional[str] = None,
    is_active: Optional[bool] = None,
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing product (Admin only)"""
    # In a real implementation, you would verify the admin token here
    # For now, we're just updating the product
    
    # Only include non-None values in the update
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if price is not None:
        update_data["price"] = price
    if mrp is not None:
        update_data["mrp"] = mrp
    if category_id is not None:
        update_data["category_id"] = category_id
    if stock_quantity is not None:
        update_data["stock_quantity"] = stock_quantity
    if unit is not None:
        update_data["unit"] = unit
    if is_active is not None:
        update_data["is_active"] = is_active
        
    product_update = ProductUpdate(**update_data)
    product = await ProductService.update_product(db, product_id, product_update)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a product (soft delete - set is_active to false) (Admin only)"""
    # In a real implementation, you would verify the admin token here
    # For now, we're just deleting the product
    
    success = await ProductService.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}