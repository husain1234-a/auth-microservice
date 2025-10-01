from typing import List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
# Remove selectinload import
# from sqlalchemy.orm import selectinload
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
        # Remove selectinload to eagerly load the category relationship
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
        # Remove selectinload to eagerly load the category relationship
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
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
        
        # Remove fetching the product again with the category relationship loaded
        # After refreshing, fetch the product
        result = await db.execute(
            select(Product).where(Product.id == db_product.id)
        )
        return result.scalar_one()
        
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
        
        # Remove fetching the product again with the category relationship loaded
        # After refreshing, fetch the product
        result = await db.execute(
            select(Product).where(Product.id == db_product.id)
        )
        return result.scalar_one()

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

    @staticmethod
    async def update_products_category_name(db: AsyncSession, category_id: int, category_name: str) -> int:
        """Update category_name for all products with the given category_id"""
        # Use bulk update for better performance
        result = await db.execute(
            select(Product).where(Product.category_id == category_id)
        )
        products = result.scalars().all()
        
        updated_count = 0
        for product in products:
            setattr(product, 'category_name', category_name)
            updated_count += 1
            
        if updated_count > 0:
            await db.commit()
            
        return updated_count