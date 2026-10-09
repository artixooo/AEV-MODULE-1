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

# Configuration Service — Week 4

services/configuration/
├── cmd/
│ ├── server/
│ │ └── main.go # Entry point, starts HTTP server
│ └── checkconn/
│ └── main_db.go # Standalone DB connectivity smoke test
├── internal/
│ ├── config/
│ │ ├── config.go # Loads environment-based settings
│ │ └── config_test.go
│ ├── watcher/
│ │ └── watcher.go # Periodically checks for configuration changes
│ ├── db/
│ │ ├── connection.go # Opens the DB pool, wires repository + cache together
│ │ └── connection_test.go
│ ├── cache/
│ │ ├── cache.go # TTL-based in-memory cache
│ │ └── cached_repository.go # Cache-wrapped decorator over the repository
│ ├── repository/
│ │ ├── models.go # Configuration, FeatureFlag, ConfigurationHistory structs
│ │ ├── repository.go # Repository interface + input types
│ │ └── repository_postgres.go # Postgres implementation
│ ├── validation/
│ │ └── sensitive.go # Sensitive-field detection (Week 4)
│ └── idpconfig/
│ ├── tenant_scope.go # Tenant-scoped config key generation (Week 4)
│ └── service.go # Save/Get identity-provider config (Week 4)
├── docs/
│ ├── openapi.yaml # API contract
│ └── config_identity-provider.md # Identity-provider design spec (Week 4)
├── .dockerignore
├── .env.example
├── Dockerfile
├── go.mod
├── go.sum
└── README.md

There is intentionally no `migrations/` folder here — the approved schema's SQL lives centrally at `database/configuration/migrations/` at the repo root. This service connects to whatever schema already exists there; it never creates or alters tables.

---

## APIs
| Method | Endpoint       | Description          |
|--------|----------------|----------------------|
| GET    | /config        | Get Configuration    |
| PUT    | /config        | Update Configuration |
| GET    | /feature-flags | List Feature Flags   |
| GET    | /organizations/{organizationId}/identity-provider | Get an organization's identity-provider config |
| PUT    | /organizations/{organizationId}/identity-provider | Create or update an organization's identity-provider config |
| GET    | /health        | Health check         |

*(Note: only `/health` is currently implemented as an HTTP route. `/config`, `/feature-flags`, and the identity-provider endpoints are documented in `docs/openapi.yaml` as the target API contract, but their HTTP handlers are not yet wired up — see Future Work. The underlying save/retrieve/validation logic for identity-provider config IS implemented and tested at the Go function level (`internal/idpconfig`), just not yet exposed as an HTTP route.)*

---

## Docker
Build the image:

docker build -t configuration-service .


Run the container:

docker run -p 8083:8083 configuration-service


Override the port at runtime if needed:

docker run -p 9090:9090 -e PORT=9090 configuration-service



When run as part of the full stack via the project's root `docker-compose.yml`, this service is exposed on host port 8087, mapped to internal port 8083 (`8087:8083`).

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

## Identity Provider Configuration (Week 4)

The service supports tenant-scoped identity-provider configuration for the
Identity Service. See `docs/config_identity-provider.md` for the full design
specification.

**Key points:**
- Tenant = `organization_id` (no separate tenant table)
- Generic provider model — supports `oidc`, `oauth2`, `saml`
- Stored using the existing `configuration` table (no new schema), keyed as
  `identity_provider:{organization_id}`
- Sensitive fields (`client_secret`, `api_key`, `private_key`, `password`,
  `signing_key`, `access_token`, `refresh_token`, `scim_token`) are never
  stored directly — only `*_ref` placeholders pointing to Secrets Service
- Full tenant isolation enforced and tested — see
  `internal/idpconfig/service_test.go`

**`ProviderConfig` fields:**

| Field | Applies to | Description |
|---|---|---|
| `type` | All | `oidc`, `oauth2`, or `saml` |
| `enabled` | All | Whether this provider is active |
| `issuer_url` | OIDC | Identity provider's issuer URL |
| `authorization_url` | OIDC, OAuth2 | Authorization endpoint |
| `token_url` | OIDC, OAuth2 | Token endpoint |
| `userinfo_url` | OIDC | Userinfo endpoint |
| `jwks_url` | OIDC | JWKS endpoint |
| `client_id` | OIDC, OAuth2 | Client identifier |
| `client_secret_ref` | OIDC, OAuth2 | Reference to the client secret in Secrets Service |
| `scopes` | OIDC, OAuth2 | Requested scopes |
| `entity_id` | SAML | SAML entity ID |
| `sso_url` | SAML | SSO endpoint |
| `certificate` | SAML | Provider's signing certificate |
| `metadata_url` | SAML | Metadata endpoint (optional) |
| `signing_key_ref` | SAML | Reference to the signing key in Secrets Service |

**Validation:** provider-specific required-field and URL validation
(`internal/idpconfig/provider_validation.go`, adapted from Harshit's
original validation logic) and sensitive-field rejection
(`internal/validation/sensitive.go`) are both applied, in that order,
before persistence in `SaveIdentityProviderConfig`.

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
- Provider-specific validation (OIDC/OAuth2/SAML required-field checks) — in progress