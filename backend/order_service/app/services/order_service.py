import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from app.models.order import Order, OrderItem, OrderTemplate, OrderFeedback, OrderStatus
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderStatusUpdate, 
    AssignDeliveryPartnerRequest, OrderItemsUpdate,
    OrderTemplateCreate, OrderFeedbackCreate,
    BulkStatusUpdate, BulkAssignDelivery
)
from app.services.cart_service import CartService
from app.services.product_service import ProductService
from app.services.notification_service import NotificationService
from app.services.payment_service import PaymentService

logger = logging.getLogger(__name__)

class OrderService:
    """Main service for handling order-related operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_order_from_cart(self, user_id: str, order_data: OrderCreate, auth_headers: Optional[Dict[str, str]] = None) -> Order:
        """Create a new order from the user's cart"""
        try:
            # Get cart items
            cart_items = await CartService.get_cart_items(user_id, auth_headers)
            if not cart_items:
                raise ValueError("Cart is empty")
            
            # Validate products and calculate total
            total_amount = 0.0
            order_items = []
            
            for item in cart_items:
                product_id = item["product_id"]
                quantity = item["quantity"]
                
                # Check product availability
                if not await ProductService.check_product_availability(product_id, quantity):
                    raise ValueError(f"Insufficient stock for product {product_id}")
                
                # Get product price
                price = await ProductService.get_product_price(product_id)
                if price is None:
                    raise ValueError(f"Product {product_id} not found")
                
                item_total = price * quantity
                total_amount += item_total
                
                order_items.append({
                    "product_id": product_id,
                    "quantity": quantity,
                    "price": price
                })
            
            # Calculate delivery fee (simplified)
            delivery_fee = 5.0
            total_amount += delivery_fee
            
            # Create order
            db_order = Order(
                user_id=user_id,
                delivery_address=order_data.delivery_address,
                delivery_latitude=order_data.delivery_latitude,
                delivery_longitude=order_data.delivery_longitude,
                total_amount=total_amount,
                delivery_fee=delivery_fee,
                scheduled_for=order_data.scheduled_for,
                status=OrderStatus.CONFIRMED if order_data.scheduled_for else OrderStatus.PENDING
            )
            
            self.db.add(db_order)
            await self.db.flush()
            
            # Create order items
            for item in order_items:
                db_item = OrderItem(
                    order_id=db_order.id,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    price=item["price"]
                )
                self.db.add(db_item)
            
            # Clear cart
            await CartService.clear_cart(user_id, auth_headers)
            
            # Send confirmation notification
            order_id_value = db_order.__dict__.get('id', db_order.id)
            user_id_value = db_order.__dict__.get('user_id', db_order.user_id)
            await NotificationService.send_order_confirmation_email(str(user_id_value), int(order_id_value), float(total_amount))
            
            await self.db.commit()
            await self.db.refresh(db_order)
            
            return db_order
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating order from cart: {str(e)}")
            raise
    
    async def get_user_orders(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Order]:
        """Get orders for a specific user"""
        try:
            result = await self.db.execute(
                select(Order)
                .where(Order.user_id == user_id)
                .order_by(Order.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            orders = list(result.scalars().all())
            
            # Load order items for each order manually
            for order in orders:
                items_result = await self.db.execute(
                    select(OrderItem).where(OrderItem.order_id == order.id)
                )
                order.items = items_result.scalars().all()
                
                # Load product details for each item
                for item in order.items:
                    try:
                        product = await ProductService.get_product(item.product_id)
                        setattr(item, 'product', product)
                    except Exception:
                        # If product is not found, skip it
                        pass
            
            return orders
        except Exception as e:
            logger.error(f"Error fetching user orders: {str(e)}")
            raise
    
    async def get_order_by_id(self, order_id: int, user_id: Optional[str] = None) -> Optional[Order]:
        """Get a specific order by ID, optionally checking user ownership"""
        try:
            query = select(Order).where(Order.id == order_id)
            if user_id:
                query = query.where(Order.user_id == user_id)
            
            result = await self.db.execute(query)
            order = result.scalars().first()
            
            if order:
                # Load order items manually
                items_result = await self.db.execute(
                    select(OrderItem).where(OrderItem.order_id == order.id)
                )
                order.items = items_result.scalars().all()
                
                # Load product details for each item
                for item in order.items:
                    try:
                        product = await ProductService.get_product(item.product_id)
                        setattr(item, 'product', product)
                    except Exception:
                        # If product is not found, skip it
                        pass
                
                # Load feedback if exists
                feedback_result = await self.db.execute(
                    select(OrderFeedback).where(OrderFeedback.order_id == order.id)
                )
                feedback = feedback_result.scalars().first()
                if feedback:
                    order.feedback = feedback
            
            return order
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {str(e)}")
            raise
    
    async def update_order_status(self, order_id: int, status_update: OrderStatusUpdate) -> Optional[Order]:
        """Update the status of an order"""
        try:
            db_order = await self.get_order_by_id(order_id)
            if not db_order:
                return None
            
            # Update status
            setattr(db_order, 'status', status_update.status.value if hasattr(status_update.status, 'value') else status_update.status)
            
            # Set delivered_at timestamp if status is delivered
            if status_update.status == OrderStatus.DELIVERED:
                setattr(db_order, 'delivered_at', datetime.utcnow())
            
            # Set cancelled_at timestamp if status is cancelled
            if status_update.status == OrderStatus.CANCELLED:
                setattr(db_order, 'cancelled_at', datetime.utcnow())
            
            await self.db.commit()
            await self.db.refresh(db_order)
            
            # Send notification
            user_id_value = db_order.__dict__.get('user_id', db_order.user_id)
            order_id_value = db_order.__dict__.get('id', db_order.id)
            status_value = db_order.__dict__.get('status', status_update.status)
            await NotificationService.send_order_notification(
                str(user_id_value),
                int(order_id_value),
                str(status_value)
            )
            
            return db_order
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating order status for order {order_id}: {str(e)}")
            raise
    
    async def assign_delivery_partner(self, order_id: int, assign_data: AssignDeliveryPartnerRequest) -> Optional[Order]:
        """Assign a delivery partner to an order"""
        try:
            db_order = await self.get_order_by_id(order_id)
            if not db_order:
                return None
            
            setattr(db_order, 'delivery_partner_id', assign_data.delivery_partner_id)
            setattr(db_order, 'status', OrderStatus.CONFIRMED.value)
            
            await self.db.commit()
            await self.db.refresh(db_order)
            
            return db_order
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error assigning delivery partner to order {order_id}: {str(e)}")
            raise
    
    async def cancel_order(self, order_id: int, user_id: str) -> Dict[str, Any]:
        """Cancel an order if eligible"""
        try:
            db_order = await self.get_order_by_id(order_id, user_id)
            if not db_order:
                raise ValueError("Order not found")
            
            # Check if order can be cancelled
            order_status = getattr(db_order, 'status', db_order.status)
            if order_status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
                raise ValueError("Order cannot be cancelled at this stage")
            
            # Update order status
            setattr(db_order, 'status', OrderStatus.CANCELLED.value)
            setattr(db_order, 'cancelled_at', datetime.utcnow())
            
            # Initiate refund
            refund_initiated = False
            try:
                order_id_value = db_order.__dict__.get('id', db_order.id)
                total_amount_value = db_order.__dict__.get('total_amount', db_order.total_amount)
                refund_result = await PaymentService.initiate_refund(
                    user_id, int(order_id_value), float(total_amount_value)
                )
                refund_initiated = refund_result.get("success", False)
            except Exception as e:
                logger.error(f"Error initiating refund for order {order_id}: {str(e)}")
            
            await self.db.commit()
            
            # Send notification
            order_id_value = db_order.__dict__.get('id', db_order.id)
            await NotificationService.send_order_notification(
                user_id, int(order_id_value), "cancelled"
            )
            
            return {
                "success": True,
                "message": "Order cancelled successfully",
                "refund_initiated": refund_initiated
            }
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error cancelling order {order_id}: {str(e)}")
            raise
    
    async def update_order_items(self, order_id: int, user_id: str, items_update: OrderItemsUpdate) -> Optional[Order]:
        """Update items in an order if eligible"""
        try:
            db_order = await self.get_order_by_id(order_id, user_id)
            if not db_order:
                return None
            
            # Check if order can be modified
            order_status = getattr(db_order, 'status', db_order.status)
            if order_status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
                raise ValueError("Order cannot be modified at this stage")
            
            # Delete existing items
            await self.db.execute(
                OrderItem.__table__.delete().where(OrderItem.order_id == order_id)
            )
            
            # Add new items
            total_amount = 0.0
            for item in items_update.items:
                # Check product availability
                if not await ProductService.check_product_availability(item.product_id, item.quantity):
                    raise ValueError(f"Insufficient stock for product {item.product_id}")
                
                # Get product price
                price = await ProductService.get_product_price(item.product_id)
                if price is None:
                    raise ValueError(f"Product {item.product_id} not found")
                
                item_total = price * item.quantity
                total_amount += item_total
                
                db_item = OrderItem(
                    order_id=order_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=price
                )
                self.db.add(db_item)
            
            # Update total amount (including delivery fee)
            delivery_fee_value = db_order.__dict__.get('delivery_fee', db_order.delivery_fee)
            setattr(db_order, 'total_amount', total_amount + float(str(delivery_fee_value)))
            
            await self.db.commit()
            await self.db.refresh(db_order)
            
            return db_order
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating order items for order {order_id}: {str(e)}")
            raise
    
    async def create_order_template(self, user_id: str, template_data: OrderTemplateCreate) -> OrderTemplate:
        """Create a new order template"""
        try:
            import json
            items_json = json.dumps([item.dict() for item in template_data.items])
            db_template = OrderTemplate(
                user_id=user_id,
                name=template_data.name,
                items=items_json
            )
            
            self.db.add(db_template)
            await self.db.commit()
            await self.db.refresh(db_template)
            
            return db_template
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating order template: {str(e)}")
            raise
    
    async def get_user_templates(self, user_id: str) -> List[OrderTemplate]:
        """Get all order templates for a user"""
        try:
            result = await self.db.execute(
                select(OrderTemplate)
                .where(OrderTemplate.user_id == user_id)
                .order_by(OrderTemplate.created_at.desc())
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error fetching user templates: {str(e)}")
            raise
    
    async def create_order_from_template(self, user_id: str, template_id: int, order_data: OrderCreate) -> Order:
        """Create a new order from a template"""
        try:
            # Get template
            result = await self.db.execute(
                select(OrderTemplate)
                .where(and_(OrderTemplate.id == template_id, OrderTemplate.user_id == user_id))
            )
            db_template = result.scalars().first()
            if not db_template:
                raise ValueError("Template not found")
            
            # Parse template items
            import json
            template_items = json.loads(db_template.__dict__.get('items', db_template.items))
            
            # Validate products and calculate total
            total_amount = 0.0
            order_items = []
            
            for item in template_items:
                product_id = item["product_id"]
                quantity = item["quantity"]
                
                # Check product availability
                if not await ProductService.check_product_availability(product_id, quantity):
                    raise ValueError(f"Insufficient stock for product {product_id}")
                
                # Get product price
                price = await ProductService.get_product_price(product_id)
                if price is None:
                    raise ValueError(f"Product {product_id} not found")
                
                item_total = price * quantity
                total_amount += item_total
                
                order_items.append({
                    "product_id": product_id,
                    "quantity": quantity,
                    "price": price
                })
            
            # Calculate delivery fee (simplified)
            delivery_fee = 5.0
            total_amount += delivery_fee
            
            # Create order
            db_order = Order(
                user_id=user_id,
                delivery_address=order_data.delivery_address,
                delivery_latitude=order_data.delivery_latitude,
                delivery_longitude=order_data.delivery_longitude,
                total_amount=total_amount,
                delivery_fee=delivery_fee,
                scheduled_for=order_data.scheduled_for,
                status=OrderStatus.CONFIRMED if order_data.scheduled_for else OrderStatus.PENDING
            )
            
            self.db.add(db_order)
            await self.db.flush()
            
            # Create order items
            for item in order_items:
                db_item = OrderItem(
                    order_id=db_order.id,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    price=item["price"]
                )
                self.db.add(db_item)
            
            await self.db.commit()
            await self.db.refresh(db_order)
            
            return db_order
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating order from template: {str(e)}")
            raise
    
    async def submit_order_feedback(self, order_id: int, user_id: str, feedback_data: OrderFeedbackCreate) -> OrderFeedback:
        """Submit feedback for an order"""
        try:
            db_order = await self.get_order_by_id(order_id, user_id)
            if not db_order:
                raise ValueError("Order not found")
            
            # Check if order is delivered
            order_status = db_order.__dict__.get('status', db_order.status)
            if str(order_status) != OrderStatus.DELIVERED.value:
                raise ValueError("Feedback can only be submitted for delivered orders")
            
            # Check if feedback already exists
            result = await self.db.execute(
                select(OrderFeedback).where(OrderFeedback.order_id == order_id)
            )
            existing_feedback = result.scalars().first()
            
            if existing_feedback:
                # Update existing feedback
                setattr(existing_feedback, 'rating', feedback_data.rating)
                setattr(existing_feedback, 'comment', feedback_data.comment)
                db_feedback = existing_feedback
            else:
                # Create new feedback
                db_feedback = OrderFeedback(
                    order_id=order_id,
                    rating=feedback_data.rating,
                    comment=feedback_data.comment
                )
                self.db.add(db_feedback)
            
            await self.db.commit()
            await self.db.refresh(db_feedback)
            
            return db_feedback
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error submitting feedback for order {order_id}: {str(e)}")
            raise
    
    async def get_admin_orders(self, user_id: Optional[str] = None, status: Optional[str] = None, 
                              limit: int = 20, offset: int = 0) -> List[Order]:
        """Get all orders for admin with optional filtering"""
        try:
            query = select(Order).order_by(Order.created_at.desc())
            
            if user_id:
                query = query.where(Order.user_id == user_id)
            
            if status:
                query = query.where(Order.status == status)
            
            query = query.limit(limit).offset(offset)
            
            result = await self.db.execute(query)
            orders = list(result.scalars().all())
            
            # Load order items for each order manually
            for order in orders:
                items_result = await self.db.execute(
                    select(OrderItem).where(OrderItem.order_id == order.id)
                )
                order.items = items_result.scalars().all()
                
                # Load product details for each item
                for item in order.items:
                    try:
                        product = await ProductService.get_product(item.product_id)
                        setattr(item, 'product', product)
                    except Exception:
                        # If product is not found, skip it
                        pass
            
            return orders
        except Exception as e:
            logger.error(f"Error fetching admin orders: {str(e)}")
            raise
    
    async def bulk_update_order_status(self, bulk_update: BulkStatusUpdate) -> Dict[str, Any]:
        """Bulk update order statuses"""
        try:
            updated_count = 0
            for order_id in bulk_update.order_ids:
                stmt = (
                    Order.__table__.update()
                    .where(Order.id == order_id)
                    .values(status=bulk_update.status.value)
                )
                result = await self.db.execute(stmt)
                if result:
                    updated_count += 1
            
            await self.db.commit()
            
            return {
                "success": True,
                "updated_count": updated_count,
                "total_count": len(bulk_update.order_ids)
            }
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error in bulk update order status: {str(e)}")
            raise
    
    async def bulk_assign_delivery_partner(self, bulk_assign: BulkAssignDelivery) -> Dict[str, Any]:
        """Bulk assign delivery partner to orders"""
        try:
            updated_count = 0
            for order_id in bulk_assign.order_ids:
                stmt = (
                    Order.__table__.update()
                    .where(Order.id == order_id)
                    .values(
                        delivery_partner_id=bulk_assign.delivery_partner_id,
                        status=OrderStatus.CONFIRMED.value
                    )
                )
                result = await self.db.execute(stmt)
                if result:
                    updated_count += 1
            
            await self.db.commit()
            
            return {
                "success": True,
                "updated_count": updated_count,
                "total_count": len(bulk_assign.order_ids)
            }
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error in bulk assign delivery partner: {str(e)}")
            raise
    
    async def get_revenue_analytics(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get revenue analytics for a date range"""
        try:
            result = await self.db.execute(
                select(
                    func.date_trunc('day', Order.created_at).label('date'),
                    func.count(Order.id).label('order_count'),
                    func.sum(Order.total_amount).label('total_revenue')
                )
                .where(and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date,
                    Order.status != OrderStatus.CANCELLED.value
                ))
                .group_by(func.date_trunc('day', Order.created_at))
                .order_by(func.date_trunc('day', Order.created_at))
            )
            
            return [
                {
                    "date": row.date,
                    "order_count": row.order_count,
                    "total_revenue": float(row.total_revenue or 0)
                }
                for row in result.fetchall()
            ]
        except Exception as e:
            logger.error(f"Error fetching revenue analytics: {str(e)}")
            raise
    
    async def get_cancellation_rate(self, period_days: int = 30) -> Dict[str, Any]:
        """Get order cancellation rate for a period"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Total orders in period
            total_result = await self.db.execute(
                select(func.count(Order.id))
                .where(and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date
                ))
            )
            total_orders = total_result.scalar() or 0
            
            # Cancelled orders in period
            cancelled_result = await self.db.execute(
                select(func.count(Order.id))
                .where(and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date,
                    Order.status == OrderStatus.CANCELLED.value
                ))
            )
            cancelled_orders = cancelled_result.scalar() or 0
            
            cancellation_rate = (cancelled_orders / total_orders * 100) if total_orders > 0 else 0
            
            return {
                "period": f"Last {period_days} days",
                "cancellation_rate": round(cancellation_rate, 2),
                "total_orders": total_orders,
                "cancelled_orders": cancelled_orders
            }
        except Exception as e:
            logger.error(f"Error fetching cancellation rate: {str(e)}")
            raise
    
    async def get_top_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top customers by order count and spending"""
        try:
            result = await self.db.execute(
                select(
                    Order.user_id,
                    func.count(Order.id).label('order_count'),
                    func.sum(Order.total_amount).label('total_spent')
                )
                .where(Order.status != OrderStatus.CANCELLED.value)
                .group_by(Order.user_id)
                .order_by(func.sum(Order.total_amount).desc())
                .limit(limit)
            )
            
            return [
                {
                    "user_id": row.user_id,
                    "order_count": row.order_count,
                    "total_spent": float(row.total_spent or 0)
                }
                for row in result.fetchall()
            ]
        except Exception as e:
            logger.error(f"Error fetching top customers: {str(e)}")
            raise