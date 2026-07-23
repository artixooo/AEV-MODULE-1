CREATE TABLE configuration (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    config_key VARCHAR(255) NOT NULL UNIQUE,

    config_value TEXT NOT NULL,

    data_type VARCHAR(30) NOT NULL,

    scope VARCHAR(30) DEFAULT 'GLOBAL',

    organization_id UUID,

    workspace_id UUID,

    project_id UUID,

    description TEXT,

    is_editable BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- Find configuration by scope
CREATE INDEX idx_configuration_scope
ON configuration(scope);

-- Find configuration for an organization
CREATE INDEX idx_configuration_organization
ON configuration(organization_id);

-- Find configuration for a workspace
CREATE INDEX idx_configuration_workspace
ON configuration(workspace_id);

-- Find configuration for a project
CREATE INDEX idx_configuration_project
ON configuration(project_id);