from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.core.firebase_auth import get_current_user_id

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
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    mrp: Optional[float] = Form(None),
    category_id: int = Form(...),
    stock_quantity: int = Form(0),
    unit: Optional[str] = Form(None),
    image: UploadFile = File(None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new product (Admin only)"""
    # TODO: Verify admin role
    # For now, we're just creating the product
    
    # Create a dictionary with only the provided values
    product_data = {
        "name": name,
        "price": price,
        "category_id": category_id,
        "stock_quantity": stock_quantity
    }
    
    if description is not None:
        product_data["description"] = description
    if mrp is not None:
        product_data["mrp"] = mrp
    if unit is not None:
        product_data["unit"] = unit
        
    # Handle image upload if provided
    image_url = None
    if image and image.filename:
        from app.utils.image_service import ImageService
        image_service = ImageService()
        try:
            image_url = await image_service.upload_image(image, "products")
            product_data["image_url"] = image_url
        except Exception as e:
            # If image upload fails, we can either raise an error or continue without image
            # For now, we'll continue without the image
            pass
        
    product_create = ProductCreate(**product_data)
    product = await ProductService.create_product(db, product_create)
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    mrp: Optional[float] = Form(None),
    category_id: Optional[int] = Form(None),
    stock_quantity: Optional[int] = Form(None),
    unit: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    image: UploadFile = File(None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing product (Admin only)"""
    # TODO: Verify admin role
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
        
    # Handle image upload if provided
    if image and image.filename:
        from app.utils.image_service import ImageService
        image_service = ImageService()
        try:
            image_url = await image_service.upload_image(image, "products")
            update_data["image_url"] = image_url
        except Exception as e:
            # If image upload fails, we can either raise an error or continue without image
            # For now, we'll continue without the image
            pass
        
    product_update = ProductUpdate(**update_data)
    product = await ProductService.update_product(db, product_id, product_update)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}")
async def delete_product(product_id: int, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """Delete a product (soft delete - set is_active to false) (Admin only)"""
    # TODO: Verify admin role
    # For now, we're just deleting the product
    
    success = await ProductService.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}