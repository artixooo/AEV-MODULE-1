Policy Service — Pod Alpha (Squad 4)

Authorization Service — RBAC Foundation

Squad Lead: Utkarsh Pratham | Squad Member: Narayanan Varadarajan | Port: 8002

Scope

This service is being built up in stages, tracked by separate issues:

| Stage | Issue | Scope |
|:---|:---:|:---|
| ✅ Project setup & DB prep | #5 | Week 1 — project structure, Docker, migrations |
| ✅ **Infrastructure readiness** | **#17** | **Week 2 — config, DB connectivity, health checks, graceful shutdown (this PR)** |
| 🔜 RBAC foundation | #61 | Week 3 — Role/Permission models, policy evaluation service, Policy APIs (no ABAC) |

This PR covers **#17 only** — infrastructure readiness. RBAC, ABAC, Segregation of Duties, and permission caching are **not** implemented here; they're picked up in the linked follow-up issues.

---

## ⚙️ Project Structure

```
services/policy/
│
├── Dockerfile                     Production image (python:3.12-slim)
├── requirements.txt               Python deps (fastapi, sqlalchemy, redis…)
├── .env.example                   Fully-documented env variable template
│
├── app/
│   ├── main.py                    FastAPI app + lifespan startup/graceful shutdown
│   │
│   ├── core/
│   │   ├── config.py              Pydantic Settings — env var loader
│   │   ├── database.py            SQLAlchemy engine + session factory
│   │   │                          (Postgres, with dev-only SQLite fallback)
│   │   └── guid.py                Portable UUID column type
│   │
│   ├── models/
│   │   └── policy_models.py       ORM: Role, Permission, Policy, SoDPolicy
│   │                              (schema prep only — no business logic yet)
│   │
│   └── routers/
│       └── health_router.py       GET /health  ·  GET /ready
│
└── tests/
    └── test_policy_service.py     Boot, health, and readiness tests
```

