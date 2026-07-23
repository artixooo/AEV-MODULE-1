CREATE TABLE workspaces (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    organization_id UUID NOT NULL,

    workspace_name VARCHAR(255) NOT NULL,

    workspace_code VARCHAR(50) NOT NULL,

    description TEXT,

    status VARCHAR(30) DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_workspace_code_per_org
        UNIQUE (organization_id, workspace_code),

    FOREIGN KEY (organization_id)
        REFERENCES organizations(id)
        ON DELETE CASCADE

);