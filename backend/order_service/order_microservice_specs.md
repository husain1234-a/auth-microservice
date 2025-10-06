# Order Microservice Specification

## Overview
This document outlines the requirements and API endpoints for a standalone Order microservice that will be extracted from the current monolithic application. The microservice will handle all order-related functionality including order creation, management, and status tracking.

## Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Serialization**: Pydantic
- **Authentication**: JWT-based via Gateway
- **Messaging**: Redis for async task queuing
- **Deployment**: Docker containerized

## Database Schema

### Orders Table
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id varchar(255) NOT NULL,
    delivery_partner_id varchar(255),
    total_amount DECIMAL(10, 2) CHECK (total_amount > 0) NOT NULL,
    delivery_fee DECIMAL(10, 2) CHECK (delivery_fee >= 0) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    delivery_address TEXT NOT NULL,
    delivery_latitude VARCHAR(20),
    delivery_longitude VARCHAR(20),
    estimated_delivery_time TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    scheduled_for TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (uid) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_order_user_status ON orders(user_id, status);
CREATE INDEX idx_order_delivery_partner ON orders(delivery_partner_id);
CREATE INDEX idx_order_created_at ON orders(created_at);
```

### Order Items Table
```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL,
    quantity INTEGER CHECK (quantity > 0) NOT NULL,
    price DECIMAL(10, 2) CHECK (price > 0) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
