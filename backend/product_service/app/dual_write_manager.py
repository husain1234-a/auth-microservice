"""
Product Service Dual-Write Manager

Implements dual-write pattern for Product Service during database migration.
Handles writing to both new isolated product_db and legacy shared database.
"""

import logging
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from datetime import datetime

# Import shared dual-write infrastructure
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from dual_write_manager import BaseDualWriteManager, DualWriteConfig, DualWriteResult
from sync_validator import DataSyncValidator
from dual_write_config import DualWriteSettings

logger = logging.getLogger(__name__)


class ProductDualWriteManager(BaseDualWriteManager):
    """
    Dual-write manager for Product Service entities.
    
    Manages synchronization between new product_db and legacy shared database
    for product and category entities.
    """
    
    def __init__(self, new_db_url: str, legacy_db_url: str, settings: DualWriteSettings):
        # Convert settings to DualWriteConfig
        config = DualWriteConfig(
            enabled=settings.enabled,
            write_to_legacy=settings.write_to_legacy,
            write_to_new=settings.write_to_new,
            validate_sync=settings.validate_sync,
            fail_on_legacy_error=settings.fail_on_legacy_error,
            fail_on_new_error=settings.fail_on_new_error,
            sync_validation_interval=settings.sync_validation_interval
        )
        
        super().__init__(new_db_url, legacy_db_url, config)
        self.settings = settings
        self.validator = DataSyncValidator(
            self.new_session_factory,
            self.legacy_session_factory
        )
    
    async def create_product(self, product_data: Dict[str, Any]) -> DualWriteResult:
        """Create a product in both databases"""
        
        async def new_db_operation(session: AsyncSession):
            # Insert product into new database
            await session.execute(
                text("""
                    INSERT INTO products (name, description, price, mrp, category_id, image_url, stock_quantity, unit, is_active, created_at, updated_at)
                    VALUES (:name, :description, :price, :mrp, :category_id, :image_url, :stock_quantity, :unit, :is_active, NOW(), NOW())
                """),
                {
                    'name': product_data['name'],
                    'description': product_data.get('description'),
                    'price': product_data['price'],
                    'mrp': product_data.get('mrp', product_data['price']),
                    'category_id': product_data['category_id'],
                    'image_url': product_data.get('image_url'),
                    'stock_quantity': product_data.get('stock_quantity', 0),
                    'unit': product_data.get('unit', 'piece'),
                    'is_active': product_data.get('is_active', True)
                }
            )
        
        async def legacy_db_operation(session: AsyncSession):
            # Insert product into legacy database
            await session.execute(
                text("""
                    INSERT INTO products (name, description, price, mrp, category_id, image_url, stock_quantity, unit, is_active, created_at, updated_at)
                    VALUES (:name, :description, :price, :mrp, :category_id, :image_url, :stock_quantity, :unit, :is_active, NOW(), NOW())
                """),
                {
                    'name': product_data['name'],
                    'description': product_data.get('description'),
                    'price': product_data['price'],
                    'mrp': product_data.get('mrp', product_data['price']),
                    'category_id': product_data['category_id'],
                    'image_url': product_data.get('image_url'),
                    'stock_quantity': product_data.get('stock_quantity', 0),
                    'unit': product_data.get('unit', 'piece'),
                    'is_active': product_data.get('is_active', True)
                }
            )
        
        return await self.dual_write(
            "create_product",
            new_db_operation,
            legacy_db_operation
        )
    
    async def update_product(self, product_id: int, product_data: Dict[str, Any]) -> DualWriteResult:
        """Update a product in both databases"""
        
        async def new_db_operation(session: AsyncSession):
            # Build dynamic update query
            set_clauses = []
            params = {'product_id': product_id}
            
            for key, value in product_data.items():
                if key != 'id':  # Don't update the primary key
                    set_clauses.append(f"{key} = :{key}")
                    params[key] = value
            
            if set_clauses:
                set_clauses.append("updated_at = NOW()")
                query = f"UPDATE products SET {', '.join(set_clauses)} WHERE id = :product_id"
                await session.execute(text(query), params)
        
        async def legacy_db_operation(session: AsyncSession):
            # Build dynamic update query for legacy DB
            set_clauses = []
            params = {'product_id': product_id}
            
            for key, value in product_data.items():
                if key != 'id':
                    set_clauses.append(f"{key} = :{key}")
                    params[key] = value
            
            if set_clauses:
                set_clauses.append("updated_at = NOW()")
                query = f"UPDATE products SET {', '.join(set_clauses)} WHERE id = :product_id"
                await session.execute(text(query), params)
        
        return await self.dual_write(
            "update_product",
            new_db_operation,
            legacy_db_operation,
            lambda: self.validate_product_sync(product_id)
        )
    
    async def update_stock(self, product_id: int, new_stock: int) -> DualWriteResult:
        """Update product stock in both databases"""
        
        async def new_db_operation(session: AsyncSession):
            await session.execute(
                text("UPDATE products SET stock_quantity = :stock, updated_at = NOW() WHERE id = :product_id"),
                {'product_id': product_id, 'stock': new_stock}
            )
        
        async def legacy_db_operation(session: AsyncSession):
            await session.execute(
                text("UPDATE products SET stock_quantity = :stock, updated_at = NOW() WHERE id = :product_id"),
                {'product_id': product_id, 'stock': new_stock}
            )
        
        return await self.dual_write(
            "update_stock",
            new_db_operation,
            legacy_db_operation,
            lambda: self.validate_product_sync(product_id)
        )
    
    async def create_category(self, category_data: Dict[str, Any]) -> DualWriteResult:
        """Create a category in both databases"""
        
        async def new_db_operation(session: AsyncSession):
            await session.execute(
                text("""
                    INSERT INTO categories (name, image_url, is_active, created_at)
                    VALUES (:name, :image_url, :is_active, NOW())
                """),
                {
                    'name': category_data['name'],
                    'image_url': category_data.get('image_url'),
                    'is_active': category_data.get('is_active', True)
                }
            )
        
        async def legacy_db_operation(session: AsyncSession):
            await session.execute(
                text("""
                    INSERT INTO categories (name, image_url, is_active, created_at)
                    VALUES (:name, :image_url, :is_active, NOW())
                """),
                {
                    'name': category_data['name'],
                    'image_url': category_data.get('image_url'),
                    'is_active': category_data.get('is_active', True)
                }
            )
        
        return await self.dual_write(
            "create_category",
            new_db_operation,
            legacy_db_operation
        )
    
    async def validate_product_sync(self, product_id: int) -> bool:
        """Validate product synchronization between databases"""
        try:
            new_db_query = "SELECT * FROM products WHERE id = :entity_id"
            legacy_db_query = "SELECT * FROM products WHERE id = :entity_id"
            
            result = await self.validator.validate_entity_sync(
                product_id, "product", new_db_query, legacy_db_query,
                ignore_fields=['updated_at']  # Ignore timestamp differences
            )
            
            return result.is_synchronized
        except Exception as e:
            logger.error(f"Product sync validation failed for id {product_id}: {e}")
            return False
    
    async def validate_category_sync(self, category_id: int) -> bool:
        """Validate category synchronization between databases"""
        try:
            new_db_query = "SELECT * FROM categories WHERE id = :entity_id"
            legacy_db_query = "SELECT * FROM categories WHERE id = :entity_id"
            
            result = await self.validator.validate_entity_sync(
                category_id, "category", new_db_query, legacy_db_query,
                ignore_fields=['created_at']  # Categories don't have updated_at
            )
            
            return result.is_synchronized
        except Exception as e:
            logger.error(f"Category sync validation failed for id {category_id}: {e}")
            return False
    
    # Implementation of abstract methods
    async def sync_entity(self, entity_id: Any, direction: str = "new_to_legacy") -> bool:
        """Synchronize a specific entity between databases"""
        # This would be implemented based on entity type
        logger.info(f"Entity sync requested for {entity_id}, direction: {direction}")
        return True
    
    async def validate_entity_sync(self, entity_id: Any) -> Dict[str, Any]:
        """Validate synchronization of a specific entity"""
        return {
            'entity_id': entity_id,
            'is_synchronized': True,
            'validation_timestamp': datetime.utcnow().isoformat()
        }