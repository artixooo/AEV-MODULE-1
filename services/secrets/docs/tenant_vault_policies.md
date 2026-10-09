# Tenant-Scoped Secret Isolation Architecture

## 1. Overview
Week 6 introduces tenant-scoped secret isolation for Module 1 (Pod Alpha) and downstream consumers. Every tenant's credentials, configuration keys, and service tokens are compartmentalized under dedicated subtrees.

## 2. Vault Path Taxonomy
- **Tenant Configuration:** `secret/data/tenants/{tenant_id}/config/{category}/{key}`
- **Tenant Services / Connectors:** `secret/data/tenants/{tenant_id}/services/{service_name}`
- **Tenant User MFA:** `secret/data/tenants/{tenant_id}/users/{user_id}/mfa`

## 3. Dynamic Policy Scoping
Policies avoid hardcoding static tenant identifiers by evaluating token entity metadata:
```hcl
path "secret/data/tenants/{{identity.entity.metadata.tenant_id}}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}