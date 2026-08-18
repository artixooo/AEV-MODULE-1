CREATE TABLE sod_policies (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    rule_name VARCHAR(150) NOT NULL UNIQUE,

    conflicting_roles JSONB NOT NULL,

    conflicting_permissions JSONB NOT NULL,

    description TEXT,

    severity VARCHAR(30) DEFAULT 'HIGH',

    status VARCHAR(30) DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
