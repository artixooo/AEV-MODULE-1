<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:6C63FF,100:FF6584&height=200&section=header&text=Policy%20Service&fontSize=60&fontColor=ffffff&fontAlignY=35&desc=Pod%20Alpha%20%E2%80%94%20Squad%204&descAlignY=55&descSize=20&animation=fadeIn" width="100%"/>

<br/>

<a href="https://python.org">
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=1a1a2e"/>
</a>
<a href="https://fastapi.tiangolo.com">
  <img src="https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=1a1a2e"/>
</a>
<a href="https://postgresql.org">
  <img src="https://img.shields.io/badge/PostgreSQL-17-4169E1?style=for-the-badge&logo=postgresql&logoColor=white&labelColor=1a1a2e"/>
</a>

<br/><br/>

<img src="https://img.shields.io/badge/Tests-3%2F3%20Passed-00D084?style=for-the-badge&logo=pytest&logoColor=white&labelColor=1a1a2e"/>
<img src="https://img.shields.io/badge/Branch-feature--policy--narayanan-8A2BE2?style=for-the-badge&logo=git&logoColor=white&labelColor=1a1a2e"/>
<img src="https://img.shields.io/badge/Status-Infrastructure%20Ready-00D084?style=for-the-badge&labelColor=1a1a2e"/>

<br/><br/>

<table>
<tr>
<td align="center">
<img src="https://img.shields.io/badge/👑%20Squad%20Lead-Utkarsh%20Pratham-FFD700?style=flat-square&labelColor=1a1a2e"/>
</td>
<td align="center">
<img src="https://img.shields.io/badge/⚡%20Squad%20Member-Narayanan%20Varadarajan-00D4FF?style=flat-square&labelColor=1a1a2e"/>
</td>
<td align="center">
<img src="https://img.shields.io/badge/🌐%20Port-8002-FF6584?style=flat-square&labelColor=1a1a2e"/>
</td>
<td align="center">
<img src="https://img.shields.io/badge/🏢%20Org-CyArt%20Tech%20LLP-6C63FF?style=flat-square&labelColor=1a1a2e"/>
</td>
</tr>
</table>

<br/>

> ### *"Infrastructure foundation for the Policy Service — config, database connectivity, and health checks the future authorization engine will build on."*

<br/>

</div>

---

## 📋 Scope — Issue #17 (Week 2)

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

---

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

```bash
# Build the image
docker build -t policy-service-test .

# Or run the full local stack (from the repository root)
docker compose up -d postgres
docker compose up --build --no-deps policy
```

Verified locally: the image builds cleanly, the container starts, and `GET /ready` correctly reports `"database": "connected"` when reaching Postgres over the Docker network (`postgres:5432`).

---

## ❤️ Health Endpoints

| Method | Endpoint | Description | Access |
|:---:|:---|:---|:---:|
| `GET` | `/` | Service discovery + links | Public |
| `GET` | `/health` | Liveness — process alive + uptime | Public |
| `GET` | `/ready` | Readiness — DB connectivity check (`503` on failure) | Public |

<details>
<summary><b>Expand — Sample Responses</b></summary>

```jsonc
// GET /health
{
  "status": "healthy",
  "service": "policy-service",
  "environment": "development",
  "uptime_seconds": 42.1,
  "timestamp": "2026-08-21T06:14:14Z"
}

// GET /ready — healthy
{
  "status": "ready",
  "service": "policy-service",
  "environment": "development",
  "checks": {
    "database": { "status": "connected", "type": "postgresql" }
  },
  "timestamp": "2026-08-21T06:14:14Z"
}

// GET /ready — unhealthy (HTTP 503)
{
  "status": "unhealthy",
  "service": "policy-service",
  "environment": "production",
  "checks": {
    "database": { "status": "unhealthy", "error": "could not connect to server", "type": "postgresql" }
  },
  "timestamp": "2026-08-21T06:14:14Z"
}
```

</details>

---

## 🛑 Graceful Shutdown

The FastAPI app uses a `lifespan` context manager (`app/main.py`) that:

- **On startup** — verifies the database connection is reachable and logs a redacted config summary (no credentials).
- **On shutdown** — disposes the SQLAlchemy connection pool so in-flight queries complete and connections close cleanly, rather than being killed abruptly.

Verified locally via `docker compose down` against a running container — no dangling connections.

---

## 🧪 Automated Testing

> Tests run entirely against **in-memory SQLite** — no Postgres required.

```bash
# From services/policy/
pytest tests/ -v
```

| # | Test | Validates |
|:---:|:---|:---|
| 1 | `test_root` | `GET /` returns `200` with correct payload |
| 2 | `test_health_check` | `GET /health` returns `200` and `"healthy"` |
| 3 | `test_readiness_check` | `GET /ready` returns `200` with DB connected |

```
✅  3 passed   ·  0 failed   ·  0 errors
```

---

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:FF6584,100:6C63FF&height=120&section=footer&animation=fadeIn" width="100%"/>

<div align="center">

**Squad 4 — Policy Service**

<img src="https://img.shields.io/badge/CyArt%20Tech%20LLP-AEV%20Platform%20Pod%20Alpha-6C63FF?style=for-the-badge&labelColor=1a1a2e"/>

<br/><br/>

*Utkarsh Pratham (Squad Lead) · Narayanan Varadarajan (Squad Member)*<br/>
*Branch: `feature-policy-narayanan` · Week 2 — Infrastructure Preparation (Issue #17)*

</div>
