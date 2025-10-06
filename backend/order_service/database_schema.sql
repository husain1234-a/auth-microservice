-- Order Microservice Database Schema

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
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for orders table
CREATE INDEX idx_order_user_status ON orders (user_id, status);

CREATE INDEX idx_order_delivery_partner ON orders (delivery_partner_id);

CREATE INDEX idx_order_created_at ON orders (created_at);

-- Order Items table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
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
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Order Feedback table
CREATE TABLE order_feedback (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
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