CREATE TABLE roles (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    role_name VARCHAR(100) NOT NULL,

    role_code VARCHAR(50) NOT NULL UNIQUE,

    description TEXT,

    is_system BOOLEAN DEFAULT FALSE,

    status VARCHAR(30) DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);