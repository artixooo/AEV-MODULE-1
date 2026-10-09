# Database Schemas Architecture

AEV Module 1 (Pod Alpha — Platform Foundation & CTEM Substrate) implements a domain-driven, service-isolated database architecture where each microservice maintains its own dedicated schema definitions, migrations, and seed datasets within its service domain directory:

| Service / Domain | Schema Directory | Migrations Directory | Description |
|---|---|---|---|
| **Identity Service** | `database/identity/schema/` | `database/identity/migrations/` | Users, sessions, refresh tokens, OAuth2/OIDC configs, SCIM resources |
| **Organization Service** | `database/organization/schema/` | `database/organization/migrations/` | 3-tier hierarchy (Organizations, Workspaces, Projects), tenant quotas, memberships |
| **Policy Service** | `database/policy/schema/` | `database/policy/migrations/` | RBAC roles, permissions, role-permissions mapping, ABAC policies, Segregation of Duties (SoD) |
| **Audit Service** | `database/audit/schema/` | `database/audit/migrations/` | Append-only immutable ledger, SHA-256 hash chaining, WORM replication metadata |
| **Secrets Service** | `database/secrets/schema/` | `database/secrets/migrations/` | Vault per-tenant mounts, secret metadata, NIST SP 800-57 rotation schedules |
| **Configuration Service** | `database/configuration/schema/` | `database/configuration/migrations/` | Feature flags, kill switch states, tenant-level dynamic overrides |
| **Shared Platform** | `database/shared/` | `database/shared/` | Shared PostgreSQL extensions (`uuid-ossp`, `pgcrypto`) and trigger functions |

## Multi-Tenant Isolation
All multi-tenant services enforce strict isolation via PostgreSQL Row-Level Security (RLS) policies defined in their respective migration files, keyed on `organization_id` / `tenant_id`.
