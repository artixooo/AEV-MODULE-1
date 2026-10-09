CREATE TABLE organizations (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    organization_name VARCHAR(255) NOT NULL,

    organization_code VARCHAR(50) UNIQUE NOT NULL,

    description TEXT,

    website VARCHAR(255),

    status VARCHAR(30) DEFAULT 'ACTIVE',

    parent_organization_id UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_parent_organization
        FOREIGN KEY (parent_organization_id)
        REFERENCES organizations(id)
        ON DELETE SET NULL

);