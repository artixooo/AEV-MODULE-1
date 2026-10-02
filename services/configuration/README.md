# Configuration Service

## Purpose

Centralized service for managing application configuration, feature flags, and tenant-specific settings.

---

## Team Ownership

**Squad:** Squad 7

**Lead:** Bhukailash Pilli

**Members:**

- Harshit Prajapat

---

## Responsibilities

- Feature Flags
- Runtime Configuration
- Tenant Configuration
- Environment Settings
- Configuration Distribution

---

# Configuration Service — Week 3

services/configuration/
├── cmd/
│   └── server/
│       └── main.go          # Application entry point & server bootstrap
├── configs/                 # Configuration files & presets
├── docs/                    # Architecture & API documentation
├── internal/
│   ├── cache/               # In-memory caching logic & TTL janitor
│   ├── config/              # Service configuration & environment loading
│   ├── db/                  # Database connection pool & client setup
│   ├── handlers/            # HTTP transport handlers & routing
│   ├── models/              # Internal domain entities & database models
│   ├── repository/          # PostgreSQL database access layer & queries
│   ├── services/            # Business logic & orchestration layer
│   └── watcher/             # Real-time config change listeners & watchers
├── pkg/                     # Exported reusable packages
├── tests/                   # Integration test suites
├── .dockerignore            # Docker ignore definitions
├── .env.example             # Example environment variables template
├── Dockerfile               # Container build definition
├── go.mod                   # Go module dependencies
├── go.sum                   # Go checksum file
└── README.md                # Service documentation

*(No `migrations/` folder here by design — the approved schema's SQL lives centrally at `database/configuration/migrations/` at the repo root. This service connects to whatever schema already exists there; it never creates or alters tables.)*

---

## APIs
| Method | Endpoint       | Description          |
|--------|----------------|----------------------|
| GET    | /config        | Get Configuration    |
| PUT    | /config        | Update Configuration |
| GET    | /feature-flags | List Feature Flags   |
| GET    | /health        | Health check         |

*(Note: only `/health` is currently implemented. The others are planned — see Future Work.)*

---

## Docker
Build the image:

docker build -t configuration-service .


Run the container:

docker run -p 8083:8083 configuration-service


Override the port at runtime if needed:

docker run -p 9090:9090 -e PORT=9090 configuration-service


*(Internal port 8083
, exposed on host port 8087 — matching the project's root `docker-compose.yml`.)*

---

## Database
**Type:** PostgreSQL
**Shared database:** `pod_alpha` (see project root `docker-compose.yml`)

**Approved schema (3 tables, defined centrally at `database/configuration/migrations/`):**
- `configuration` — generic key/value config, scoped by `organization_id` / `workspace_id` / `project_id`
- `feature_flags` — same scoping model, includes rollout percentage
- `configuration_history` — audit trail; a row is written every time `configuration` is inserted or updated

This service connects to `pod_alpha` — it does not create or alter tables. Access to these tables is only through this service's API.

---

## Environment Variables
| Variable             | Default | Description                                                       |
|-----------------------|---------|---------------------------------------------------------------------|
| PORT                  | 8083    | Port the HTTP server listens on                                     |
| AUTH_ENABLED          | false   | Whether authentication is enforced for this environment             |
| IDENTITY_SERVICE_URL  | (empty) | URL of the Identity Service, for auth-related lookups                |
| JWT_ALGORITHM         | HS256   | JWT signing algorithm used across the system                         |
| JWT_EXPIRATION        | 3600    | JWT token expiration, in seconds                                      |
| DATABASE_URL          | —       | PostgreSQL connection string for the shared `pod_alpha` database      |

See `.env.example` for the full list.

---

## Dependencies
- Identity Service
- Organization Service
- `github.com/jackc/pgx/v5` (PostgreSQL driver)

---

## Technology
- Go
- PostgreSQL

---

## Future Work
- Expose `/config` (GET/PUT) and `/feature-flags` HTTP handlers (currently only `/health` is wired up)
- Wire the watcher module to trigger cache invalidation on real configuration changes
- Integration with Identity Service for request authentication
- Integration with Organization Service for tenant/org scoping validation
- CI test harness for repository layer against a real Postgres instance (e.g. testcontainers-go)
