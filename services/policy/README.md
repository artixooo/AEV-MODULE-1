# Policy Service — Pod Alpha (Squad 4)

## Authorization Service — Tenant & Scope-Aware RBAC Foundation (Week 4)

**Squad Lead:** Utkarsh Pratham | **Squad Members:** Narayanan Varadarajan & Pratik | **Port:** 8002

---

## Scope & Milestones

This service is being built up in stages, tracked by separate issues:

| Stage | Issue | Scope |
| :--- | :--- | :--- |
| **Project setup & DB prep** | #5 | Week 1 — project structure, Docker, migrations |
| **Infrastructure readiness** | #17 | Week 2 — config, DB connectivity, health checks, graceful shutdown |
| **RBAC foundation** | #61 | Week 3 — Role/permission data access, RBAC evaluation service, JWT-authenticated Policy APIs |
| **Tenant & Scope Authorization** | **#93 (Current)** | **Tenant Context, Cross-Tenant Isolation, Scopes (Org/Workspace/Project), Membership-to-Role mappings** |
| **ABAC / SoD / caching** | Future | Attribute-based conditions, Segregation of Duties, decision caching |

ABAC is explicitly out of scope, as is Segregation of Duties enforcement and decision caching.

---

## 🛡️ Week 4: Tenant & Scope Authorization Architecture

### 1. Multi-Tenant Isolation (Zero Trust)

When evaluating permissions, the Policy Service checks two things: that `tenant_id` matches `target_tenant_id`, **and** that the resolved role's `organization_id` (stored in the database) actually matches the target tenant — not just that the caller's two supplied values match each other. A role belonging to one organization is genuinely unreachable when evaluated against a different organization's context, even if the caller sends internally-consistent but fabricated tenant values for both fields; the role lookup itself fails and returns `role_not_found`. This is backed by a real `organization_id` column on the `Role` table (migration `006_add_organization_scoping.sql`), verified against a live PostgreSQL instance.

Any attempt by an entity in **Tenant A** to access or perform operations on a resource owned by **Tenant B** results in an immediate **`DENY`** with reason:
```
cross_tenant_access_denied
```

### 2. Hierarchical Authorization Scopes

The platform organizes resources in a three-tier hierarchy:

$$\text{Organization} \longrightarrow \text{Workspace} \longrightarrow \text{Project}$$

* **Organization Level (`organization`):** Broader scope covering the entire tenant.
* **Workspace Level (`workspace`):** Scoped to a collaborative team workspace.
* **Project Level (`project`):** Granular scope confined to a single project.

> **Known limitation:** Organization-level isolation above is enforced against real database records. Workspace and project-level isolation are currently *interface-only* — the scope hierarchy correctly checks a role's declared authority *breadth* (can this role reach the workspace/project level at all), but there's no `Workspace` or `Project` entity anywhere in the platform yet (checked: not in this service, not in Organization Service, not on any open branch as of Week 4) to check *identity* against (e.g. "can this specific role be used in this specific workspace"). This mirrors Organization Service's own state — even its authorization placeholder explicitly defers real enforcement to this service. Closing this gap is blocked on Organization Service introducing real Workspace/Project data, not on anything in Policy Service.

### 3. Membership-to-Role Mapping

The Policy Service natively resolves Organization Service membership roles to canonical RBAC roles and enforced maximum scopes:

| Organization Membership Role | Effective RBAC Role | Maximum Allowed Scope |
| :--- | :--- | :--- |
| `org_owner` | `admin` | `organization` |
| `org_admin` | `admin` | `organization` |
| `workspace_admin` | `editor` | `workspace` |
| `workspace_member` | `viewer` | `workspace` |
| `project_admin` | `editor` | `project` |
| `project_contributor` | `editor` | `project` |
| `project_viewer` | `viewer` | `project` |
| `viewer` | `viewer` | `project` |

---

## 🔑 A note on authentication vs. authorization

