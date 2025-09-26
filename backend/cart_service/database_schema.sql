-- Cart Microservice Database Schema
-- This schema is designed to work with the existing auth and product services

-- Users table (provided by auth service)
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

-- Categories table (provided by product service)
CREATE TABLE categories (
    id SERIAL NOT NULL,
    name varchar(100) NOT NULL,
    image_url varchar(500),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id)
);

-- Products table (provided by product service)
CREATE TABLE products (
    id SERIAL NOT NULL,
    name varchar(200) NOT NULL,
    description text,
    price double precision NOT NULL,
    mrp double precision,
    category_id integer,
    image_url varchar(500),
    stock_quantity integer,
    unit varchar(20),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES categories (id),
    CONSTRAINT products_price_check CHECK (price > (0)::double precision),
    CONSTRAINT products_mrp_check CHECK (mrp > (0)::double precision),
    CONSTRAINT products_stock_quantity_check CHECK (stock_quantity >= 0)
);

CREATE INDEX ix_products_id ON public.products USING btree (id);

CREATE INDEX ix_categories_id ON public.categories USING btree (id);

-- Cart tables (new for cart service)

-- Main cart table
CREATE TABLE carts (
    id SERIAL NOT NULL,
    user_id varchar(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT carts_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (uid) ON DELETE CASCADE
);

-- Cart items table
CREATE TABLE cart_items (
    id SERIAL NOT NULL,
    cart_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL DEFAULT 1,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT cart_items_cart_id_fkey FOREIGN KEY (cart_id) REFERENCES carts (id) ON DELETE CASCADE,
    CONSTRAINT cart_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
    CONSTRAINT cart_items_quantity_check CHECK (quantity > 0),
    UNIQUE (cart_id, product_id)
);

-- Wishlist table
CREATE TABLE wishlists (
    id SERIAL NOT NULL,
    user_id varchar(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT wishlists_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (uid) ON DELETE CASCADE
);

-- Wishlist items table
CREATE TABLE wishlist_items (
    id SERIAL NOT NULL,
    wishlist_id integer NOT NULL,
    product_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT wishlist_items_wishlist_id_fkey FOREIGN KEY (wishlist_id) REFERENCES wishlists (id) ON DELETE CASCADE,
    CONSTRAINT wishlist_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
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
    CONSTRAINT cart_promo_codes_cart_id_fkey FOREIGN KEY (cart_id) REFERENCES carts (id) ON DELETE CASCADE,
    CONSTRAINT cart_promo_codes_promo_code_id_fkey FOREIGN KEY (promo_code_id) REFERENCES promo_codes (id) ON DELETE CASCADE,
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