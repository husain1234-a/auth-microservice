-- Product Microservice Database Schema
-- This schema is designed for isolated product service database with no foreign key constraints

-- Categories table (managed by product service)
CREATE TABLE categories (
    id SERIAL NOT NULL,
    name varchar(100) NOT NULL,
    image_url varchar(500),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id)
);

-- Products table (managed by product service)
CREATE TABLE products (
    id SERIAL NOT NULL,
    name varchar(200) NOT NULL,
    description text,
    price double precision NOT NULL,
    mrp double precision,
    category_id integer, -- No foreign key constraint
    category_name varchar(100), -- Denormalized category name
    image_url varchar(500),
    stock_quantity integer DEFAULT 0,
    unit varchar(20), -- kg, gm, piece, liter
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT products_price_check CHECK (price > (0)::double precision),
    CONSTRAINT products_mrp_check CHECK (mrp > (0)::double precision),
    CONSTRAINT products_stock_quantity_check CHECK (stock_quantity >= 0)
);

-- Indexes for better performance
CREATE INDEX ix_products_id ON products USING btree (id);

CREATE INDEX ix_products_category_id ON products USING btree (category_id);

CREATE INDEX ix_categories_id ON categories USING btree (id);

-- Grant privileges to poc_user
GRANT ALL PRIVILEGES ON TABLE categories TO poc_user;

GRANT ALL PRIVILEGES ON TABLE products TO poc_user;

-- Grant usage on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO poc_user;

-- Grant usage on the schema
GRANT USAGE ON SCHEMA public TO poc_user;