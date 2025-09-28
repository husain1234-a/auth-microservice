"""
Cart Service with Dual-Write Support

This service layer implements cart operations with dual-write functionality
during the database migration phase.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime

from app.models.cart import Cart, CartItem, Wishlist, WishlistItem
from app.models.user import User
from app.core.database import get_db, get_dual_write_manager
from app.core.dual_write_manager import CartDualWriteManager

logger = logging.getLogger(__name__)


class CartService:
    """
    Cart service with dual-write support for database migration.
    
    This service handles all cart-related operations and automatically
    writes to both new and legacy databases when dual-write is enabled.
    """
    
    def __init__(self):
        self.dual_write_manager: Optional[CartDualWriteManager] = None
    
    async def _get_dual_write_manager(self) -> Optional[CartDualWriteManager]:
        """Get dual-write manager instance"""
        if not self.dual_write_manager:
            self.dual_write_manager = get_dual_write_manager()
        return self.dual_write_manager
    
    async def create_cart_for_user(self, user_id: str) -> Dict[str, Any]:
        """
        Create a cart for a user.
        Uses dual-write if enabled, otherwise writes only to new database.
        """
        dual_write_manager = await self._get_dual_write_manager()
        
        if dual_write_manager:
            # Use dual-write
            result = await dual_write_manager.create_cart(user_id)
            
            if result.success:
                # Get the created cart from new database
                async for session in get_db():
                    cart_result = await session.execute(
                        select(Cart).where(Cart.user_id == user_id)
                    )
                    cart = cart_result.scalar_one_or_none()
                    
                    if cart:
                        return {
                            'id': cart.id,
                            'user_id': cart.user_id,
                            'created_at': cart.created_at,
                            'updated_at': cart.updated_at,
                            'dual_write_result': result.to_dict()
                        }
                    break
            else:
                logger.error(f"Failed to create cart for user {user_id}: {result.to_dict()}")
                raise Exception("Failed to create cart")
        else:
            # Single database write
            async for session in get_db():
                try:
                    # Check if cart already exists
                    existing_cart = await session.execute(
                        select(Cart).where(Cart.user_id == user_id)
                    )
                    cart = existing_cart.scalar_one_or_none()
                    
                    if not cart:
                        cart = Cart(user_id=user_id)
                        session.add(cart)
                        await session.commit()
                        await session.refresh(cart)
                    
                    return {
                        'id': cart.id,
                        'user_id': cart.user_id,
                        'created_at': cart.created_at,
                        'updated_at': cart.updated_at
                    }
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Error creating cart for user {user_id}: {e}")
                    raise
                finally:
                    break
    
    async def add_item_to_cart(
        self, 
        user_id: str, 
        product_id: int, 
        quantity: int
    ) -> Dict[str, Any]:
        """
        Add an item to user's cart.
        Uses dual-write if enabled.
        """
        # First ensure cart exists
        cart_data = await self.create_cart_for_user(user_id)
        cart_id = cart_data['id']
        
        dual_write_manager = await self._get_dual_write_manager()
        
        if dual_write_manager:
            # Use dual-write
            result = await dual_write_manager.add_cart_item(cart_id, product_id, quantity)
            
            if result.success:
                # Get the cart item from new database
                async for session in get_db():
                    item_result = await session.execute(
                        select(CartItem).where(
                            CartItem.cart_id == cart_id,
                            CartItem.product_id == product_id
                        )
                    )
                    cart_item = item_result.scalar_one_or_none()
                    
                    if cart_item:
                        return {
                            'id': cart_item.id,
                            'cart_id': cart_item.cart_id,
                            'product_id': cart_item.product_id,
                            'quantity': cart_item.quantity,
                            'created_at': cart_item.created_at,
                            'updated_at': cart_item.updated_at,
                            'dual_write_result': result.to_dict()
                        }
                    break
            else:
                logger.error(f"Failed to add item to cart: {result.to_dict()}")
                raise Exception("Failed to add item to cart")
        else:
            # Single database write
            async for session in get_db():
                try:
                    # Check if item already exists
                    existing_item = await session.execute(
                        select(CartItem).where(
                            CartItem.cart_id == cart_id,
                            CartItem.product_id == product_id
                        )
                    )
                    cart_item = existing_item.scalar_one_or_none()
                    
                    if cart_item:
                        cart_item.quantity = quantity
                        cart_item.updated_at = datetime.utcnow()
                    else:
                        cart_item = CartItem(
                            cart_id=cart_id,
                            product_id=product_id,
                            quantity=quantity
                        )
                        session.add(cart_item)
                    
                    await session.commit()
                    await session.refresh(cart_item)
                    
                    return {
                        'id': cart_item.id,
                        'cart_id': cart_item.cart_id,
                        'product_id': cart_item.product_id,
                        'quantity': cart_item.quantity,
                        'created_at': cart_item.created_at,
                        'updated_at': cart_item.updated_at
                    }
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Error adding item to cart: {e}")
                    raise
                finally:
                    break
    
    async def remove_item_from_cart(
        self, 
        user_id: str, 
        product_id: int
    ) -> Dict[str, Any]:
        """
        Remove an item from user's cart.
        Uses dual-write if enabled.
        """
        # Get user's cart
        async for session in get_db():
            cart_result = await session.execute(
                select(Cart).where(Cart.user_id == user_id)
            )
            cart = cart_result.scalar_one_or_none()
            
            if not cart:
                raise Exception("Cart not found")
            
            cart_id = cart.id
            break
        
        dual_write_manager = await self._get_dual_write_manager()
        
        if dual_write_manager:
            # Use dual-write
            result = await dual_write_manager.remove_cart_item(cart_id, product_id)
            
            return {
                'success': result.success,
                'dual_write_result': result.to_dict()
            }
        else:
            # Single database write
            async for session in get_db():
                try:
                    result = await session.execute(
                        select(CartItem).where(
                            CartItem.cart_id == cart_id,
                            CartItem.product_id == product_id
                        )
                    )
                    cart_item = result.scalar_one_or_none()
                    
                    if cart_item:
                        await session.delete(cart_item)
                        await session.commit()
                    
                    return {'success': True}
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Error removing item from cart: {e}")
                    raise
                finally:
                    break
    
    async def get_cart_contents(self, user_id: str) -> Dict[str, Any]:
        """Get cart contents for a user"""
        async for session in get_db():
            try:
                # Get cart with items
                cart_result = await session.execute(
                    select(Cart).where(Cart.user_id == user_id)
                )
                cart = cart_result.scalar_one_or_none()
                
                if not cart:
                    return {
                        'cart_id': None,
                        'user_id': user_id,
                        'items': [],
                        'total_items': 0
                    }
                
                # Get cart items
                items_result = await session.execute(
                    select(CartItem).where(CartItem.cart_id == cart.id)
                )
                items = items_result.scalars().all()
                
                cart_items = []
                for item in items:
                    cart_items.append({
                        'id': item.id,
                        'product_id': item.product_id,
                        'quantity': item.quantity,
                        'created_at': item.created_at,
                        'updated_at': item.updated_at
                    })
                
                return {
                    'cart_id': cart.id,
                    'user_id': cart.user_id,
                    'items': cart_items,
                    'total_items': len(cart_items),
                    'created_at': cart.created_at,
                    'updated_at': cart.updated_at
                }
            except Exception as e:
                logger.error(f"Error getting cart contents for user {user_id}: {e}")
                raise
            finally:
                break
    
    async def clear_cart(self, user_id: str) -> Dict[str, Any]:
        """Clear all items from user's cart"""
        async for session in get_db():
            try:
                # Get cart
                cart_result = await session.execute(
                    select(Cart).where(Cart.user_id == user_id)
                )
                cart = cart_result.scalar_one_or_none()
                
                if not cart:
                    return {'success': True, 'message': 'Cart not found'}
                
                # Delete all cart items
                await session.execute(
                    delete(CartItem).where(CartItem.cart_id == cart.id)
                )
                
                await session.commit()
                
                return {'success': True, 'message': 'Cart cleared'}
            except Exception as e:
                await session.rollback()
                logger.error(f"Error clearing cart for user {user_id}: {e}")
                raise
            finally:
                break
    
    async def sync_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync user data to cart service database.
        This is used when user data changes in the auth service.
        """
        dual_write_manager = await self._get_dual_write_manager()
        
        if dual_write_manager:
            result = await dual_write_manager.sync_user(user_data)
            return {
                'success': result.success,
                'dual_write_result': result.to_dict()
            }
        else:
            # Single database write
            async for session in get_db():
                try:
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
                    
                    await session.commit()
                    
                    return {'success': True}
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Error syncing user data: {e}")
                    raise
                finally:
                    break
    
    async def get_dual_write_status(self) -> Dict[str, Any]:
        """Get dual-write status and health information"""
        dual_write_manager = await self._get_dual_write_manager()
        
        if dual_write_manager:
            health_status = await dual_write_manager.health_check()
            return {
                'dual_write_enabled': True,
                'health_status': health_status
            }
        else:
            return {
                'dual_write_enabled': False,
                'message': 'Dual-write not configured or disabled'
            }