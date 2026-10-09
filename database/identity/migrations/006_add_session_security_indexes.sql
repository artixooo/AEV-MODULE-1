CREATE INDEX IF NOT EXISTS idx_sessions_user_id
    ON sessions(user_id);

CREATE INDEX IF NOT EXISTS idx_sessions_tenant_id
    ON sessions(tenant_id);

CREATE INDEX IF NOT EXISTS idx_sessions_expires_at
    ON sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_session_id
    ON refresh_tokens(session_id);
