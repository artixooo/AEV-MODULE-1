CREATE TABLE configuration_history (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    configuration_id UUID NOT NULL,

    old_value TEXT,

    new_value TEXT NOT NULL,

    changed_by UUID,

    change_reason TEXT,

    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (configuration_id)
        REFERENCES configuration(id)
        ON DELETE CASCADE

);

-- Find history for a configuration
CREATE INDEX idx_configuration_history_configuration
ON configuration_history(configuration_id);

-- Find changes made by a user
CREATE INDEX idx_configuration_history_changed_by
ON configuration_history(changed_by);

-- Find changes by date
CREATE INDEX idx_configuration_history_changed_at
ON configuration_history(changed_at);