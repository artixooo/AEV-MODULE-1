# Configuration Service

## Purpose

Centralized service for managing application configuration, feature flags, and tenant-specific settings.

---

## Team Ownership

**Squad:** Squad 7

**Lead:** Bhukailash Pilli

**Members:**

- Future Member (To Be Assigned)

---

## Responsibilities

- Feature Flags
- Runtime Configuration
- Tenant Configuration
- Environment Settings
- Configuration Distribution

---

## APIs

| Method | Endpoint       | Description          |
|--------|----------------|----------------------|
| GET    | /config        | Get Configuration    |
| PUT    | /config        | Update Configuration |
| GET    | /feature-flags | List Feature Flags   |

---

## Database

PostgreSQL

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