Identity Service issues JWTs containing only a `sub` (the user's email) and `exp` claim — no role. Neither Identity nor Organization Service currently expose a way to look up a user's role. A documented target contract exists (Gateway team's `authentication-contract.md`, branch `week-3-gateway-auth`) specifying that Identity should eventually issue `tenant_id`, `roles`, and `permissions` claims, but that work has not landed yet, and Gateway's own JWT-validation middleware is also still unmerged as of this writing.

Because of this, `POST /evaluate` takes `role_code` (or `membership_role`) as explicit request parameters rather than deriving them from the token, and is additionally restricted to trusted internal callers via a shared `X-Service-API-Key` header (see `app/middleware/service_auth_middleware.py`) — an authenticated end-user JWT alone is not sufficient to call it. This prevents any authenticated user from querying "do I have role X's permissions" for an arbitrary X. Once Identity issues a trustworthy role claim, this endpoint should be revisited to derive role context from the token directly instead.

---

## 📡 API Reference (v1)

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/policy/roles` | Bearer JWT | List all active roles in the system |
| **GET** | `/api/v1/policy/permissions` | Bearer JWT | List all defined permissions |
| **POST** | `/api/v1/policy/evaluate` | Bearer JWT + `X-Service-API-Key` | **Internal Service Endpoint**: Tenant & Scope-aware RBAC evaluation |

### Decision Reasons

* `role_has_permission`: Allowed (Role has the required permission).
* `cross_tenant_access_denied`: Denied (Requester tenant does not match target resource tenant).
* `scope_mismatch`: Denied (User's membership scope cannot access the higher-level requested scope).
* `role_missing_permission`: Denied (Role does not have permission granted).
* `role_not_found`: Denied (Role or membership role does not exist, including a role that exists but belongs to a different organization).
* `permission_not_found`: Denied (Target permission does not exist).

Full interactive docs (Swagger UI) are available at `/docs` once the service is running.

---

## 💡 Example Evaluation Requests

### 1. Tenant-Aware Request (JSON Body)
```json
POST /api/v1/policy/evaluate
Headers:
  Authorization: Bearer <jwt_token>
  X-Service-API-Key: <internal_service_key>

{
  "tenant_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "target_tenant_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "membership_role": "org_admin",
  "permission_code": "org:delete",
  "scope": "organization"
}
```

### 2. Tenant Context via Headers
```json
POST /api/v1/policy/evaluate
Headers:
  Authorization: Bearer <jwt_token>
  X-Service-API-Key: <internal_service_key>
  X-Tenant-ID: "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

{
  "role_code": "editor",
  "permission_code": "project:edit",
  "target_tenant_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
}
```

### 3. Legacy Flat RBAC Request (Backward Compatible)
```json
POST /api/v1/policy/evaluate
Headers:
  Authorization: Bearer <jwt_token>
  X-Service-API-Key: <internal_service_key>

{
  "role_code": "editor",
  "permission_code": "articles:edit"
}
```

---

## ⚙️ Project Structure

`services/policy/` contains: `Dockerfile`, `requirements.txt`, `.env.example`, an `app/` folder with `main.py` plus `core/`, `models/`, `repositories/`, `services/`, `middleware/`, `schemas/`, and `routers/` subfolders, and a `tests/` folder with `test_policy_service.py`, `test_rbac_evaluation.py`, `test_policy_api.py`, `test_auth_middleware.py`, and `test_tenant_context.py`.

`app/api/` and `app/utils/` exist as empty scaffold folders (matching Identity/Organization's structure) — they'll be filled in as future work lands.

---

## 🔧 Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `APP_NAME` | `policy-service` | Service identifier |
| `APP_ENV` | `development` | `development` / `staging` / `production` |
| `PORT` | `8002` | HTTP port |
| `HOST` | `0.0.0.0` | Bind interface |
| `DATABASE_URL` | see `.env.example` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379` | Reserved for future caching |
| `IDENTITY_SERVICE_URL` | `http://localhost:8000` | Upstream Identity Service |
| `ORGANIZATION_SERVICE_URL` | `http://localhost:8001` | Upstream Organization Service |
| `POLICY_CACHE_TTL` | `300` | Reserved for future caching |
| `ENABLE_SOD_ENFORCEMENT` | `true` | Reserved for future SoD logic |
| `JWT_SECRET_KEY` | `change-me` | Shared secret for validating JWTs from Identity Service |
| `JWT_ALGORITHM` | `HS256` | Signing algorithm — must match Identity Service |
| `SERVICE_API_KEY` | `change-me` | Shared secret for trusted internal service-to-service calls (required on `POST /evaluate`) |

Config loads via `pydantic-settings`, reading from environment variables and/or a local `.env` file.

> **Important:** the connection strings and secrets shown above are local development defaults only, matching `docker-compose.yml`'s local Postgres container. Never reuse these values in staging/production — the service refuses to start with default `JWT_SECRET_KEY`/`SERVICE_API_KEY` values outside `development` (see `app/core/config.py`).

---

## 🗄️ Database & Migration Framework

Schema is owned exclusively by SQL migration files, not by the application at runtime:
```
database/policy/migrations/
├── 001_create_roles.sql
├── 002_create_permissions.sql
├── 003_create_role_permissions.sql
├── 004_create_policies.sql
├── 005_create_sod_policies.sql
└── 006_add_organization_scoping.sql
```


Applied via the shared migration runner:

```bash
# From the repository root — DATABASE_URL should come from your environment,
# not be hardcoded (this example uses the local dev default from .env.example)
./database/scripts/migrate.sh
```

The ORM models in `app/models/policy_models.py` mirror this schema exactly (including the native Postgres `UUID` type via `app/core/guid.py`), but table creation/seeding is deliberately kept out of the app itself — this avoids the service silently drifting from the migration-defined schema.

---

## 🚀 Quickstart Guide

```bash
# From services/policy/
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

---

## 🐳 Docker & Docker Compose

```bash
docker build -t policy-service-test .
docker compose up -d postgres
docker compose up --build --no-deps policy
```

Verified locally: image builds cleanly, container starts, `GET /ready` reports database connected over the Docker network.

---

## ❤️ Health Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/` | Service discovery |
| **GET** | `/health` | Liveness check |
| **GET** | `/ready` | Readiness check (503 on DB failure) |

---

## 🛑 Graceful Shutdown

The FastAPI app uses a `lifespan` context manager that verifies the database connection on startup and disposes the connection pool cleanly on shutdown. Verified locally via `docker compose down`.

---

## 🧪 Testing

Run the full automated test suite:
```bash
pytest tests/ -v
```

**Test Coverage:**
* `test_auth_middleware.py`: JWT validation, signature verification, and expired token rejection.
* `test_policy_api.py`: Endpoint authentication, internal service key enforcement, and standard responses.
* `test_policy_service.py`: Service health, readiness, and root discovery.
* `test_rbac_evaluation.py`: Role-permission database evaluation logic.
* `test_tenant_context.py`: Multi-tenant isolation, cross-tenant denial, all three scope levels, membership mapping, and header-based tenant extraction.

**Result:** 30 passed, 0 failed, 0 errors.

---

## Authentication & Architecture Contracts
For detailed architectural flows, token contracts, and RBAC specifications:
- [Gateway Authentication Flow](../../docs/architecture/gateway-auth-flow.md)
- [JWT Authentication Flow & Claims Contract](../../docs/architecture/jwt-auth-flow.md)
- [RBAC Architecture & Roles Model](../../docs/architecture/rbac-architecture.md)
- [Authentication Setup & Verification Guide](../../docs/setup/authentication-setup-guide.md)


Squad 4 — Policy Service | CyArt Tech LLP | AEV Platform (Pod Alpha)

Utkarsh Pratham (Squad Lead) | Narayanan Varadarajan & Pratik (Squad Members)
Branch: `feature/policy-week4-tenant-context-pratik` | Tenant & Scope Authorization (Issue #93)