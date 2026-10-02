```markdown
# Role-Based Access Control (RBAC) Architecture

## Overview
> **Implementation Status:** This document defines the target architectural model for access control. The full enforcement of this Tenant/Workspace hierarchy and specific role mappings is tracked as follow-up work.

The platform utilizes a centralized, multi-tenant Role-Based Access Control (RBAC) model. Access decisions are decoupled between edge routing and downstream policy evaluations.

---

## RBAC Model Hierarchy

```text
Tenant / Organization
 └── Workspace
      └── Project
           └── Roles [ Owner | Admin | Member | Viewer ]
                └── Permissions [ create, read, update, delete ]

```

---

## Core Roles & Permissions

| Role | Scope | Permitted Actions |
| --- | --- | --- |
| `owner` | Organization | Full administrative control, billing management, organization deletion. |
| `admin` | Organization / Workspace | Manage users, configure workspace settings, assign roles, create projects. |
| `member` | Workspace / Project | Read and write workspace resources, create and manage assigned tasks. |
| `viewer` | Project | Read-only access to assigned projects. Cannot modify or delete resources. |

---

## Context Propagation

The Gateway extracts roles and permissions from validated JWT claims and forwards them via HTTP headers:

* `X-User-Id`: Extracted from `sub`
* `X-Tenant-Id`: Extracted from `tenant_id`
* `X-User-Roles`: Comma-delimited roles list
* `X-User-Permissions`: Comma-delimited permissions list

Downstream services (Organization, Policy, Secrets) inspect these headers directly to enforce localized access controls without needing to re-parse or verify the JWT signature.

```

```