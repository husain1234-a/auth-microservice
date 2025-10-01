-- Migration script to remove foreign key constraints and add denormalized fields

-- Product Service Migrations
-- Remove foreign key constraint but keep the column
ALTER TABLE products
DROP CONSTRAINT IF EXISTS products_category_id_fkey;

ALTER TABLE products ALTER COLUMN category_id DROP NOT NULL;

-- Add category_name column for denormalization
ALTER TABLE products
ADD COLUMN IF NOT EXISTS category_name VARCHAR(100);

-- Populate category_name with existing data
UPDATE products
SET
    category_name = (
        SELECT name
        FROM categories
        WHERE
            categories.id = products.category_id
    )
WHERE
    category_id IS NOT NULL
    AND category_name IS NULL;

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

-- Remove all foreign key constraints:
ALTER TABLE carts DROP CONSTRAINT IF EXISTS carts_user_id_fkey;

ALTER TABLE cart_items
DROP CONSTRAINT IF EXISTS cart_items_cart_id_fkey;

ALTER TABLE cart_items
DROP CONSTRAINT IF EXISTS cart_items_product_id_fkey;

ALTER TABLE wishlists
DROP CONSTRAINT IF EXISTS wishlists_user_id_fkey;

ALTER TABLE wishlist_items
DROP CONSTRAINT IF EXISTS wishlist_items_wishlist_id_fkey;

ALTER TABLE wishlist_items
DROP CONSTRAINT IF EXISTS wishlist_items_product_id_fkey;

ALTER TABLE cart_promo_codes
DROP CONSTRAINT IF EXISTS cart_promo_codes_cart_id_fkey;

ALTER TABLE cart_promo_codes
DROP CONSTRAINT IF EXISTS cart_promo_codes_promo_code_id_fkey;