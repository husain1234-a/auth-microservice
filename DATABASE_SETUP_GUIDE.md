# Database Setup Guide for Microservices

This guide provides instructions for setting up isolated databases for each microservice in the architecture.

## Database Structure

Each microservice has its own isolated database:

1. **auth_db** - Authentication service database
2. **product_db** - Product service database
3. **cart_db** - Cart service database
4. **promotion_db** - Promotion service database

All databases use the `poc_user` user with password `admin123`.

## Setup Instructions

### 1. Create Databases

Connect to PostgreSQL as a superuser and create the databases:

```sql
CREATE DATABASE auth_db;
CREATE DATABASE product_db;
CREATE DATABASE cart_db;
CREATE DATABASE promotion_db;
```

### 2. Create User and Set Permissions

Run the [setup_all_databases.sql](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/database/migrations/setup_all_databases.sql) script to create the `poc_user` and set permissions:

```bash
psql -U postgres -f database/migrations/setup_all_databases.sql
```

### 3. Create Tables in Each Database

#### Auth Service Database (auth_db)

Apply the [auth service schema](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/backend/auth_service/database_schema.sql):

```bash
psql -U poc_user -d auth_db -f backend/auth_service/database_schema.sql
```

#### Product Service Database (product_db)

Apply the [product service schema](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/backend/product_service/database_schema.sql):

```bash
psql -U poc_user -d product_db -f backend/product_service/database_schema.sql
```

#### Cart Service Database (cart_db)

Apply the [cart service schema](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/backend/cart_service/isolated_database_schema.sql):

```bash
psql -U poc_user -d cart_db -f backend/cart_service/isolated_database_schema.sql
```

#### Promotion Service Database (promotion_db)

Apply the [promotion service schema](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/backend/promotion_service/database_schema.sql):

```bash
psql -U poc_user -d promotion_db -f backend/promotion_service/database_schema.sql
```

## Database Schema Details

### Auth Service (auth_db)

- **users** table: Stores user information from Firebase authentication
  - `uid` (Primary Key): Firebase user ID
  - `email`: User email
  - `phone_number`: User phone number
  - `display_name`: User display name
  - `photo_url`: User profile photo URL
  - `role`: User role (customer, delivery_guy, owner, admin)
  - `is_active`: User account status
  - `created_at`, `updated_at`: Timestamps

### Product Service (product_db)

- **categories** table: Product categories
  - `id` (Primary Key): Category ID
  - `name`: Category name
  - `image_url`: Category image URL
  - `is_active`: Category status
  - `created_at`: Creation timestamp

- **products** table: Product information
  - `id` (Primary Key): Product ID
  - `name`: Product name
  - `description`: Product description
  - `price`: Product selling price
  - `mrp`: Product maximum retail price
  - `category_id`: Category ID (no foreign key)
  - `category_name`: Category name (denormalized)
  - `image_url`: Product image URL
  - `stock_quantity`: Available stock
  - `unit`: Product unit (kg, gm, piece, liter)
  - `is_active`: Product status
  - `created_at`, `updated_at`: Timestamps

### Cart Service (cart_db)

- **users** table: Denormalized user information (synced from auth service)
- **categories** table: Denormalized category information (synced from product service)
- **products** table: Denormalized product information (synced from product service)
- **carts** table: User shopping carts
  - `id` (Primary Key): Cart ID
  - `user_id`: User ID
  - `created_at`, `updated_at`: Timestamps

- **cart_items** table: Items in shopping carts
  - `id` (Primary Key): Cart item ID
  - `cart_id`: Cart ID
  - `product_id`: Product ID
  - `product_name`: Product name (denormalized)
  - `product_price`: Product price (denormalized)
  - `product_image_url`: Product image URL (denormalized)
  - `quantity`: Item quantity
  - `created_at`, `updated_at`: Timestamps

- **wishlists** table: User wishlists
  - `id` (Primary Key): Wishlist ID
  - `user_id`: User ID
  - `created_at`, `updated_at`: Timestamps

