CREATE TABLE projects (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    workspace_id UUID NOT NULL,

    project_name VARCHAR(255) NOT NULL,

    project_code VARCHAR(50) NOT NULL,

    description TEXT,

    start_date DATE,

    end_date DATE,

    status VARCHAR(30) DEFAULT 'PLANNING',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_project_code_per_workspace
        UNIQUE (workspace_id, project_code),

    FOREIGN KEY (workspace_id)
        REFERENCES workspaces(id)
        ON DELETE CASCADE

);