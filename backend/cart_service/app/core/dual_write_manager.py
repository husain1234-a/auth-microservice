"""
Cart Service Dual-Write Manager

Implements dual-write pattern for Cart Service during database migration.
Handles writing to both new isolated cart_db and legacy shared database.
"""

import logging
from typing import Any, Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from datetime import datetime

# Import shared dual-write infrastructure
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from dual_write_manager import BaseDualWriteManager, DualWriteConfig, DualWriteResult
from sync_validator import DataSyncValidator, SyncValidationResult
from dual_write_config import DualWriteSettings

from app.models.cart import Cart, CartItem, Wishlist, WishlistItem, PromoCode, CartPromoCode
from app.models.user import User

logger = logging.getLogger(__name__)


class CartDualWriteManager(BaseDualWriteManager):
    """
    Dual-write manager for Cart Service entities.
    
    Manages synchronization between new cart_db and legacy shared database
    for all cart-related entities: carts, cart_items, wishlists, wishlist_items,
    promo_codes, and cart_promo_codes.
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
    
    # Cart Operations
    async def create_cart(self, user_id: str) -> DualWriteResult:
        """Create a cart in both databases"""
        
        async def new_db_operation(session: AsyncSession):
            # Check if cart already exists
            existing_cart = await session.execute(
                select(Cart).where(Cart.user_id == user_id)
            )
            if existing_cart.scalar_one_or_none():
                return  # Cart already exists
            
            cart = Cart(user_id=user_id)
            session.add(cart)
            await session.flush()
            return cart.id
        
        async def legacy_db_operation(session: AsyncSession):
            # Check if cart already exists in legacy DB
            result = await session.execute(
                text("SELECT id FROM carts WHERE user_id = :user_id"),
                {'user_id': user_id}
            )
            if result.fetchone():
                return  # Cart already exists
            
            await session.execute(
                text("""
                    INSERT INTO carts (user_id, created_at, updated_at)
                    VALUES (:user_id, NOW(), NOW())
                """),
                {'user_id': user_id}
            )
        
        return await self.dual_write(
            "create_cart",
            new_db_operation,
            legacy_db_operation,
            lambda: self.validate_cart_sync(user_id)
        )
    
    async def add_cart_item(self, cart_id: int, product_id: int, quantity: int) -> DualWriteResult:
        """Add item to cart in both databases"""
        
        async def new_db_operation(session: AsyncSession):
            # Check if item already exists
            existing_item = await session.execute(
                select(CartItem).where(
                    CartItem.cart_id == cart_id,
                    CartItem.product_id == product_id
                )
            )
            existing = existing_item.scalar_one_or_none()
            
            if existing:
                existing.quantity = quantity
                existing.updated_at = datetime.utcnow()
            else:
                cart_item = CartItem(
                    cart_id=cart_id,
                    product_id=product_id,
                    quantity=quantity
                )
                session.add(cart_item)
            
            await session.flush()
        
        async def legacy_db_operation(session: AsyncSession):
            # Check if item exists in legacy DB
            result = await session.execute(
                text("""
                    SELECT id FROM cart_items 
                    WHERE cart_id = :cart_id AND product_id = :product_id
                """),
                {'cart_id': cart_id, 'product_id': product_id}
            )
            existing = result.fetchone()
            
            if existing:
                await session.execute(
                    text("""
                        UPDATE cart_items 
                        SET quantity = :quantity, updated_at = NOW()
                        WHERE cart_id = :cart_id AND product_id = :product_id
                    """),
                    {'cart_id': cart_id, 'product_id': product_id, 'quantity': quantity}
                )
            else:
                await session.execute(
                    text("""
                        INSERT INTO cart_items (cart_id, product_id, quantity, created_at, updated_at)
                        VALUES (:cart_id, :product_id, :quantity, NOW(), NOW())
                    """),
                    {'cart_id': cart_id, 'product_id': product_id, 'quantity': quantity}
                )
        
        return await self.dual_write(
            "add_cart_item",
            new_db_operation,
            legacy_db_operation,
            lambda: self.validate_cart_item_sync(cart_id, product_id)
        )
    
    async def remove_cart_item(self, cart_id: int, product_id: int) -> DualWriteResult:
        """Remove item from cart in both databases"""
        
        async def new_db_operation(session: AsyncSession):
            result = await session.execute(
                select(CartItem).where(
                    CartItem.cart_id == cart_id,
                    CartItem.product_id == product_id
                )
            )
            cart_item = result.scalar_one_or_none()
            if cart_item:
                await session.delete(cart_item)
        
        async def legacy_db_operation(session: AsyncSession):
            await session.execute(
                text("""
                    DELETE FROM cart_items 
                    WHERE cart_id = :cart_id AND product_id = :product_id
                """),
                {'cart_id': cart_id, 'product_id': product_id}
            )
        
        return await self.dual_write(
            "remove_cart_item",
            new_db_operation,
            legacy_db_operation
        )
    
    # Wishlist Operations
    async def create_wishlist(self, user_id: str) -> DualWriteResult:
        """Create a wishlist in both databases"""
        
        async def new_db_operation(session: AsyncSession):
            existing_wishlist = await session.execute(
                select(Wishlist).where(Wishlist.user_id == user_id)
            )
            if existing_wishlist.scalar_one_or_none():
                return  # Wishlist already exists
            
            wishlist = Wishlist(user_id=user_id)
            session.add(wishlist)
            await session.flush()
            return wishlist.id
        
        async def legacy_db_operation(session: AsyncSession):
            result = await session.execute(
                text("SELECT id FROM wishlists WHERE user_id = :user_id"),
                {'user_id': user_id}
            )
            if result.fetchone():
                return  # Wishlist already exists
            
            await session.execute(
                text("""
                    INSERT INTO wishlists (user_id, created_at, updated_at)
                    VALUES (:user_id, NOW(), NOW())
                """),
                {'user_id': user_id}
            )
        
        return await self.dual_write(
            "create_wishlist",
            new_db_operation,
            legacy_db_operation,
            lambda: self.validate_wishlist_sync(user_id)
        )
    
    async def add_wishlist_item(self, wishlist_id: int, product_id: int) -> DualWriteResult:
        """Add item to wishlist in both databases"""
        
        async def new_db_operation(session: AsyncSession):
            existing_item = await session.execute(
                select(WishlistItem).where(
                    WishlistItem.wishlist_id == wishlist_id,
                    WishlistItem.product_id == product_id
                )
            )
            if existing_item.scalar_one_or_none():
                return  # Item already in wishlist
            
            wishlist_item = WishlistItem(
                wishlist_id=wishlist_id,
                product_id=product_id
            )
            session.add(wishlist_item)
            await session.flush()
        
        async def legacy_db_operation(session: AsyncSession):
            result = await session.execute(
                text("""
                    SELECT id FROM wishlist_items 
                    WHERE wishlist_id = :wishlist_id AND product_id = :product_id
                """),
                {'wishlist_id': wishlist_id, 'product_id': product_id}
            )
            if result.fetchone():
                return  # Item already exists
            
            await session.execute(
                text("""
                    INSERT INTO wishlist_items (wishlist_id, product_id, created_at, updated_at)
                    VALUES (:wishlist_id, :product_id, NOW(), NOW())
                """),
                {'wishlist_id': wishlist_id, 'product_id': product_id}
            )
        
        return await self.dual_write(
            "add_wishlist_item",
            new_db_operation,
            legacy_db_operation,
            lambda: self.validate_wishlist_item_sync(wishlist_id, product_id)
        )
    
    # User Operations (for cart service user cache)
    async def sync_user(self, user_data: Dict[str, Any]) -> DualWriteResult:
        """Sync user data to cart service database"""
        
        async def new_db_operation(session: AsyncSession):
            existing_user = await session.execute(
                select(User).where(User.uid == user_data['uid'])
            )
            user = existing_user.scalar_one_or_none()
            
            if user:
                # Update existing user
                for key, value in user_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                user.updated_at = datetime.utcnow()
            else:
                # Create new user
                user = User(**user_data)
                session.add(user)
            
            await session.flush()
        
        async def legacy_db_operation(session: AsyncSession):
            # Legacy DB is the source of truth for users, no need to write back
            pass
        
        return await self.dual_write(
            "sync_user",
            new_db_operation,
            legacy_db_operation
        )
    
    # Validation Methods
    async def validate_cart_sync(self, user_id: str) -> bool:
        """Validate cart synchronization between databases"""
        try:
            new_db_query = "SELECT * FROM carts WHERE user_id = :entity_id"
            legacy_db_query = "SELECT * FROM carts WHERE user_id = :entity_id"
            
            result = await self.validator.validate_entity_sync(
                user_id, "cart", new_db_query, legacy_db_query,
                ignore_fields=['updated_at']  # Ignore timestamp differences
            )
            
            return result.is_synchronized
        except Exception as e:
            logger.error(f"Cart sync validation failed for user {user_id}: {e}")
            return False
    
    async def validate_cart_item_sync(self, cart_id: int, product_id: int) -> bool:
        """Validate cart item synchronization"""
        try:
            new_db_query = """
                SELECT * FROM cart_items 
                WHERE cart_id = :cart_id AND product_id = :product_id
            """
            legacy_db_query = """
                SELECT * FROM cart_items 
                WHERE cart_id = :cart_id AND product_id = :product_id
            """
            
            # Create composite entity ID for validation
            entity_id = f"{cart_id}_{product_id}"
            
            # Custom validation since we need two parameters
            async with self.new_session_factory() as new_session:
                new_result = await new_session.execute(
                    text(new_db_query), {'cart_id': cart_id, 'product_id': product_id}
                )
                new_data = new_result.fetchone()
            
            async with self.legacy_session_factory() as legacy_session:
                legacy_result = await legacy_session.execute(
                    text(legacy_db_query), {'cart_id': cart_id, 'product_id': product_id}
                )
                legacy_data = legacy_result.fetchone()
            
            # Both should exist or both should not exist
            if (new_data is None) != (legacy_data is None):
                return False
            
            if new_data and legacy_data:
                # Compare quantity (main field that matters)
                return new_data.quantity == legacy_data.quantity
            
            return True  # Both are None
            
        except Exception as e:
            logger.error(f"Cart item sync validation failed for cart {cart_id}, product {product_id}: {e}")
            return False
    
    async def validate_wishlist_sync(self, user_id: str) -> bool:
        """Validate wishlist synchronization"""
        try:
            new_db_query = "SELECT * FROM wishlists WHERE user_id = :entity_id"
            legacy_db_query = "SELECT * FROM wishlists WHERE user_id = :entity_id"
            
            result = await self.validator.validate_entity_sync(
                user_id, "wishlist", new_db_query, legacy_db_query,
                ignore_fields=['updated_at']
            )
            
            return result.is_synchronized
        except Exception as e:
            logger.error(f"Wishlist sync validation failed for user {user_id}: {e}")
            return False
    
    async def validate_wishlist_item_sync(self, wishlist_id: int, product_id: int) -> bool:
        """Validate wishlist item synchronization"""
        try:
            # Similar to cart item validation
            new_db_query = """
                SELECT * FROM wishlist_items 
                WHERE wishlist_id = :wishlist_id AND product_id = :product_id
            """
            legacy_db_query = """
                SELECT * FROM wishlist_items 
                WHERE wishlist_id = :wishlist_id AND product_id = :product_id
            """
            
            async with self.new_session_factory() as new_session:
                new_result = await new_session.execute(
                    text(new_db_query), {'wishlist_id': wishlist_id, 'product_id': product_id}
                )
                new_data = new_result.fetchone()
            
            async with self.legacy_session_factory() as legacy_session:
                legacy_result = await legacy_session.execute(
                    text(legacy_db_query), {'wishlist_id': wishlist_id, 'product_id': product_id}
                )
                legacy_data = legacy_result.fetchone()
            
            # Both should exist or both should not exist
            return (new_data is None) == (legacy_data is None)
            
        except Exception as e:
            logger.error(f"Wishlist item sync validation failed for wishlist {wishlist_id}, product {product_id}: {e}")
            return False
    
    # Implementation of abstract methods
    async def sync_entity(self, entity_id: Any, direction: str = "new_to_legacy") -> bool:
        """Synchronize a specific entity between databases"""
        # This would be implemented based on entity type
        # For now, return True as a placeholder
        logger.info(f"Entity sync requested for {entity_id}, direction: {direction}")
        return True
    
    async def validate_entity_sync(self, entity_id: Any) -> Dict[str, Any]:
        """Validate synchronization of a specific entity"""
        # This would be implemented based on entity type
        # For now, return basic validation result
        return {
            'entity_id': entity_id,
            'is_synchronized': True,
            'validation_timestamp': datetime.utcnow().isoformat()
        }