- **wishlist_items** table: Items in wishlists
  - `id` (Primary Key): Wishlist item ID
  - `wishlist_id`: Wishlist ID
  - `product_id`: Product ID
  - `product_name`: Product name (denormalized)
  - `product_price`: Product price (denormalized)
  - `product_image_url`: Product image URL (denormalized)
  - `created_at`, `updated_at`: Timestamps

- **promo_codes** table: Promotion codes
  - `id` (Primary Key): Promo code ID
  - `code`: Promo code
  - `discount_type`: Discount type (percentage or fixed_amount)
  - `discount_value`: Discount value
  - `minimum_order_value`: Minimum order value for promo
  - `max_uses`: Maximum uses allowed
  - `used_count`: Number of times used
  - `valid_from`, `valid_until`: Validity period
  - `is_active`: Promo code status
  - `created_at`, `updated_at`: Timestamps

- **cart_promo_codes** table: Association between carts and promo codes
  - `id` (Primary Key): Association ID
  - `cart_id`: Cart ID
  - `promo_code_id`: Promo code ID
  - `applied_at`: Application timestamp

### Promotion Service (promotion_db)

- **promo_codes** table: Promotion codes
  - `id` (Primary Key): Promo code ID
  - `code`: Promo code
  - `discount_type`: Discount type (percentage or fixed_amount)
  - `discount_value`: Discount value
  - `minimum_order_value`: Minimum order value for promo
  - `max_uses`: Maximum uses allowed
  - `used_count`: Number of times used
  - `valid_from`, `valid_until`: Validity period
  - `is_active`: Promo code status
  - `created_at`, `updated_at`: Timestamps

- **user_promo_usage** table: Track promo code usage by users
  - `id` (Primary Key): Usage record ID
  - `user_id`: User ID
  - `promo_code_id`: Promo code ID
  - `used_at`: Usage timestamp
  - `order_id`: Associated order ID

## Data Synchronization

Since each service has its own isolated database, data synchronization between services is handled through:

1. **Event-driven architecture**: Services publish events when data changes
2. **Service-to-service communication**: Services call each other's APIs to sync data
3. **Denormalized fields**: Critical data is stored locally in each service

## Migration from Existing Schema

If you're migrating from the previous schema with foreign key constraints:

1. Apply the [remove_foreign_keys.sql](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/database/migrations/remove_foreign_keys.sql) migration script
2. Create the isolated databases as described above
3. Migrate data to the new structure
4. Update service configurations to use isolated database connections

## Testing the Setup

To verify the database setup:

1. Connect to each database as `poc_user`
2. Verify all tables are created
3. Insert test data into each table
4. Verify permissions are correctly set

```bash
# Test auth_db
psql -U poc_user -d auth_db -c "SELECT * FROM users LIMIT 1;"

# Test product_db
psql -U poc_user -d product_db -c "SELECT * FROM products LIMIT 1;"

# Test cart_db
psql -U poc_user -d cart_db -c "SELECT * FROM carts LIMIT 1;"

# Test promotion_db
psql -U poc_user -d promotion_db -c "SELECT * FROM promo_codes LIMIT 1;"
```

## Troubleshooting

### Common Issues

1. **Permission denied**: Ensure `poc_user` has been created and granted proper permissions
2. **Table not found**: Verify the schema files have been applied to the correct databases
3. **Connection refused**: Check PostgreSQL is running and accessible

### Resetting Databases

If you need to reset the databases:

```sql
-- Connect as superuser
DROP DATABASE IF EXISTS auth_db;
DROP DATABASE IF EXISTS product_db;
DROP DATABASE IF EXISTS cart_db;
DROP DATABASE IF EXISTS promotion_db;

-- Recreate databases
CREATE DATABASE auth_db;
CREATE DATABASE product_db;
CREATE DATABASE cart_db;
CREATE DATABASE promotion_db;

-- Recreate user
DROP ROLE IF EXISTS poc_user;
CREATE ROLE poc_user LOGIN PASSWORD 'admin123';
```

Then reapply all the setup steps.