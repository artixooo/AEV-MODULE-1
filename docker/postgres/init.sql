-- ============================================================================
-- POD ALPHA: PLATFORM FOUNDATION & TRUST LAYER
-- Comprehensive Database Initialization & Master Schema
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. ORGANIZATIONS, WORKSPACES, PROJECTS & TENANTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_name VARCHAR(255) NOT NULL,
    organization_code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    website VARCHAR(255),
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    parent_organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    workspace_name VARCHAR(255) NOT NULL,
    workspace_code VARCHAR(50) NOT NULL,
    description TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_workspace_org_code UNIQUE (organization_id, workspace_code)
);

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_name VARCHAR(255) NOT NULL,
    project_code VARCHAR(50) NOT NULL,
    description TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_project_workspace_code UNIQUE (workspace_id, project_code)
);

CREATE TABLE IF NOT EXISTS tenant_quotas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(100) NOT NULL,
    quota_name VARCHAR(100) NOT NULL,
    limit_value INTEGER NOT NULL,
    unit VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_tenant_quota UNIQUE (tenant_id, quota_name)
);

-- ============================================================================
-- 2. IDENTITY, USERS, SESSIONS & TOKENS
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(150),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    tenant_id UUID,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'MEMBER',
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_membership_org_user UNIQUE (organization_id, user_id)
);

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,
    session_token TEXT,
    token_hash VARCHAR(64),
    device_name VARCHAR(150),
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    jti VARCHAR(255) UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS oauth_provider_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    provider_name VARCHAR(100) NOT NULL,
    client_id VARCHAR(255) NOT NULL,
    client_secret_encrypted TEXT NOT NULL,
    auth_url VARCHAR(500) NOT NULL,
    token_url VARCHAR(500) NOT NULL,
    userinfo_url VARCHAR(500),
    scopes VARCHAR(255) DEFAULT 'openid profile email',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS oidc_provider_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    provider_name VARCHAR(100) NOT NULL,
    issuer_url VARCHAR(500) NOT NULL,
    client_id VARCHAR(255) NOT NULL,
    client_secret_encrypted TEXT NOT NULL,
    jwks_uri VARCHAR(500),
    scopes VARCHAR(255) DEFAULT 'openid profile email',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 3. POLICY, RBAC, ABAC & SOD
-- ============================================================================

CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    effect VARCHAR(20) NOT NULL DEFAULT 'ALLOW',
    actions JSONB NOT NULL DEFAULT '[]',
    resources JSONB NOT NULL DEFAULT '[]',
    conditions JSONB DEFAULT '{}',
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sod_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    role_a_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    role_b_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 4. CRYPTOGRAPHIC TAMPER-EVIDENT AUDIT LEDGER
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    user_id UUID,
    organization_id UUID,
    workspace_id UUID,
    project_id UUID,
    resource_type VARCHAR(100),
    resource_id UUID,
    action VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_id UUID,
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_log_id UUID NOT NULL REFERENCES audit_logs(id) ON DELETE CASCADE,
    event_payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_hash_chain (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_log_id UUID NOT NULL UNIQUE REFERENCES audit_logs(id) ON DELETE CASCADE,
    previous_hash VARCHAR(255) NOT NULL,
    current_hash VARCHAR(255) NOT NULL,
    hash_algorithm VARCHAR(30) DEFAULT 'SHA-256',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 5. CONFIGURATION & FEATURE FLAGS
-- ============================================================================

CREATE TABLE IF NOT EXISTS configuration (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    is_secret BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255) NOT NULL UNIQUE,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT,
    roll_out_percentage INTEGER NOT NULL DEFAULT 100,
    target_organizations JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS configuration_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID REFERENCES configuration(id) ON DELETE CASCADE,
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(255),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 6. SECRETS METADATA & NIST KEY ROTATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS secret_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    path VARCHAR(500) NOT NULL UNIQUE,
    version INTEGER NOT NULL DEFAULT 1,
    algorithm VARCHAR(50) DEFAULT 'AES-256-GCM',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS secret_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metadata_id UUID NOT NULL REFERENCES secret_metadata(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS secret_rotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    secret_path VARCHAR(500) NOT NULL UNIQUE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    key_strength VARCHAR(50) NOT NULL DEFAULT 'AES-256-GCM',
    rotation_interval_days INTEGER NOT NULL DEFAULT 90,
    last_rotated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    next_rotation_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + INTERVAL '90 days'),
    status VARCHAR(30) NOT NULL DEFAULT 'SYNCED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SEED DATA: ORGANIZATIONS, ROLES, PERMISSIONS, SEED AUDIT CHAIN & FLAGS
-- ============================================================================

-- Organizations
INSERT INTO organizations (id, organization_name, organization_code, description, website, status)
VALUES 
    ('00000000-0000-0000-0000-000000000001', 'Acme Cyber Defense Corp', 'acme-defense', 'Primary enterprise defense operations', 'https://defense.acme.com', 'ACTIVE'),
    ('00000000-0000-0000-0000-000000000002', 'CyArt Tech Enterprise', 'cyart-tech', 'Attack Exposure Validation host partner', 'https://cyart.io', 'ACTIVE'),
    ('00000000-0000-0000-0000-000000000003', 'Apex Threat Intelligence', 'apex-intel', 'Global intelligence provider', 'https://apex-threat.org', 'ACTIVE')
ON CONFLICT (organization_code) DO NOTHING;

-- Workspaces
INSERT INTO workspaces (id, organization_id, workspace_name, workspace_code, description, status)
VALUES
    ('00000000-0000-0000-0001-000000000001', '00000000-0000-0000-0000-000000000002', 'Pod Alpha Core', 'pod-alpha-core', 'Foundation and trust substrate infrastructure', 'ACTIVE'),
    ('00000000-0000-0000-0001-000000000002', '00000000-0000-0000-0000-000000000002', 'Security Operations Center', 'soc-prod', 'Real-time telemetry and posture monitoring', 'ACTIVE')
ON CONFLICT DO NOTHING;

-- Quotas
INSERT INTO tenant_quotas (tenant_id, quota_name, limit_value, unit, description)
VALUES 
    ('00000000-0000-0000-0000-000000000002', 'max_workspaces', 1000, 'count', 'Maximum workspaces per tenant'),
    ('00000000-0000-0000-0000-000000000002', 'max_projects', 10000, 'count', 'Maximum projects per workspace'),
    ('00000000-0000-0000-0000-000000000002', 'max_identities', 50000, 'count', 'Maximum provisioned identities')
ON CONFLICT DO NOTHING;

-- Platform Seeded Roles (From Pod Alpha Proposal)
INSERT INTO roles (id, name, description, is_system)
VALUES
    ('10000000-0000-0000-0000-000000000001', 'SUPER_ADMIN', 'Platform-wide administrator with unrestricted capabilities', TRUE),
    ('10000000-0000-0000-0000-000000000002', 'ORG_ADMIN', 'Organization owner with tenant scope administration', TRUE),
    ('10000000-0000-0000-0000-000000000003', 'SECURITY_ADMIN', 'Manages authentication, policies, and cryptographic keys', TRUE),
    ('10000000-0000-0000-0000-000000000004', 'AUDITOR', 'Read-only access to tamper-evident audit ledger and compliance logs', TRUE),
    ('10000000-0000-0000-0000-000000000005', 'OPERATOR', 'Operational maintenance, health inspection, and configuration view', TRUE),
    ('10000000-0000-0000-0000-000000000006', 'MEMBER', 'Standard authenticated platform tenant user', TRUE)
ON CONFLICT (name) DO NOTHING;

-- Permissions
INSERT INTO permissions (name, resource, action, description)
VALUES
    ('users:read', 'users', 'read', 'View user profiles and directories'),
    ('users:write', 'users', 'write', 'Create and modify user identities'),
    ('org:read', 'organizations', 'read', 'View tenant and workspace hierarchy'),
    ('org:write', 'organizations', 'write', 'Modify organization configurations'),
    ('policy:evaluate', 'policy', 'evaluate', 'Evaluate runtime ABAC and RBAC policies'),
    ('policy:manage', 'policy', 'write', 'Create and alter authorization policies'),
    ('audit:read', 'audit', 'read', 'Query audit logs and verify cryptographic chain'),
    ('secrets:access', 'secrets', 'read', 'Retrieve tenant-isolated credentials'),
    ('secrets:rotate', 'secrets', 'rotate', 'Execute cryptographic key rotations'),
    ('config:manage', 'configuration', 'write', 'Set runtime configuration and feature flags')
ON CONFLICT (name) DO NOTHING;

-- Seed Admin User (password is Admin123!)
INSERT INTO users (id, username, email, hashed_password, full_name, is_active, is_superuser, mfa_enabled, organization_id)
VALUES (
    '20000000-0000-0000-0000-000000000001',
    'admin',
    'admin@cyart.io',
    '$2b$12$K89sO.X9b4iPjO5L8V6Eeu7oX1QOqW7X2pU0vS.5g9dK6dG7jLq1m',
    'CyArt Super Admin',
    TRUE,
    TRUE,
    FALSE,
    '00000000-0000-0000-0000-000000000002'
) ON CONFLICT (email) DO NOTHING;

-- Membership
INSERT INTO memberships (organization_id, user_id, role, status)
VALUES ('00000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000001', 'SUPER_ADMIN', 'ACTIVE')
ON CONFLICT DO NOTHING;

-- Feature Flags (with instant kill switch capabilities)
INSERT INTO feature_flags (key, enabled, description, roll_out_percentage)
VALUES
    ('audit_immutable_backup', TRUE, 'Hourly immutable WORM storage backup replication', 100),
    ('jit_access_workflow', TRUE, 'Just-In-Time temporary privilege elevation', 100),
    ('scim_provisioning_v2', TRUE, 'SCIM 2.0 automated employee provisioning', 100),
    ('per_tenant_key_rotation', TRUE, 'NIST SP 800-57 automated key lifecycle management', 100),
    ('strict_rls_enforcement', TRUE, 'PostgreSQL database row-level security isolation', 100),
    ('abac_context_evaluator', TRUE, 'Context-aware dynamic IP and time boundary checking', 100)
ON CONFLICT (key) DO NOTHING;

-- Key Vault Secret Paths & NIST Rotation Schedules
INSERT INTO secret_rotations (secret_path, organization_id, key_strength, rotation_interval_days, status)
VALUES
    ('/secret/data/tenant_00000000-0000-0000-0000-000000000002/database', '00000000-0000-0000-0000-000000000002', 'AES-256-GCM', 90, 'SYNCED'),
    ('/secret/data/tenant_00000000-0000-0000-0000-000000000002/jwt_signing_key', '00000000-0000-0000-0000-000000000002', 'Ed25519', 30, 'ACTIVE'),
    ('/secret/data/tenant_00000000-0000-0000-0000-000000000002/saml_private_key', '00000000-0000-0000-0000-000000000002', 'RSA-4096', 365, 'SYNCED'),
    ('/secret/data/tenant_00000000-0000-0000-0000-000000000001/database', '00000000-0000-0000-0000-000000000001', 'AES-256-GCM', 90, 'SYNCED'),
    ('/secret/data/tenant_00000000-0000-0000-0000-000000000001/jwt_signing_key', '00000000-0000-0000-0000-000000000001', 'Ed25519', 30, 'ACTIVE')
ON CONFLICT (secret_path) DO NOTHING;

-- Initial Cryptographic Hash Chain Entries (Valid SHA-256 mathematical chain)
INSERT INTO audit_logs (id, event_id, event_type, service_name, action, status, actor_name, ip_address, event_timestamp)
VALUES 
    ('30000000-0000-0000-0000-000000000001', gen_random_uuid(), 'SystemStart', 'gateway', 'SYSTEM_BOOT', 'SUCCESS', 'system', '127.0.0.1', '2026-10-09 00:00:00+00'),
    ('30000000-0000-0000-0000-000000000002', gen_random_uuid(), 'AuthSuccess', 'identity', 'USER_LOGIN', 'SUCCESS', 'admin@cyart.io', '192.168.1.10', '2026-10-09 00:05:00+00'),
    ('30000000-0000-0000-0000-000000000003', gen_random_uuid(), 'SSOUpdate', 'identity', 'SSO_PROVIDER_UPDATE', 'SUCCESS', 'admin@cyart.io', '192.168.1.10', '2026-10-09 00:10:00+00'),
    ('30000000-0000-0000-0000-000000000004', gen_random_uuid(), 'PolicyEval', 'policy', 'POLICY_EVALUATION', 'SUCCESS', 'auditor@cyart.io', '10.0.4.15', '2026-10-09 00:15:00+00'),
    ('30000000-0000-0000-0000-000000000005', gen_random_uuid(), 'SecretRotated', 'secrets', 'SECRET_ROTATION', 'SUCCESS', 'system-vault', '127.0.0.1', '2026-10-09 00:20:00+00')
ON CONFLICT DO NOTHING;

INSERT INTO audit_hash_chain (audit_log_id, previous_hash, current_hash, hash_algorithm)
VALUES
    ('30000000-0000-0000-0000-000000000001', '0000000000000000000000000000000000000000000000000000000000000000', '6de2ca432f8a9f172ea5dac957c1cc4ad7d9b4ab6c3b27757eb37e7bf5b05373', 'SHA-256'),
    ('30000000-0000-0000-0000-000000000002', '6de2ca432f8a9f172ea5dac957c1cc4ad7d9b4ab6c3b27757eb37e7bf5b05373', '355a953139e7c1bc3e633c6b011b28c43da19cb4e6fb1c0d2e4d6d3ba5053240', 'SHA-256'),
    ('30000000-0000-0000-0000-000000000003', '355a953139e7c1bc3e633c6b011b28c43da19cb4e6fb1c0d2e4d6d3ba5053240', '9bb26a153eb814f1ae69690944435f652be07f2988e3beaf35fc111c9df6236f', 'SHA-256'),
    ('30000000-0000-0000-0000-000000000004', '9bb26a153eb814f1ae69690944435f652be07f2988e3beaf35fc111c9df6236f', 'cd13a3bbc2e4167c9b95ff27069364b851ca5365d60494321e594cfa57d5af8e', 'SHA-256'),
    ('30000000-0000-0000-0000-000000000005', 'cd13a3bbc2e4167c9b95ff27069364b851ca5365d60494321e594cfa57d5af8e', '0f7a0ab63073423ba24c43744f3799bc5a33266d3a0d8a1080b6ef2f29fce489', 'SHA-256')
ON CONFLICT DO NOTHING;