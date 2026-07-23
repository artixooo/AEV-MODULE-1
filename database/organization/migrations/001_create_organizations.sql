CREATE TABLE organizations (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    organization_name VARCHAR(255) NOT NULL,

    organization_code VARCHAR(50) UNIQUE NOT NULL,

    description TEXT,

    website VARCHAR(255),

    status VARCHAR(30) DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);