```

### Order Templates Table
```sql
CREATE TABLE order_templates (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    items JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT order_templates_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (uid) ON DELETE CASCADE
);
```

### Order Feedback Table
```sql
CREATE TABLE order_feedback (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_order_feedback_order_id ON order_feedback(order_id);
```

## API Endpoints

### Create Order
- **Endpoint**: `POST /orders`
- **Description**: Create a new order from the user's cart
- **Authentication**: Required - JWT token
- **Request Body**:
  ```json
  {
    "delivery_address": "123 Main St, City, State 12345",
    "delivery_latitude": "40.7128",
    "delivery_longitude": "-74.0060"
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "user_id": 123,
    "total_amount": 25.97,
    "delivery_fee": 5.00,
    "status": "confirmed",
    "delivery_address": "123 Main St, City, State 12345",
    "delivery_latitude": "40.7128",
    "delivery_longitude": "-74.0060",
    "estimated_delivery_time": "2023-01-01T13:30:00Z",
    "delivered_at": null,
    "cancelled_at": null,
    "scheduled_for": null,
    "created_at": "2023-01-01T13:00:00Z",
    "items": [
      {
        "id": 1,
        "product_id": 5,
        "quantity": 2,
        "price": 2.99,
        "product": {
          "id": 5,
          "name": "Apple",
          "description": "Fresh red apples",
          "price": 2.99,
          "mrp": 3.99,
          "category_id": 1,
          "image_url": "https://example.com/apple.jpg",
          "stock_quantity": 100,
          "unit": "kg",
          "is_active": true,
          "created_at": "2023-01-01T00:00:00Z"
        }
      }
    ]
  }
  ```

### Get User's Orders
- **Endpoint**: `GET /orders/my-orders`
- **Description**: Retrieve the current user's order history
- **Authentication**: Required - JWT token
- **Query Parameters**:
  - `limit` (optional, default=20, max=50): Maximum number of orders to return
  - `offset` (optional, default=0): Number of orders to skip
- **Response**:
  ```json
  [
    {
      "id": 1,
      "user_id": 123,
      "total_amount": 25.97,
      "delivery_fee": 5.00,
      "status": "delivered",
      "delivery_address": "123 Main St, City, State 12345",
      "delivery_latitude": "40.7128",
      "delivery_longitude": "-74.0060",
      "estimated_delivery_time": "2023-01-01T13:30:00Z",
      "delivered_at": "2023-01-01T13:25:00Z",
      "cancelled_at": null,
      "scheduled_for": null,
      "created_at": "2023-01-01T13:00:00Z",
      "items": [
        {
          "id": 1,
          "product_id": 5,
          "quantity": 2,
          "price": 2.99,
          "product": {
            "id": 5,
            "name": "Apple",
            "description": "Fresh red apples",
            "price": 2.99,
            "mrp": 3.99,
            "category_id": 1,
            "image_url": "https://example.com/apple.jpg",
            "stock_quantity": 100,
            "unit": "kg",
            "is_active": true,
            "created_at": "2023-01-01T00:00:00Z"
          }
        }
      ]
    }
  ]
  ```

### Get Order by ID
- **Endpoint**: `GET /orders/{order_id}`
- **Description**: Retrieve a specific order by its ID
- **Authentication**: Required - JWT token
- **Response**:
  ```json
  {
    "id": 1,
    "user_id": 123,
    "total_amount": 25.97,
    "delivery_fee": 5.00,
    "status": "delivered",
    "delivery_address": "123 Main St, City, State 12345",
    "delivery_latitude": "40.7128",
    "delivery_longitude": "-74.0060",
    "estimated_delivery_time": "2023-01-01T13:30:00Z",
    "delivered_at": "2023-01-01T13:25:00Z",
    "cancelled_at": null,
    "scheduled_for": null,
    "created_at": "2023-01-01T13:00:00Z",
    "items": [
      {
        "id": 1,
        "product_id": 5,
        "quantity": 2,
        "price": 2.99,
        "product": {
          "id": 5,
          "name": "Apple",
          "description": "Fresh red apples",
          "price": 2.99,
          "mrp": 3.99,
          "category_id": 1,
          "image_url": "https://example.com/apple.jpg",
          "stock_quantity": 100,
          "unit": "kg",
          "is_active": true,
          "created_at": "2023-01-01T00:00:00Z"
        }
      }
    ]
  }
  ```

### Update Order Status (Admin/Delivery Partner)
- **Endpoint**: `PUT /orders/{order_id}/status`
- **Description**: Update the status of an order
- **Authentication**: Required - JWT token with admin/delivery partner role
- **Request Body**:
  ```json
  {
    "status": "out_for_delivery"
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "user_id": 123,
    "total_amount": 25.97,
    "delivery_fee": 5.00,
    "status": "out_for_delivery",
    "delivery_address": "123 Main St, City, State 12345",
    "delivery_latitude": "40.7128",
    "delivery_longitude": "-74.0060",
    "estimated_delivery_time": "2023-01-01T13:30:00Z",
    "delivered_at": null,
    "cancelled_at": null,
    "scheduled_for": null,
    "created_at": "2023-01-01T13:00:00Z",
    "items": [
      {
        "id": 1,
        "product_id": 5,
        "quantity": 2,
        "price": 2.99,
        "product": {
          "id": 5,
          "name": "Apple",
          "description": "Fresh red apples",
          "price": 2.99,
          "mrp": 3.99,
          "category_id": 1,
          "image_url": "https://example.com/apple.jpg",
          "stock_quantity": 100,
          "unit": "kg",
          "is_active": true,
          "created_at": "2023-01-01T00:00:00Z"
        }
      }
    ]
  }
  ```

### Get All Orders (Admin Only)
- **Endpoint**: `GET /orders`
- **Description**: Retrieve all orders with optional filtering
- **Authentication**: Required - JWT token with admin role
- **Query Parameters**:
  - `user_id` (optional): Filter by user ID
  - `status` (optional): Filter by order status
  - `limit` (optional, default=20, max=50): Maximum number of orders to return
  - `offset` (optional, default=0): Number of orders to skip
- **Response**:
  ```json
  [
    {
      "id": 1,
      "user_id": 123,
      "total_amount": 25.97,
      "delivery_fee": 5.00,
      "status": "out_for_delivery",
      "delivery_address": "123 Main St, City, State 12345",
      "delivery_latitude": "40.7128",
      "delivery_longitude": "-74.0060",
      "estimated_delivery_time": "2023-01-01T13:30:00Z",
      "delivered_at": null,
      "cancelled_at": null,
      "scheduled_for": null,
      "created_at": "2023-01-01T13:00:00Z",
      "items": [
        {
          "id": 1,
          "product_id": 5,
          "quantity": 2,
          "price": 2.99,
          "product": {
            "id": 5,
            "name": "Apple",
            "description": "Fresh red apples",
            "price": 2.99,
            "mrp": 3.99,
            "category_id": 1,
            "image_url": "https://example.com/apple.jpg",
            "stock_quantity": 100,
            "unit": "kg",
            "is_active": true,
            "created_at": "2023-01-01T00:00:00Z"
          }
        }
      ]
    }
  ]
  ```

### Assign Delivery Partner (Admin Only)
- **Endpoint**: `PUT /orders/{order_id}/assign-delivery`
- **Description**: Assign a delivery partner to an order
- **Authentication**: Required - JWT token with admin role
- **Request Body**:
  ```json
  {
    "delivery_partner_id": 456
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "user_id": 123,
    "total_amount": 25.97,
    "delivery_fee": 5.00,
    "status": "confirmed",
    "delivery_address": "123 Main St, City, State 12345",
    "delivery_latitude": "40.7128",
    "delivery_longitude": "-74.0060",
    "estimated_delivery_time": "2023-01-01T13:30:00Z",
    "delivered_at": null,
    "cancelled_at": null,
    "scheduled_for": null,
    "created_at": "2023-01-01T13:00:00Z",
    "items": [
      {
        "id": 1,
        "product_id": 5,
        "quantity": 2,
        "price": 2.99,
        "product": {
          "id": 5,
          "name": "Apple",
          "description": "Fresh red apples",
          "price": 2.99,
          "mrp": 3.99,
          "category_id": 1,
          "image_url": "https://example.com/apple.jpg",
          "stock_quantity": 100,
          "unit": "kg",
          "is_active": true,
          "created_at": "2023-01-01T00:00:00Z"
        }
      }
    ]
  }
  ```

### Cancel Order
- **Endpoint**: `POST /orders/{order_id}/cancel`
- **Description**: Cancel an order if eligible
- **Authentication**: Required - JWT token
- **Response**:
  ```json
  {
    "success": true,
    "message": "Order cancelled successfully",
    "refund_initiated": true
  }
  ```

### Modify Order Items
- **Endpoint**: `PUT /orders/{order_id}/items`
- **Description**: Update items in an order if eligible
- **Authentication**: Required - JWT token
- **Request Body**:
  ```json
  {
    "items": [
      {"product_id": 5, "quantity": 3},
      {"product_id": 8, "quantity": 1}
    ]
  }
  ```

### Real-Time Order Tracking
- **Endpoint**: `GET /orders/{order_id}/tracking-stream`
- **Description**: Get real-time tracking stream for an order
- **Authentication**: Required - JWT token

### Get Delivery Location
- **Endpoint**: `GET /orders/{order_id}/delivery-location`
- **Description**: Get current delivery location for an order
- **Authentication**: Required - JWT token
- **Response**:
  ```json
  {
    "order_id": 1,
    "latitude": "40.7128",
    "longitude": "-74.0060",
    "last_updated": "2023-01-01T13:25:00Z"
  }
  ```

### Bulk Order Operations
- **Endpoint**: `PUT /orders/bulk-status-update`
- **Description**: Bulk update order statuses
- **Authentication**: Required - JWT token with admin role
- **Request Body**:
  ```json
  {
    "order_ids": [1, 2, 3],
    "status": "out_for_delivery"
  }
  ```

- **Endpoint**: `POST /orders/bulk-assign-delivery`
- **Description**: Bulk assign delivery partner to orders
- **Authentication**: Required - JWT token with admin role
- **Request Body**:
  ```json
  {
    "order_ids": [1, 2, 3],
    "delivery_partner_id": 456
  }
  ```

### Export Orders
- **Endpoint**: `GET /orders/export`
- **Description**: Export orders in specified format
- **Authentication**: Required - JWT token with admin role
- **Query Parameters**:
  - `format` (optional, default=json): Export format (json or csv)
  - `status` (optional): Filter by order status

### Create Scheduled Order
- **Endpoint**: `POST /orders/scheduled`
- **Description**: Create a scheduled order for future delivery
- **Authentication**: Required - JWT token
- **Request Body**:
  ```json
  {
    "delivery_address": "123 Main St, City, State 12345",
    "delivery_latitude": "40.7128",
    "delivery_longitude": "-74.0060",
    "scheduled_for": "2023-01-02T08:00:00Z"
  }
  ```

### Request Order Return
- **Endpoint**: `POST /orders/{order_id}/request-return`
- **Description**: Request return for a delivered order
- **Authentication**: Required - JWT token

### Create Order Template
- **Endpoint**: `POST /templates`
- **Description**: Create a new order template
- **Authentication**: Required - JWT token
- **Request Body**:
  ```json
  {
    "name": "Weekly Grocery Pack",
    "items": [
      {"product_id": 5, "quantity": 2},
      {"product_id": 8, "quantity": 1}
    ]
  }
  ```

### Get Order Templates
- **Endpoint**: `GET /templates`
- **Description**: Get all order templates for the current user
- **Authentication**: Required - JWT token

### Get Order Template
- **Endpoint**: `GET /templates/{id}`
- **Description**: Get a specific order template by ID
- **Authentication**: Required - JWT token

### Delete Order Template
- **Endpoint**: `DELETE /templates/{id}`
- **Description**: Delete an order template
- **Authentication**: Required - JWT token

### Create Order from Template
- **Endpoint**: `POST /templates/{id}/order`
- **Description**: Create a new order from a template
- **Authentication**: Required - JWT token
- **Request Body**:
  ```json
  {
    "delivery_address": "123 Main St, City, State 12345",
    "delivery_latitude": "40.7128",
    "delivery_longitude": "-74.0060"
  }
  ```

### Submit Order Feedback
- **Endpoint**: `POST /orders/{order_id}/feedback`
- **Description**: Submit feedback for an order
- **Authentication**: Required - JWT token
- **Request Body**:
  ```json
  {
    "rating": 5,
    "comment": "Fast delivery!"
  }
  ```

### Get Revenue Analytics
- **Endpoint**: `GET /analytics/revenue`
- **Description**: Get revenue analytics for a date range
- **Authentication**: Required - JWT token with admin role
- **Query Parameters**:
  - `start_date` (required): Start date for analytics
  - `end_date` (required): End date for analytics

### Get Delivery Performance
- **Endpoint**: `GET /analytics/delivery-performance`
- **Description**: Get delivery performance metrics
- **Authentication**: Required - JWT token with admin role

### Get Top Customers
- **Endpoint**: `GET /analytics/top-customers`
- **Description**: Get top customers by order count and spending
- **Authentication**: Required - JWT token with admin role
- **Query Parameters**:
  - `limit` (optional, default=10): Maximum number of customers to return

### Get Cancellation Rate
- **Endpoint**: `GET /analytics/cancellation-rate`
- **Description**: Get order cancellation rate for a period
- **Authentication**: Required - JWT token with admin role
- **Query Parameters**:
  - `period_days` (optional, default=30): Number of days to analyze

## Data Models

### Order Models

#### OrderStatus Enum
```python
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURN_REQUESTED = "return_requested"
    RETURN_APPROVED = "return_approved"
    PICKED_UP = "picked_up"
    REFUNDED = "refunded"
```

#### OrderItemResponse
```python
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: Optional[ProductResponse] = None
    
    class Config:
        from_attributes = True
```

#### OrderCreate
```python
class OrderCreate(BaseModel):
    delivery_address: str
    delivery_latitude: Optional[str] = None
    delivery_longitude: Optional[str] = None
    scheduled_for: Optional[datetime] = None
```

#### OrderResponse
```python
class OrderResponse(BaseModel):
    id: int
    user_id: str
    total_amount: float
    delivery_fee: float
    status: OrderStatus
    delivery_address: str
    delivery_latitude: Optional[str] = None
    delivery_longitude: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    created_at: datetime
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True
```

#### OrderStatusUpdate
```python
class OrderStatusUpdate(BaseModel):
    status: OrderStatus
```

#### AssignDeliveryPartnerRequest
```python
class AssignDeliveryPartnerRequest(BaseModel):
    delivery_partner_id: str
```

## Authentication & Authorization

### JWT Token Structure
The microservice will use JWT tokens for authentication, validated through the API Gateway. The token will contain the following claims:
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "admin",  // or "user" or "delivery_partner"
  "exp": 1234567890,
  "iat": 1234567890
}
```

### Implementation Details
1. **Token Validation**: All endpoints will validate the JWT token using a middleware that communicates with the Auth Service
2. **User Identification**: Extract user ID from the token for order operations
3. **Role-Based Access Control**: Different roles have different permissions:
   - **User**: Can create orders, view their own orders, cancel eligible orders, submit feedback
   - **Delivery Partner**: Can update order status for assigned orders
   - **Admin**: Full access to all order operations
4. **Error Handling**: Unauthorized requests will return a 401 Unauthorized status

### Security Middleware
```python
from fastapi import HTTPException, status
from jose import JWTError, jwt

async def get_current_user(token: str = Header(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role", "user")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return {"user_id": int(user_id), "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

## Required Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/order_db

# JWT
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256

# App
APP_NAME=Order Service
DEBUG=True
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# External Services
USER_SERVICE_URL=http://auth-service:8001
PRODUCT_SERVICE_URL=http://product-service:8002
CART_SERVICE_URL=http://cart-service:8003
PAYMENT_SERVICE_URL=http://payment-service:8005
NOTIFICATION_SERVICE_URL=http://notification-service:8006

# Redis for async tasks
REDIS_URL=redis://localhost:6379/0
```

## Dependencies (requirements.txt)

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
pydantic==2.5.0
pydantic-settings==2.0.3
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
aiohttp==3.9.1
alembic==1.12.1
redis==5.0.1
hiredis==2.2.3
celery==5.3.4
httpx==0.25.0
```

## Project Structure

```
order-service/
├── app/
│   ├── routes/
│   │   ├── orders.py
│   │   ├── templates.py
│   │   ├── feedback.py
│   │   ├── analytics.py
│   │   └── api.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── order.py
│   │   └── base.py
│   ├── schemas/
│   │   └── order.py
│   ├── services/
│   │   ├── order_service.py
│   │   ├── cart_service.py
│   │   ├── product_service.py
│   │   ├── notification_service.py
│   │   └── payment_service.py
│   ├── tasks/
│   │   └── notification_tasks.py
│   └── main.py
├── tests/
│   └── test_order_service.py
├── requirements.txt
├── Dockerfile
├── .env
└── README.md
```

## Integration with Other Services

### Cart Service Integration
The order service needs to communicate with the cart service to:
1. Retrieve cart items for order creation
2. Clear cart after successful order creation

Implementation example:
```python
import httpx
from fastapi import HTTPException

class CartService:
    @staticmethod
    async def get_cart_items(user_id: str):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{settings.CART_SERVICE_URL}/api/v1/cart/{user_id}")
                if response.status_code == 200:
                    return response.json().get("items", [])
                elif response.status_code == 404:
                    return []
                else:
                    raise HTTPException(status_code=response.status_code, detail="Failed to retrieve cart")
            except httpx.RequestError:
                raise HTTPException(status_code=503, detail="Cart service unavailable")
    
    @staticmethod
    async def clear_cart(user_id: str):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(f"{settings.CART_SERVICE_URL}/api/v1/cart/{user_id}/clear")
                return response.status_code == 200
            except httpx.RequestError:
                return False
```

### Product Service Integration
The order service needs to communicate with the product service to:
1. Validate product existence
2. Retrieve product details for order items
3. Check product availability

Implementation example:
```python
import httpx
from fastapi import HTTPException

class ProductService:
    @staticmethod
    async def get_product(product_id: int):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{settings.PRODUCT_SERVICE_URL}/api/products/{product_id}")
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
            except httpx.RequestError:
                raise HTTPException(status_code=503, detail="Product service unavailable")
    
    @staticmethod
    async def check_product_availability(product_id: int, quantity: int):
        product = await ProductService.get_product(product_id)
        if not product:
            return False
        return product.get("stock_quantity", 0) >= quantity
    
    @staticmethod
    async def get_product_price(product_id: int):
        product = await ProductService.get_product(product_id)
        if not product:
            return None
        return product.get("price")
```

### Notification Service Integration
The order service needs to communicate with the notification service to:
1. Send order confirmation notifications
2. Send order status update notifications

Implementation example:
```python
import httpx
from fastapi import HTTPException

class NotificationService:
    @staticmethod
    async def send_order_notification(user_id: str, order_id: int, status: str):
        async with httpx.AsyncClient() as client:
            try:
                notification_data = {
                    "user_id": user_id,
                    "order_id": order_id,
                    "status": status
                }
                response = await client.post(
                    f"{settings.NOTIFICATION_SERVICE_URL}/notifications/order-status",
                    json=notification_data
                )
                return response.status_code == 200
            except httpx.RequestError:
                return False
```

### Payment Service Integration
The order service needs to communicate with the payment service to:
1. Process payments for orders
2. Initiate refunds for cancelled orders

Implementation example:
```python
import httpx
from fastapi import HTTPException

class PaymentService:
    @staticmethod
    async def process_payment(user_id: str, order_id: int, amount: float):
        async with httpx.AsyncClient() as client:
            try:
                payment_data = {
                    "user_id": user_id,
                    "order_id": order_id,
                    "amount": amount
                }
                response = await client.post(
                    f"{settings.PAYMENT_SERVICE_URL}/payments/process",
                    json=payment_data
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(status_code=response.status_code, detail="Payment processing failed")
            except httpx.RequestError:
                raise HTTPException(status_code=503, detail="Payment service unavailable")
    
    @staticmethod
    async def initiate_refund(user_id: str, order_id: int, amount: float):
        async with httpx.AsyncClient() as client:
            try:
                refund_data = {
                    "user_id": user_id,
                    "order_id": order_id,
                    "amount": amount
                }
                response = await client.post(
                    f"{settings.PAYMENT_SERVICE_URL}/payments/refund",
                    json=refund_data
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(status_code=response.status_code, detail="Refund initiation failed")
            except httpx.RequestError:
                raise HTTPException(status_code=503, detail="Payment service unavailable")
```

## Asynchronous Task Processing

### Notification Tasks
Order notifications are processed asynchronously using Redis and Celery:

```python
from celery import Celery
import redis

# Initialize Celery
celery_app = Celery("order_service", broker=settings.REDIS_URL)

@celery_app.task
def send_order_confirmation_email(email: str, order_id: int, total_amount: float):
    """Send order confirmation email asynchronously"""
    # Implementation for sending email
    pass

@celery_app.task
def send_order_notification(fcm_tokens: list, order_id: int, status: str):
    """Send push notification for order status update"""
    # Implementation for sending push notification
    pass
```

## Additional Considerations

### 1. Concurrency Handling
- Implement proper locking mechanisms to handle concurrent order creation
- Use database constraints to prevent race conditions

### 2. Error Handling
- Standardized error response format
- Proper HTTP status codes
- Detailed error messages for debugging
- Graceful degradation when dependent services are unavailable

### 3. Logging & Monitoring
- Structured logging for all operations
- Request tracing with unique IDs
- Performance metrics collection
- Error rate monitoring

### 4. Caching
- Implement Redis caching for frequently accessed orders
- Cache invalidation strategies

### 5. Rate Limiting
- Implement rate limiting to prevent abuse
- Different limits for different types of requests

### 6. Health Checks
- Basic health check endpoint
- Detailed health check with database connectivity verification
- Dependency health checks (Redis, other services)

## Implementation Status

The Order Microservice has been fully implemented with the following components:

1. ✅ Database schema with all required tables and relationships
2. ✅ Core configuration and security modules
3. ✅ Data models for all entities
4. ✅ Pydantic schemas for request/response validation
5. ✅ Service classes for inter-service communication
6. ✅ Main order service with all business logic
7. ✅ REST API endpoints for all features
8. ✅ Docker configuration for containerization
9. ✅ Environment configuration
10. ✅ Integration with API Gateway
11. ✅ Comprehensive documentation

The service is ready for deployment and integration with the existing microservice architecture.