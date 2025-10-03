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