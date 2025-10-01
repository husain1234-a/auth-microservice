-- Migration script to remove foreign key constraints from cart service and add denormalized fields

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

-- Add denormalized category_name column to products table
ALTER TABLE products
ADD COLUMN IF NOT EXISTS category_name varchar(100);

-- Remove foreign key constraint from carts table
ALTER TABLE carts DROP CONSTRAINT IF EXISTS carts_user_id_fkey;

-- Remove foreign key constraint from cart_items table to carts
ALTER TABLE cart_items
DROP CONSTRAINT IF EXISTS cart_items_cart_id_fkey;

-- Remove foreign key constraint from cart_items table to products
ALTER TABLE cart_items
DROP CONSTRAINT IF EXISTS cart_items_product_id_fkey;

-- Remove foreign key constraint from wishlists table
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

-- Remove foreign key constraint from products table to categories
ALTER TABLE products
DROP CONSTRAINT IF EXISTS products_category_id_fkey;

-- Populate denormalized fields with existing data (if any)
-- This would typically be done through the application layer in a real migration
-- For now, we're just adding the columns to support the new architecture

-- Update products table to remove NOT NULL constraint from category_id
ALTER TABLE products ALTER COLUMN category_id DROP NOT NULL;

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