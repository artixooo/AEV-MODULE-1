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

## Future Work
- Repository layer for reading/writing configuration data (`configuration_db`)
- Database migrations for the 5 owned tables
- Cache layer to reduce database load on repeated reads
- Wire the watcher module to detect real configuration changes once the repository layer exists
- Expose `/config` (GET/PUT) and `/feature-flags` HTTP handlers
- Unit tests covering repository and cache logic