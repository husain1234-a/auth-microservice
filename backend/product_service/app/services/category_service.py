from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from typing import Sequence


class CategoryService:
    @staticmethod
    async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Category]:
        """Get all categories"""
        result = await db.execute(select(Category).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_category(db: AsyncSession, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        result = await db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_category(db: AsyncSession, category: CategoryCreate) -> Category:
        """Create new category"""
        # Create a dictionary with the category data
        category_data = category.model_dump(exclude_unset=True)
        db_category = Category(**category_data)
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        return db_category

    @staticmethod
    async def update_category(db: AsyncSession, category_id: int, category_update: CategoryUpdate) -> Optional[Category]:
        """Update category"""
        result = await db.execute(select(Category).where(Category.id == category_id))
        db_category = result.scalar_one_or_none()
        if not db_category:
            return None
            
        update_data = category_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
            
        await db.commit()
        await db.refresh(db_category)
        return db_category

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int) -> bool:
        """Delete category (soft delete by setting is_active to False)"""
        result = await db.execute(select(Category).where(Category.id == category_id))
        db_category = result.scalar_one_or_none()
        if not db_category:
            return False
            
        setattr(db_category, 'is_active', False)
        await db.commit()
        return True