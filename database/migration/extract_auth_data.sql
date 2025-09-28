-- Extract Auth Service Data from Monolithic Database
-- This script extracts user-related data for migration to auth_db

-- Extract users table data
\copy (
    SELECT 
        uid,
        email,
        phone_number,
        display_name,
        photo_url,
        role,
        is_active,
        created_at,
        updated_at
    FROM users 
    ORDER BY created_at
) TO 'migration_data/users.csv' WITH CSV HEADER;

-- Create user profiles data (extended from users table)
\copy (
    SELECT 
        uid as user_id,
        NULL as first_name,
        NULL as last_name,
        NULL as address_line1,
        NULL as address_line2,
        NULL as city,
        NULL as state,
        NULL as postal_code,
        NULL as country,
        '{}' as preferences,
        created_at,
        updated_at
    FROM users 
    ORDER BY created_at
) TO 'migration_data/user_profiles.csv' WITH CSV HEADER;

-- Note: user_sessions table doesn't exist in monolithic DB
-- Will be created fresh in the new auth service