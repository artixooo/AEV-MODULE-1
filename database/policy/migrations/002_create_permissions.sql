CREATE TABLE permissions (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    permission_name VARCHAR(150) NOT NULL,

    permission_code VARCHAR(100) NOT NULL UNIQUE,

    resource VARCHAR(100) NOT NULL,

    action VARCHAR(50) NOT NULL,

    description TEXT,

    is_system BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);