CREATE TABLE secret_metadata (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    secret_name VARCHAR(150) NOT NULL,

    vault_path VARCHAR(255) NOT NULL UNIQUE,

    secret_type VARCHAR(50) NOT NULL,

    description TEXT,

    owner_service VARCHAR(100) NOT NULL,

    current_version INTEGER DEFAULT 1,

    status VARCHAR(30) DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);