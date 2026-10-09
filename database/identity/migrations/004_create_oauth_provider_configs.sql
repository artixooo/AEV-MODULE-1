CREATE TABLE IF NOT EXISTS oauth_provider_configs (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    tenant_id UUID NOT NULL,

    provider VARCHAR(100) NOT NULL,

    client_id VARCHAR(255) NOT NULL,

    client_secret_ref VARCHAR(255) NOT NULL,

    authorization_url TEXT NOT NULL,

    token_url TEXT NOT NULL,

    redirect_uri TEXT NOT NULL,

    scopes TEXT NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_oauth_provider_configs_tenant_provider
        UNIQUE (tenant_id, provider)

);
