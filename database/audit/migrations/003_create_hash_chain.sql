CREATE TABLE audit_hash_chain (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    audit_log_id UUID NOT NULL UNIQUE,

    previous_hash VARCHAR(255),

    current_hash VARCHAR(255) NOT NULL,

    hash_algorithm VARCHAR(30) DEFAULT 'SHA-256',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (audit_log_id)
        REFERENCES audit_logs(id)
        ON DELETE CASCADE

);

-- Quickly locate hash information for an audit log
CREATE INDEX idx_audit_hash_chain_audit_log_id
ON audit_hash_chain(audit_log_id);