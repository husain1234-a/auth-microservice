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
    CONSTRAINT products_price_check CHECK (price > (0)::double precision),
    CONSTRAINT products_mrp_check CHECK (mrp > (0)::double precision),
    CONSTRAINT products_stock_quantity_check CHECK (stock_quantity >= 0)
);

CREATE INDEX ix_products_id ON public.products USING btree (id);

CREATE INDEX ix_categories_id ON public.categories USING btree (id);