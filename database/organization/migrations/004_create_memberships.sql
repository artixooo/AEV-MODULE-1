CREATE TABLE memberships (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    organization_id UUID NOT NULL,

    workspace_id UUID NOT NULL,

    membership_status VARCHAR(30) DEFAULT 'ACTIVE',

    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_membership
        UNIQUE (
            user_id,
            organization_id,
            workspace_id
        ),

    CONSTRAINT fk_membership_organization
        FOREIGN KEY (organization_id)
        REFERENCES organizations(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_membership_workspace
        FOREIGN KEY (workspace_id)
        REFERENCES workspaces(id)
        ON DELETE CASCADE

);