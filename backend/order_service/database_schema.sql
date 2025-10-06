-- Order Microservice Database Schema

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

-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id varchar(255) NOT NULL,
    delivery_partner_id varchar(255),
    total_amount DECIMAL(10, 2) CHECK (total_amount > 0) NOT NULL,
    delivery_fee DECIMAL(10, 2) CHECK (delivery_fee >= 0) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    delivery_address TEXT NOT NULL,
    delivery_latitude VARCHAR(20),
    delivery_longitude VARCHAR(20),
    estimated_delivery_time TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    scheduled_for TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (uid) ON DELETE CASCADE
);

-- Indexes for orders table
CREATE INDEX idx_order_user_status ON orders (user_id, status);

CREATE INDEX idx_order_delivery_partner ON orders (delivery_partner_id);

CREATE INDEX idx_order_created_at ON orders (created_at);

-- Order Items table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL,
    quantity INTEGER CHECK (quantity > 0) NOT NULL,
    price DECIMAL(10, 2) CHECK (price > 0) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for order_items table
CREATE INDEX idx_order_items_order_id ON order_items (order_id);

-- Order Templates table
CREATE TABLE order_templates (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    items JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT order_templates_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (uid) ON DELETE CASCADE
);

-- Order Feedback table
CREATE TABLE order_feedback (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    rating INTEGER CHECK (
        rating >= 1
        AND rating <= 5
    ),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for order_feedback table
CREATE INDEX idx_order_feedback_order_id ON order_feedback (order_id);

-- Connect to your database as a superuser (like postgres) and run:
GRANT ALL PRIVILEGES ON TABLE orders TO poc_user;

GRANT ALL PRIVILEGES ON TABLE order_items TO poc_user;

GRANT ALL PRIVILEGES ON TABLE order_templates TO poc_user;

GRANT ALL PRIVILEGES ON TABLE order_feedback TO poc_user;

-- Also grant usage on the schema
GRANT USAGE ON SCHEMA public TO poc_user;