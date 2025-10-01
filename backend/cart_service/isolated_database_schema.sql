-- Cart Microservice Database Schema (Isolated)
-- This schema is designed for isolated cart service database with no foreign key constraints

-- Denormalized Users table (synced from auth service)
CREATE TABLE users (
    uid varchar(255) NOT NULL,
    email varchar(255),
    phone_number varchar(20),
    display_name varchar(255),
    photo_url text,
    role varchar(50) DEFAULT 'customer'::character varying,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (uid)
);

-- Denormalized Categories table (synced from product service)
CREATE TABLE categories (
    id integer NOT NULL,
    name varchar(100) NOT NULL,
    image_url varchar(500),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id)
);

-- Denormalized Products table (synced from product service)
CREATE TABLE products (
    id integer NOT NULL,
    name varchar(200) NOT NULL,
    description text,
    price double precision NOT NULL,
    mrp double precision,
    category_id integer, -- No foreign key constraint
    category_name varchar(100), -- Denormalized category name
    image_url varchar(500),
    stock_quantity integer,
    unit varchar(20),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT products_price_check CHECK (price > (0)::double precision),
    CONSTRAINT products_mrp_check CHECK (mrp > (0)::double precision),
    CONSTRAINT products_stock_quantity_check CHECK (stock_quantity >= 0)
);

-- Cart tables (managed by cart service)

-- Main cart table
CREATE TABLE carts (
    id SERIAL NOT NULL,
    user_id varchar(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id)
    -- No foreign key constraint to users table
);

-- Cart items table
CREATE TABLE cart_items (
    id SERIAL NOT NULL,
    cart_id integer NOT NULL,
    product_id integer NOT NULL,
    product_name varchar(200) NOT NULL, -- Denormalized product name
    product_price double precision NOT NULL, -- Denormalized product price
    product_image_url varchar(500), -- Denormalized product image URL
    quantity integer NOT NULL DEFAULT 1,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    -- No foreign key constraints to carts and products tables
    CONSTRAINT cart_items_quantity_check CHECK (quantity > 0),
    UNIQUE (cart_id, product_id)
);

-- Wishlist table
CREATE TABLE wishlists (
    id SERIAL NOT NULL,
    user_id varchar(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id)
    -- No foreign key constraint to users table
);

-- Wishlist items table
CREATE TABLE wishlist_items (
    id SERIAL NOT NULL,
    wishlist_id integer NOT NULL,
    product_id integer NOT NULL,
    product_name varchar(200) NOT NULL, -- Denormalized product name
    product_price double precision NOT NULL, -- Denormalized product price
    product_image_url varchar(500), -- Denormalized product image URL
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    -- No foreign key constraints to wishlists and products tables
    UNIQUE (wishlist_id, product_id)
);

-- Promo codes table
CREATE TABLE promo_codes (
    id SERIAL NOT NULL,
    code varchar(50) NOT NULL UNIQUE,
    discount_type varchar(20) NOT NULL, -- 'percentage' or 'fixed_amount'
    discount_value double precision NOT NULL,
    minimum_order_value double precision DEFAULT 0,
    max_uses integer,
    used_count integer DEFAULT 0,
    valid_from timestamp with time zone,
    valid_until timestamp with time zone,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT promo_codes_discount_value_check CHECK (discount_value > 0),
    CONSTRAINT promo_codes_minimum_order_value_check CHECK (minimum_order_value >= 0),
    CONSTRAINT promo_codes_max_uses_check CHECK (max_uses > 0),
    CONSTRAINT promo_codes_used_count_check CHECK (used_count >= 0)
);

-- Junction table for cart and promo codes (many-to-many relationship)
CREATE TABLE cart_promo_codes (
    id SERIAL NOT NULL,
    cart_id integer NOT NULL,
    promo_code_id integer NOT NULL,
    applied_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    -- No foreign key constraints to carts and promo_codes tables
    UNIQUE (cart_id, promo_code_id)
);

-- Indexes for better performance
CREATE INDEX ix_carts_user_id ON carts (user_id);

CREATE INDEX ix_cart_items_cart_id ON cart_items (cart_id);

CREATE INDEX ix_cart_items_product_id ON cart_items (product_id);

CREATE INDEX ix_wishlists_user_id ON wishlists (user_id);

CREATE INDEX ix_wishlist_items_wishlist_id ON wishlist_items (wishlist_id);

CREATE INDEX ix_wishlist_items_product_id ON wishlist_items (product_id);

CREATE INDEX ix_promo_codes_code ON promo_codes (code);

CREATE INDEX ix_cart_promo_codes_cart_id ON cart_promo_codes (cart_id);

CREATE INDEX ix_cart_promo_codes_promo_code_id ON cart_promo_codes (promo_code_id);

-- Grant privileges to poc_user
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

-- Grant usage on the schema
GRANT USAGE ON SCHEMA public TO poc_user;