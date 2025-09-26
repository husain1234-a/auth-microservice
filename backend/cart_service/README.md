# Cart Microservice

This microservice handles shopping cart and wishlist functionality for the e-commerce platform.

## Features

- User shopping cart management (add, remove, clear items)
- Wishlist management (add, remove, move to cart)
- Promo code application and validation
- Integration with Product and User services
- RESTful API with comprehensive documentation

## Technology Stack

- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async)
- **Authentication**: JWT tokens
- **Communication**: REST API with other microservices
- **Containerization**: Docker

## API Endpoints

### Cart Operations

- `GET /api/v1/cart` - Get user's cart
- `POST /api/v1/cart/add` - Add item to cart
- `POST /api/v1/cart/remove` - Remove item from cart
- `DELETE /api/v1/cart/clear` - Clear all items from cart
- `POST /api/v1/cart/promo/apply` - Apply promo code
- `DELETE /api/v1/cart/promo/remove` - Remove promo code

### Wishlist Operations

- `GET /api/v1/wishlist` - Get user's wishlist
- `POST /api/v1/wishlist/add` - Add item to wishlist
- `POST /api/v1/wishlist/remove` - Remove item from wishlist
- `POST /api/v1/wishlist/move-to-cart` - Move item from wishlist to cart
- `DELETE /api/v1/wishlist/clear` - Clear all items from wishlist

## Database Schema

The service uses the following tables:

1. `carts` - User shopping carts
2. `cart_items` - Items in shopping carts
3. `wishlists` - User wishlists
4. `wishlist_items` - Items in wishlists
5. `promo_codes` - Available promo codes
6. `cart_promo_codes` - Applied promo codes for carts

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.11 (for local development)

### Running with Docker

```bash
docker-compose up --build
```

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env` file

3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Environment Variables

- `DATABASE_URL` - PostgreSQL database connection string
- `JWT_SECRET_KEY` - Secret key for JWT token signing
- `PRODUCT_SERVICE_URL` - URL for the Product microservice
- `USER_SERVICE_URL` - URL for the User/Auth microservice

## Testing

Run tests with:
```bash
python -m pytest
```

## Documentation

API documentation is available at:
- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc
