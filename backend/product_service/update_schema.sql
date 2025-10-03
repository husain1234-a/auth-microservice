-- SQL queries to update the database structure to match the updated code
-- This script removes the foreign key constraint from the products table

-- Drop the foreign key constraint
ALTER TABLE products
DROP CONSTRAINT IF EXISTS products_category_id_fkey;

-- Verify the changes
\d products