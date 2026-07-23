CREATE TABLE audit_events (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    audit_log_id UUID NOT NULL,

    event_payload JSONB NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (audit_log_id)
        REFERENCES audit_logs(id)
        ON DELETE CASCADE

);

-- Quickly find event details for an audit log
CREATE INDEX idx_audit_events_audit_log_id
ON audit_events(audit_log_id);