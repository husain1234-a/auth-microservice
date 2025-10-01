-- Complete Migration Script for Microservice Architecture
-- This script removes all foreign key constraints and adds denormalized fields

-- Product Service Migrations
-- Remove foreign key constraint but keep the column
ALTER TABLE products
DROP CONSTRAINT IF EXISTS products_category_id_fkey;

-- Update products table to remove NOT NULL constraint from category_id
ALTER TABLE products ALTER COLUMN category_id DROP NOT NULL;

-- Add category_name column for denormalization
ALTER TABLE products
ADD COLUMN IF NOT EXISTS category_name VARCHAR(100);

-- Populate category_name with existing data (if needed)
-- This would typically be done through the application layer in a real migration

-- Cart Service Migrations

-- Add denormalized columns to cart_items table
ALTER TABLE cart_items
ADD COLUMN IF NOT EXISTS product_name varchar(200);

ALTER TABLE cart_items
ADD COLUMN IF NOT EXISTS product_price double precision;

ALTER TABLE cart_items
ADD COLUMN IF NOT EXISTS product_image_url varchar(500);

-- Add denormalized columns to wishlist_items table
ALTER TABLE wishlist_items
ADD COLUMN IF NOT EXISTS product_name varchar(200);

ALTER TABLE wishlist_items
ADD COLUMN IF NOT EXISTS product_price double precision;

ALTER TABLE wishlist_items
ADD COLUMN IF NOT EXISTS product_image_url varchar(500);

-- Remove all foreign key constraints from cart service:

-- Remove foreign key constraint from carts table to users
ALTER TABLE carts DROP CONSTRAINT IF EXISTS carts_user_id_fkey;

-- Remove foreign key constraint from cart_items table to carts
ALTER TABLE cart_items
DROP CONSTRAINT IF EXISTS cart_items_cart_id_fkey;

-- Remove foreign key constraint from cart_items table to products
ALTER TABLE cart_items
DROP CONSTRAINT IF EXISTS cart_items_product_id_fkey;

-- Remove foreign key constraint from wishlists table to users
ALTER TABLE wishlists
DROP CONSTRAINT IF EXISTS wishlists_user_id_fkey;

-- Remove foreign key constraint from wishlist_items table to wishlists
ALTER TABLE wishlist_items
DROP CONSTRAINT IF EXISTS wishlist_items_wishlist_id_fkey;

-- Remove foreign key constraint from wishlist_items table to products
ALTER TABLE wishlist_items
DROP CONSTRAINT IF EXISTS wishlist_items_product_id_fkey;

-- Remove foreign key constraint from cart_promo_codes table to carts
ALTER TABLE cart_promo_codes
DROP CONSTRAINT IF EXISTS cart_promo_codes_cart_id_fkey;

-- Remove foreign key constraint from cart_promo_codes table to promo_codes
ALTER TABLE cart_promo_codes
DROP CONSTRAINT IF EXISTS cart_promo_codes_promo_code_id_fkey;

-- Grant necessary privileges
GRANT ALL PRIVILEGES ON TABLE carts TO poc_user;

GRANT ALL PRIVILEGES ON TABLE wishlists TO poc_user;

GRANT ALL PRIVILEGES ON TABLE cart_items TO poc_user;

GRANT ALL PRIVILEGES ON TABLE wishlist_items TO poc_user;

GRANT ALL PRIVILEGES ON TABLE promo_codes TO poc_user;

GRANT ALL PRIVILEGES ON TABLE cart_promo_codes TO poc_user;

GRANT ALL PRIVILEGES ON TABLE users TO poc_user;

GRANT ALL PRIVILEGES ON TABLE categories TO poc_user;

GRANT ALL PRIVILEGES ON TABLE products TO poc_user;

-- Grant usage on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO poc_user;

-- Verify the changes
SELECT 'Migration completed successfully' as status;