# Product Microservice

This microservice handles all product-related functionality including product management, categories, and inventory.

## Features
- Product and category management
- Image processing and storage with Cloudflare R2
- JWT-based authentication
- Role-based access control (admin/user)
- PostgreSQL database with SQLAlchemy ORM

## API Endpoints

### Categories
- `GET /api/categories` - Get all categories
- `GET /api/categories/{category_id}` - Get category by ID
- `POST /api/categories` - Create new category (Admin only)
- `PUT /api/categories/{category_id}` - Update category (Admin only)

### Products
- `GET /api/products` - Get all products
- `GET /api/products/{product_id}` - Get product by ID
- `POST /api/products` - Create new product (Admin only)
- `PUT /api/products/{product_id}` - Update product (Admin only)
- `DELETE /api/products/{product_id}` - Delete product (Admin only)

## Environment Variables
Check `.env.example` for required environment variables.

## Running the Service
```bash
docker-compose up --build
```