> [!NOTE]
> `app/api/`, `app/schemas/`, `app/services/`, `app/middleware/`, and `app/utils/` exist as empty scaffold folders (matching Identity/Organization's structure) — they'll be filled in as RBAC/ABAC work lands in future issues.

The Policy Service will become the centralized authorization authority for the AEV Platform. **This PR covers only Week 1**: project setup and authorization database preparation. Authorization *logic* is Week 2 work and is tracked separately.

## 🔧 Environment Variables

| Variable | Default | Description |
|:---|:---|:---|
| `APP_NAME` | `policy-service` | Service identifier |
| `APP_ENV` | `development` | `development` \| `staging` \| `production` |
| `PORT` | `8002` | HTTP port |
| `HOST` | `0.0.0.0` | Bind interface |
| `DATABASE_URL` | *(see `.env.example`)* | PostgreSQL connection string — set via environment variable, never hardcoded |
| `REDIS_URL` | `redis://localhost:6379` | Reserved for future caching (not used yet) |
| `IDENTITY_SERVICE_URL` | `http://localhost:8000` | Upstream Identity Service |
| `ORGANIZATION_SERVICE_URL` | `http://localhost:8001` | Upstream Organization Service |
| `POLICY_CACHE_TTL` | `300` | Reserved for future caching (not used yet) |
| `ENABLE_SOD_ENFORCEMENT` | `true` | Reserved for future SoD logic (not used yet) |

Config loads via `pydantic-settings`, reading from environment variables and/or a local `.env` file. Verified locally: real environment variables correctly override the documented defaults.

> [!IMPORTANT]
> The connection strings shown in this document (e.g. `postgres:postgres@localhost`) are the **local development defaults only**, matching `docker-compose.yml`'s local Postgres container. Never reuse these values in staging/production — set `DATABASE_URL` via a real secret/environment variable there.

---

## 🗄️ Database & Migration Framework

Schema is owned exclusively by SQL migration files — **not** by the application at runtime:

```
database/policy/migrations/
├── 001_create_roles.sql
├── 002_create_permissions.sql
├── 003_create_role_permissions.sql
├── 004_create_policies.sql
└── 005_create_sod_policies.sql
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

ABAC is explicitly out of scope for this issue, as is Segregation of Duties enforcement and decision caching.

A note on authentication vs. authorization

Identity Service issues JWTs containing only a sub (the user's email) and exp claim — no role. Neither Identity nor Organization Service currently expose a way to look up a user's role. A documented target contract exists (Gateway team's authentication-contract.md, branch week-3-gateway-auth) specifying that Identity should eventually issue tenant_id, roles, and permissions claims, but that work has not landed yet, and Gateway's own JWT-validation middleware is also still unmerged.

Because of this, POST /evaluate takes role_code as an explicit request parameter rather than deriving it from the token, and is additionally restricted to trusted internal callers via a shared X-Service-API-Key header (see app/middleware/service_auth_middleware.py) — an authenticated end-user JWT alone is not sufficient to call it. This prevents any authenticated user from querying "do I have role X's permissions" for an arbitrary X. Once Identity issues a trustworthy role claim, this endpoint should be revisited to derive role_code from the token directly instead.

API Reference (v1)
Method	Endpoint	Auth	Description
GET	/api/v1/policy/roles	Bearer	List all active roles
GET	/api/v1/policy/permissions	Bearer	List all permissions
POST    /api/v1/policy/evaluate Bearer + X-Service-API-Key  RBAC check: does role_code have permission_code? (internal service use only)

reason is one of: role_has_permission, role_missing_permission, role_not_found, permission_not_found — the last two return DENY, not an error.

Full interactive docs (Swagger UI) are available at /docs once the service is running.

Project Structure

services/policy/ contains: Dockerfile, requirements.txt, .env.example, an app/ folder with main.py plus core/, models/, repositories/, services/, middleware/, schemas/, and routers/ subfolders, and a tests/ folder with test_policy_service.py, test_rbac_evaluation.py, and test_policy_api.py.

app/api/ and app/utils/ exist as empty scaffold folders (matching Identity/Organization's structure) — they'll be filled in as future work lands.

Environment Variables
Variable	Default	Description
APP_NAME	policy-service	Service identifier
APP_ENV	development	development / staging / production
PORT	8002	HTTP port
HOST	0.0.0.0	Bind interface
DATABASE_URL	see .env.example	PostgreSQL connection string
REDIS_URL	redis://localhost:6379	Reserved for future caching
IDENTITY_SERVICE_URL	http://localhost:8000	Upstream Identity Service
ORGANIZATION_SERVICE_URL	http://localhost:8001	Upstream Organization Service
POLICY_CACHE_TTL	300	Reserved for future caching
ENABLE_SOD_ENFORCEMENT	true	Reserved for future SoD logic
JWT_SECRET_KEY	change-me	Shared secret for validating JWTs from Identity Service
JWT_ALGORITHM	HS256	Signing algorithm — must match Identity Service
SERVICE_API_KEY | change-me | Shared secret for trusted internal service-to-service calls (required on POST /evaluate)

Config loads via pydantic-settings, reading from environment variables and/or a local .env file.

The connection strings shown above are local development defaults only, matching docker-compose.yml's local Postgres container. Never reuse these values in staging/production.

Database & Migration Framework

Schema is owned exclusively by SQL migration files, not by the application at runtime: database/policy/migrations/ contains 001_create_roles.sql, 002_create_permissions.sql, 003_create_role_permissions.sql, 004_create_policies.sql, and 005_create_sod_policies.sql.

Applied via the shared migration runner: ./database/scripts/migrate.sh

The ORM models in app/models/policy_models.py mirror this schema exactly.

Quickstart

pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

Docker

docker build -t policy-service-test .
docker compose up -d postgres
docker compose up --build --no-deps policy

Verified locally: image builds cleanly, container starts, GET /ready reports database connected over the Docker network.

Health Endpoints
Method	Endpoint	Description
GET	/	Service discovery
GET	/health	Liveness check
GET	/ready	Readiness check (503 on DB failure)
Graceful Shutdown

The FastAPI app uses a lifespan context manager that verifies the database connection on startup and disposes the connection pool cleanly on shutdown. Verified locally via docker compose down.

Testing

pytest tests/ -v

16 tests: 3 service-level (root/health/readiness), 4 RBAC evaluation-logic tests, 9 full API-layer tests covering auth enforcement, service-credential enforcement, and real ALLOW/DENY decisions.

Result: 16 passed, 0 failed, 0 errors.

Squad 4 — Policy Service | CyArt Tech LLP | AEV Platform (Pod Alpha)

Utkarsh Pratham (Squad Lead) | Narayanan Varadarajan (Squad Member)
Branch: week3-policy-rbac | RBAC Foundation (Issue #61)