# Order Microservice

This microservice handles all order-related functionality including order creation, management, and status tracking.

## Features

- Create orders from user's cart
- Retrieve user's order history
- Get specific order details
- Update order status (admin/delivery partner)
- Assign delivery partners to orders
- Order cancellation
- Order modification
- Real-time order tracking
- Bulk order operations
- Order analytics and reporting
- Saved order templates
- Scheduled/future orders
- Return and refund management
- Dynamic delivery fee calculation
- Customer feedback and ratings

## Technology Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Serialization**: Pydantic
- **Authentication**: JWT-based via Gateway
- **Messaging**: Redis for async task queuing
- **Deployment**: Docker containerized

## API Endpoints

### Orders
- `POST /orders` - Create a new order
- `GET /orders/my-orders` - Get user's orders
- `GET /orders/{order_id}` - Get order by ID
- `PUT /orders/{order_id}/status` - Update order status
- `GET /orders` - Get all orders (admin only)
- `PUT /orders/{order_id}/assign-delivery` - Assign delivery partner
- `POST /orders/{order_id}/cancel` - Cancel order
- `PUT /orders/{order_id}/items` - Modify order items
- `GET /orders/{order_id}/tracking-stream` - Real-time tracking stream
- `GET /orders/{order_id}/delivery-location` - Get delivery location
- `PUT /orders/bulk-status-update` - Bulk status update
- `POST /orders/bulk-assign-delivery` - Bulk assign delivery
- `GET /orders/export` - Export orders
- `POST /orders/scheduled` - Create scheduled order
- `POST /orders/{order_id}/request-return` - Request return

### Templates
- `POST /templates` - Create template
- `GET /templates` - List all templates
- `GET /templates/{id}` - Get specific template
- `DELETE /templates/{id}` - Delete template
- `POST /templates/{id}/order` - Create order from template

### Analytics
- `GET /analytics/revenue` - Revenue analytics
- `GET /analytics/delivery-performance` - Delivery performance
- `GET /analytics/top-customers` - Top customers
- `GET /analytics/cancellation-rate` - Cancellation rate

### Feedback
- `POST /orders/{order_id}/feedback` - Submit feedback

## Environment Variables

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
PAYMENT_SERVICE_URL=http://payment-service:8004
NOTIFICATION_SERVICE_URL=http://notification-service:8005

# Redis for async tasks
REDIS_URL=redis://localhost:6379/0
```