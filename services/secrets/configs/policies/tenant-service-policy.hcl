# ==============================================================================
# Dynamic Policy: Tenant-Scoped Service Isolation Policy
# ==============================================================================

# Deny root enumeration and listing across tenant namespaces
path "secret/data/tenants" {
  capabilities = ["deny"]
}

path "secret/metadata/tenants" {
  capabilities = ["deny"]
}

# Dynamic tenant configuration partition (database, integration tokens, configs)
path "secret/data/tenants/{{identity.entity.metadata.tenant_id}}/config/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/tenants/{{identity.entity.metadata.tenant_id}}/config/*" {
  capabilities = ["read", "list", "delete"]
}

# Dynamic tenant service & connector credentials
path "secret/data/tenants/{{identity.entity.metadata.tenant_id}}/services/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/tenants/{{identity.entity.metadata.tenant_id}}/services/*" {
  capabilities = ["read", "list"]
}

# User MFA partition (inherited from Week 5)
path "secret/data/tenants/{{identity.entity.metadata.tenant_id}}/users/*/mfa" {
  capabilities = ["create", "read", "update", "delete"]
}

# Explicit denial for any wildcard cross-tenant traversal attempt
path "secret/data/tenants/+" {
  capabilities = ["deny"]
}

path "secret/metadata/tenants/+" {
  capabilities = ["deny"]
}