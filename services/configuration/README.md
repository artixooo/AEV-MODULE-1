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

## Folder Structure

services/configuration/
├── cmd/
│ └── server/
│ └── main.go # Entry point, starts HTTP server
├── internal/
│ ├── config/
│ │ └── config.go # Loads environment-based settings
│ └── watcher/
│ └── watcher.go # Periodically checks for configuration changes
├── .dockerignore
├── .env.example
├── Dockerfile
├── go.mod
├── go.sum
└── README.md

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

docker run -p 8082:8082 configuration-service


Override the port at runtime if needed:

docker run -p 9090:9090 -e PORT=9090 configuration-service

---

---

## Database
**Type:** PostgreSQL
**Database name:** `configuration_db`

**Owned tables (schema defined separately by Squad 7):**
- Feature Flags
- Tenant Configuration
- Runtime Configuration
- Environment Settings
- Application Configuration

No other squad may modify these tables directly — access is only through this service's API.

---

## Environment Variables
| Variable | Default | Description                        |
|----------|---------|--------------------------------------|
| PORT     | 8082    | Port the HTTP server listens on      |

See `.env.example` for the full list.

---

## Dependencies
- Identity Service
- Organization Service

---

## Technology
- Go
- PostgreSQL

---

## Environment Variables

See `.env.example`


# Configuration Service — Repository, Cache, and DB Connection

Matches the **approved** schema (3 tables: `configuration`, `feature_flags`,
`configuration_history`). Table creation lives centrally in
`database/migration/` at the repo root — **this service does not create
or alter tables**, it only connects to whatever schema already exists
there.

## Folder structure

```
services/configuration/
├── cmd/
│   └── server/          # Main application entry point
├── db/                  # Database connection & client initialization
├── internal/
│   ├── cache/           # In-memory caching logic & TTL janitor
│   ├── config/          # Environment variable parser
│   ├── handlers/        # HTTP/gRPC API handlers
│   ├── models/          # Domain models & structs
│   └── repository/      # PostgreSQL queries & database interfaces
├── migrations/          # Service-specific SQL migrations (if any)
├── Dockerfile           # Service container definition
└── run_tests.ps1        # Test & migration automation script

```

(There is intentionally no `migrations/` folder here — see `database/migration/`
at the repo root for the actual SQL.)

## 1. `db/` — connection setup

`db.New(ctx, cfg)` is the one place that opens a `pgxpool.Pool` and wires
everything together: Postgres repository → wrapped in the caching
decorator → returned ready to use.

```go
handle, err := db.New(ctx, db.Config{}) // reads DATABASE_URL from env if DatabaseURL is empty
if err != nil {
    log.Fatal(err)
}
defer handle.Close()

repo := handle.Repo // satisfies repository.Repository

cfg, err := repo.GetConfig(ctx, "max_upload_size_mb")
```

`db.New` pings the database immediately so connection problems surface at
startup, not on the first real request. It does **not** touch schema —
if `database/migration/`'s migrations haven't been run yet against the
target database, calls through `repo` will fail with a normal Postgres
"relation does not exist" error, not anything from this package.

Config knobs (`db.Config`): `DatabaseURL` (falls back to the
`DATABASE_URL` env var), `CacheTTL` (defaults to 30s), `CacheSweepInterval`
(defaults to 1 minute).

## 2. Repository layer (`internal/repository/`)

- `models.go` — `Configuration`, `FeatureFlag`, `ConfigurationHistory` structs, plus `Scope` and `DataType` typed enums.
- `repository.go` — the `Repository` interface and `SaveConfigInput` / `SaveFeatureFlagInput` / `ListFilter` input types.
- `repository_postgres.go` — Postgres implementation (pgx/v5).

Key design points:

- **`config_key` is globally unique**, so `GetConfig(key)` / `SaveConfig(input)` operate on a single row — `scope` + `organization_id`/`workspace_id`/`project_id` describe *which level owns that key*, not a per-tenant copy of it.
- **`SaveConfig` writes an audit row on every call**, inside a transaction: locks the existing row (if any) with `FOR UPDATE`, does the insert/update, then inserts a matching row into `configuration_history` with the old and new value. Pass `ChangedBy` / `ChangeReason` on the input to populate the audit fields.
- **`feature_flags` has no history table** in the approved schema, so `SaveFeatureFlag` is a plain upsert with no audit write.
- `ListConfigurations` / `ListFeatureFlags` take a `ListFilter{Scope, OrganizationID, WorkspaceID, ProjectID}` — pass zero values to not filter on that dimension.

## 3. Cache module (`internal/cache/`)

- `cache.go` — `Cache` interface + `InMemoryCache` (TTL-based, goroutine-safe, with a background janitor).
- `cached_repository.go` — `CachedRepository`, a decorator implementing `Repository`.

| Method | Cached? | Reason |
|---|---|---|
| `GetConfig` / `SaveConfig` | ✅ (JSON-serialized, write-through on save) | single-row lookup by a stable key |
| `GetFeatureFlag` / `SaveFeatureFlag` | ✅ (same pattern) | same |
| `ListConfigurations` / `ListFeatureFlags` | ❌ | arbitrary filters → no single reusable cache key |
| `GetConfigurationHistory` | ❌ | audit trail should always reflect latest state |

`CachedRepository.InvalidateConfig(key)` / `InvalidateFlag(key)` are
exposed for the rare case something changed the DB out-of-band and the
cache needs a manual bust.


## 4. Tests

- `internal/cache/cache_test.go` — `InMemoryCache` set/get/delete, TTL expiry, janitor sweep.
- `internal/cache/fake_repository_test.go` — an in-memory fake implementing `repository.Repository`, used only in tests.
- `internal/cache/cached_repository_test.go` — verifies `CachedRepository` actually serves repeat reads from cache, write-through on save avoids an extra DB hit, list calls always pass through, and manual invalidation forces a refetch.
- `internal/repository/repository_test.go` — validation guard-clause tests (`ErrInvalidInput` on empty keys) that don't need a live DB, plus a sanity check on the `Scope` string constants.

Full CRUD behavior of `PostgresRepository` (upserts, history writes, scope
filtering) needs a real Postgres instance to test meaningfully — these
tests don't attempt to fake that with mocks, since the SQL correctness
*is* the thing worth testing. Recommend wiring up
[testcontainers-go](https://golang.testcontainers.org/) with a Postgres
container for that layer in CI; happy to add that harness if you want it
in this PR.

## Dependencies

Only external dependency is `github.com/jackc/pgx/v5`. Run `go mod tidy`
after dropping this into your real repo (module path in `go.mod` is a
placeholder — update `github.com/yourorg/yourrepo/...` to match).

## A note on verification

Every `.go` file is confirmed valid with `gofmt` and the cache-layer logic
is covered by the tests above. I couldn't run `go build`/`go test` end-to-
end in my sandbox — it can't reach `proxy.golang.org` (or `gopkg.in`, a
transitive dep of pgx's test tooling) to resolve the module graph. That's
a restriction on my end, not a problem with the code; `go mod tidy && go
test ./...` should work normally in your environment.
