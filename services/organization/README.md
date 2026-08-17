# Organization Service

## Purpose

The **Organization Service** is a core microservice in Pod Alpha (AEV Module 1) responsible for managing organizations, workspaces, projects, and memberships.

## Current Status

**Week 1 — Project Preparation & Verification**

Week 1 establishes the Organization Service foundation. Business functionality and CRUD implementation are deferred to subsequent weeks.

---

## Week 1 Verification

The following Week 1 project preparation items were established and verified:

- [x] FastAPI application structure established
- [x] Database layer and SQLAlchemy Declarative Base configured
- [x] Service-level Alembic environment connected to model metadata
- [x] Centralized Organization migrations verified under `database/organization/migrations/`
- [x] Approved Organization migration files identified
- [x] Organization SQLAlchemy model created
- [x] Pydantic schemas created
- [x] Organization router skeleton registered
- [x] Organization service-layer skeleton created
- [x] Health endpoints (`/`, `/health`, `/ready`) prepared
- [x] Unit test suite verified
- [x] Dockerfile verified
- [x] Documentation updated

### Test Verification

The Week 1 test suite was executed locally:

```text
Command: python -m pytest
Result: 10 passed, 0 failed
Execution time: 7.99 seconds
```

---

## Architecture & Directory Structure

```text
services/organization/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entrypoint
│   │
│   ├── api/                     # API/system endpoints
│   │   ├── __init__.py
│   │   └── health.py            # Health and readiness endpoints
│   │
│   ├── core/                    # Core configuration and logging
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── db/                      # Database engine and session setup
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   ├── models/                  # SQLAlchemy domain models
│   │   ├── __init__.py
│   │   └── organization.py
│   │
│   ├── routers/                 # FastAPI routers
│   │   ├── __init__.py
│   │   └── organization.py
│   │
│   ├── schemas/                 # Pydantic validation schemas
│   │   ├── __init__.py
│   │   └── organization.py
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   └── organization.py
│   │
│   └── utils/                   # Helper functions
│       └── __init__.py
│
├── migrations/                  # Service-level Alembic environment
│   ├── env.py
│   └── versions/
│
├── tests/                       # Service test suite
│   ├── __init__.py
│   ├── test_imports.py
│   ├── test_health.py
│   ├── test_config.py
│   ├── test_db.py
│   └── test_models_schemas.py
│
├── Dockerfile                   # Containerization definition
├── alembic.ini                  # Alembic configuration
├── requirements.txt             # Python dependencies
└── README.md                    # Service documentation
```

---

# Week 2 — Infrastructure Verification

Week 2 focused on verifying the Organization Service infrastructure, PostgreSQL integration, database schema, service health, Docker networking, graceful shutdown, and logging.

## Week 2 Verification

The following Week 2 infrastructure items were verified:

- [x] PostgreSQL connection verified
- [x] Organization database initialized
- [x] Organization database migrations executed
- [x] Organization database schema verified
- [x] `/health` endpoint verified
- [x] `/ready` endpoint verified with database connectivity
- [x] Docker networking verified
- [x] Graceful shutdown verified
- [x] Logging configuration verified

---

## Database Verification

The Organization Service successfully connected to PostgreSQL using:

```text
postgresql://postgres:postgres@postgres:5432/pod_alpha
```

The following Organization tables were created and verified:

```text
organizations
workspaces
projects
memberships
```

### Organization Migrations

The approved centralized migration location is:

```text
database/organization/migrations/
```

Migration files:

```text
001_create_organizations.sql
002_create_workspaces.sql
003_create_projects.sql
004_create_memberships.sql
```

---

## Health Verification

The Organization Service health endpoint was verified successfully:

```text
GET /health
```

**HTTP 200**

Response:

```json
{
  "status": "healthy",
  "service": "organization-service"
}
```

---

## Readiness Verification

The Organization Service readiness endpoint was verified successfully:

```text
GET /ready
```

**HTTP 200**

Response:

```json
{
  "status": "ready",
  "database": "connected"
}
```

This confirms that the Organization Service can successfully connect to PostgreSQL.

---

## Docker Networking

The Organization container successfully resolved the PostgreSQL container through Docker DNS:

```text
postgres → 172.18.0.8
```

This verifies container-to-container DNS connectivity.

---

## Graceful Shutdown

The Organization Service was started independently and stopped using Docker.

The container exited successfully:

```text
ExitCode=0
```

The service logs confirmed:

```text
Shutting down
Waiting for application shutdown.
Organization Service stopped
Application shutdown complete.
Finished server process
```

This verifies that the Organization Service performs a clean application shutdown.

---

## Logging Verification

The Organization Service uses Python's standard `logging` module.

Configuration:

```text
Log Level: INFO
Logger: organization-service
Format: %(asctime)s | %(levelname)s | %(message)s
```

Startup and shutdown lifecycle events were successfully recorded in the service logs.

---

## Testing

The Organization Service test suite was verified during Week 1:

```text
Command: python -m pytest
Result: 10 passed, 0 failed
```

---

## Current Scope

Week 2 focuses on infrastructure verification:

- PostgreSQL connectivity
- Database initialization
- Database migrations
- Database schema verification
- Health endpoint
- Readiness endpoint
- Docker networking
- Graceful shutdown
- Logging

Business functionality and CRUD implementation are deferred to subsequent weeks.

> [!NOTE]
> The Organization Service was independently verified using `docker compose up -d organization --no-deps`. The full Docker Compose startup chain currently has a separate Identity Service dependency issue.