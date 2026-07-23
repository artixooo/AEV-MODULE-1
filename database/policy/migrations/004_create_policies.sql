CREATE TABLE policies (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    policy_name VARCHAR(150) NOT NULL,

    policy_code VARCHAR(100) NOT NULL UNIQUE,

    resource VARCHAR(100) NOT NULL,

    action VARCHAR(50) NOT NULL,

    effect VARCHAR(10) NOT NULL DEFAULT 'ALLOW',

    conditions JSONB NOT NULL,

    priority INTEGER DEFAULT 100,

    is_system BOOLEAN DEFAULT TRUE,

    status VARCHAR(30) DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);