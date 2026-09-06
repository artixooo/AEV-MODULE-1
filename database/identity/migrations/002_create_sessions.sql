CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    tenant_id UUID NOT NULL,

    session_token TEXT NOT NULL UNIQUE,

    device_name VARCHAR(150),

    device_type VARCHAR(50),

    ip_address VARCHAR(50),

    user_agent TEXT,

    is_active BOOLEAN DEFAULT TRUE,

    expires_at TIMESTAMP NOT NULL,

    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);