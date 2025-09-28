-- Extract Product Service Data from Monolithic Database
-- This script extracts product and category data for migration to product_db

-- Extract categories table data
\copy (
    SELECT 
        id,
        name,
        NULL as description,
        image_url,
        NULL as parent_category_id,
        is_active,
        0 as sort_order,
        created_at,
        created_at as updated_at
    FROM categories 
    ORDER BY id
) TO 'migration_data/categories.csv' WITH CSV HEADER;

-- Extract products table data
\copy (
    SELECT 
        id,
        name,
        description,
        price,
        mrp,
        category_id,
        image_url,
        stock_quantity,
        unit,
        NULL as sku,
        NULL as weight,
        NULL as dimensions,
        NULL as tags,
        is_active,
        false as is_featured,
        created_at,
        updated_at
    FROM products 
    ORDER BY id
) TO 'migration_data/products.csv' WITH CSV HEADER;

-- Create initial inventory records for existing products
\copy (
    SELECT 
        id as product_id,
        stock_quantity as quantity_change,
        stock_quantity as new_quantity,
        'initial_stock' as change_type,
        'migration' as reference_id,
        'Initial stock from migration' as notes,
        created_at,
        'system' as created_by
    FROM products 
    WHERE stock_quantity > 0
    ORDER BY id
) TO 'migration_data/product_inventory.csv' WITH CSV HEADER;