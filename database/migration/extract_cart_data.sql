-- Extract Cart Service Data from Monolithic Database
-- This script extracts cart and wishlist data for migration to cart_db

-- Extract carts table data with reference IDs
\copy (
    SELECT 
        id,
        user_id as user_id_ref,
        NULL as session_id,
        'active' as status,
        COALESCE((
            SELECT COUNT(*) 
            FROM cart_items ci 
            WHERE ci.cart_id = c.id
        ), 0) as total_items,
        COALESCE((
            SELECT SUM(ci.quantity * p.price) 
            FROM cart_items ci 
            JOIN products p ON ci.product_id = p.id 
            WHERE ci.cart_id = c.id
        ), 0) as total_amount,
        'INR' as currency,
        NULL as expires_at,
        created_at,
        updated_at
    FROM carts c
    ORDER BY id
) TO 'migration_data/carts.csv' WITH CSV HEADER;

-- Extract cart_items table data with snapshots
\copy (
    SELECT 
        ci.id,
        ci.cart_id,
        ci.product_id as product_id_ref,
        NULL as product_variant_id_ref,
        ci.quantity,
        p.price as unit_price,
        (ci.quantity * p.price) as total_price,
        p.name as product_name_snapshot,
        p.image_url as product_image_snapshot,
        NULL as product_sku_snapshot,
        ci.created_at as last_validated_at,
        'valid' as validation_status,
        ci.created_at,
        ci.updated_at
    FROM cart_items ci
    JOIN products p ON ci.product_id = p.id
    ORDER BY ci.id
) TO 'migration_data/cart_items.csv' WITH CSV HEADER;

-- Extract wishlists table data
\copy (
    SELECT 
        id,
        user_id as user_id_ref,
        'My Wishlist' as name,
        NULL as description,
        false as is_public,
        COALESCE((
            SELECT COUNT(*) 
            FROM wishlist_items wi 
            WHERE wi.wishlist_id = w.id
        ), 0) as total_items,
        created_at,
        updated_at
    FROM wishlists w
    ORDER BY id
) TO 'migration_data/wishlists.csv' WITH CSV HEADER;

-- Extract wishlist_items table data with snapshots
\copy (
    SELECT 
        wi.id,
        wi.wishlist_id,
        wi.product_id as product_id_ref,
        NULL as product_variant_id_ref,
        p.name as product_name_snapshot,
        p.price as product_price_snapshot,
        p.image_url as product_image_snapshot,
        wi.created_at as last_validated_at,
        'valid' as validation_status,
        NULL as notes,
        0 as priority,
        wi.created_at,
        wi.updated_at
    FROM wishlist_items wi
    JOIN products p ON wi.product_id = p.id
    ORDER BY wi.id
) TO 'migration_data/wishlist_items.csv' WITH CSV HEADER;