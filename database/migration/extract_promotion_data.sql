-- Extract Promotion Service Data from Monolithic Database
-- This script extracts promo code data for migration to promotion_db

-- Extract promo_codes table data with enhanced fields
\copy (
    SELECT 
        id,
        code,
        code as name,
        'Migrated promo code' as description,
        discount_type,
        discount_value,
        minimum_order_value,
        NULL as maximum_discount_amount,
        max_uses,
        1 as max_uses_per_user,
        used_count,
        valid_from,
        valid_until,
        is_active,
        NULL as applicable_categories,
        NULL as applicable_products,
        NULL as applicable_user_roles,
        NULL as minimum_user_age_days,
        false as first_time_users_only,
        false as stackable,
        false as auto_apply,
        created_at,
        updated_at,
        'system' as created_by
    FROM promo_codes 
    ORDER BY id
) TO 'migration_data/promo_codes.csv' WITH CSV HEADER;

-- Extract promo usage data from cart_promo_codes
\copy (
    SELECT 
        cpc.id,
        cpc.promo_code_id,
        c.user_id as user_id_ref,
        cpc.cart_id as cart_id_ref,
        NULL as order_id_ref,
        COALESCE((
            SELECT pc.discount_value 
            FROM promo_codes pc 
            WHERE pc.id = cpc.promo_code_id
        ), 0) as discount_amount,
        COALESCE(c.total_amount, 0) as original_amount,
        COALESCE(c.total_amount, 0) - COALESCE((
            SELECT pc.discount_value 
            FROM promo_codes pc 
            WHERE pc.id = cpc.promo_code_id
        ), 0) as final_amount,
        '{}' as usage_context,
        cpc.applied_at,
        'applied' as status
    FROM cart_promo_codes cpc
    JOIN carts c ON cpc.cart_id = c.id
    ORDER BY cpc.id
) TO 'migration_data/promo_usage.csv' WITH CSV HEADER;