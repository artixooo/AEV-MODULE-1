CREATE TABLE feature_flags (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    flag_key VARCHAR(255) NOT NULL UNIQUE,

    flag_name VARCHAR(255) NOT NULL,

    description TEXT,

    is_enabled BOOLEAN DEFAULT FALSE,

    scope VARCHAR(30) DEFAULT 'GLOBAL',

    organization_id UUID,

    workspace_id UUID,

    project_id UUID,

    rollout_percentage INTEGER DEFAULT 100,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_rollout_percentage
        CHECK (rollout_percentage BETWEEN 0 AND 100)

);

-- Find feature flags by scope
CREATE INDEX idx_feature_flags_scope
ON feature_flags(scope);

-- Find feature flags for an organization
CREATE INDEX idx_feature_flags_organization
ON feature_flags(organization_id);

-- Find feature flags for a workspace
CREATE INDEX idx_feature_flags_workspace
ON feature_flags(workspace_id);

-- Find feature flags for a project
CREATE INDEX idx_feature_flags_project
ON feature_flags(project_id);

-- Find enabled feature flags quickly
CREATE INDEX idx_feature_flags_enabled
ON feature_flags(is_enabled);