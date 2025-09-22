from typing import List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    @staticmethod
    async def get_products(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 50, 
        category_id: Optional[int] = None, 
        search: Optional[str] = None
    ) -> Sequence[Product]:
        """Get all products with optional filtering"""
        query = select(Product)
        
        # Apply filters
        if category_id:
            query = query.where(Product.category_id == category_id)
        if search:
            query = query.where(Product.name.contains(search))
            
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_product(db: AsyncSession, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        result = await db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_product(db: AsyncSession, product: ProductCreate) -> Product:
        """Create new product"""
        # Create a dictionary with the product data
        product_data = product.model_dump(exclude_unset=True)
        db_product = Product(**product_data)
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        return db_product

    @staticmethod
    async def update_product(db: AsyncSession, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
        """Update product"""
        result = await db.execute(select(Product).where(Product.id == product_id))
        db_product = result.scalar_one_or_none()
        if not db_product:
            return None
            
        update_data = product_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
            
        await db.commit()
        await db.refresh(db_product)
        return db_product

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: int) -> bool:
        """Delete product (soft delete by setting is_active to False)"""
        result = await db.execute(select(Product).where(Product.id == product_id))
        db_product = result.scalar_one_or_none()
        if not db_product:
            return False
            
        setattr(db_product, 'is_active', False)
        await db.commit()
        return True