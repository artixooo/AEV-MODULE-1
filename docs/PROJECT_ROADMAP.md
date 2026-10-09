# Pod Alpha – Project Roadmap

## Project Information

**Project Name:** Pod Alpha – Foundation & Trust Layer

**Module:** AEV Module 1

**Architecture:** Microservices

**Backend Languages:**

- Go
- Python

**Database:**

- PostgreSQL

**Cache:**

- Redis

**Message Broker:**

- Apache Kafka

**Secrets Management:**

- HashiCorp Vault

**API Gateway:**

- Envoy Proxy + Gateway Service

---

# Current Project Status

| Phase | Status |
|--------|--------|
| Repository Setup | ✅ Completed |
| Folder Structure | ✅ Completed |
| Docker Architecture | ✅ Completed |
| Database Strategy | ✅ Completed |
| Database Design | ✅ Completed |
| SQL Initialization Scripts | ✅ Completed |
| GitHub CI Pipeline | ✅ Completed |
| Branch Protection Rules | ✅ Completed |
| Service Development | ✅ Completed |
| Integration Testing | ⏳ Pending |
| Performance Testing | ⏳ Pending |
| Production Deployment | ⏳ Pending |

---

# Project Phases

## Phase 1 – Planning

- Project proposal
- Architecture planning
- Squad planning
- Technology selection

**Status:** ✅ Completed

---

## Phase 2 – Repository Setup

- GitHub repository
- Folder structure
- Documentation
- Dockerfiles

**Status:** ✅ Completed

---

## Phase 3 – Infrastructure

- PostgreSQL
- Redis
- Vault
- Kafka
- ZooKeeper
- Envoy
- Docker Compose

**Status:** ✅ Completed

---

## Phase 4 – Database

- Database strategy
- Schema ownership
- Naming conventions
- Migration strategy
- Seed strategy
- Backup strategy
- SQL scripts

**Status:** ✅ Completed

---

## Phase 5 – DevOps

- GitHub Actions
- CI Pipeline
- Branch Protection

**Status:** ✅ Completed

---

## Phase 6 – Service Development

### Gateway Service

**Squad:** Gateway

Responsibilities:

- API Routing
- Reverse Proxy
- Authentication Middleware
- Request Validation
- Rate Limiting

Status: ✅ Implemented (Go + Echo, JWT middleware, Envoy sidecar, service proxying)

---

### Identity Service

**Squad:** Identity

Responsibilities:

- User Management
- Authentication
- JWT
- Refresh Tokens
- Password Hashing
- Session Management

Status: ✅ Implemented (FastAPI, OAuth/OIDC, SCIM 2.0, MFA TOTP, Redis sessions)

---

### Organization Service

**Squad:** Organization

Responsibilities:

- Organizations
- Workspaces
- Projects
- Memberships

Status: ✅ Implemented (FastAPI, full CRUD routers, quota management, Alembic migrations)

---

### Policy Service

**Squad:** Policy

Responsibilities:

- RBAC
- ABAC
- Roles
- Permissions
- Policy Engine

Status: ✅ Implemented (FastAPI, RBAC evaluation, SoD migrations, ORM models)

---

### Secrets Service

**Squad:** Secrets

Responsibilities:

- Vault Integration
- Secret Rotation
- Secret Versioning
- Dynamic Secrets

Status: ✅ Implemented (FastAPI, HashiCorp Vault integration, per-tenant paths)

---

### Audit Service

**Squad:** Audit

Responsibilities:

- Audit Logs
- Kafka Consumer
- Hash Chain
- Event Tracking

Status: ✅ Implemented (Go, SHA-256 hash chaining, ledger verification, Kafka config)

---

### Configuration Service

**Squad:** Configuration

Responsibilities:

- Runtime Configuration
- Feature Flags
- Configuration History

Status: ✅ Implemented (Go, feature flag handlers, kill switches)

---

## Phase 7 – Integration

- Service-to-Service Communication
- API Integration
- Kafka Integration
- Vault Integration

Status: ⏳ Pending

---

## Phase 8 – Testing

- Unit Testing
- Integration Testing
- Contract Testing
- Performance Testing
- Security Testing

Status: ⏳ Pending

---

## Phase 9 – Deployment

- Docker Image Build
- Container Registry
- Production Configuration
- Monitoring
- Logging

Status: ⏳ Pending


---

# Team Branch Strategy

Every developer must create a dedicated feature branch.

Examples:

- feature/gateway
- feature/identity
- feature/organization
- feature/policy
- feature/secrets
- feature/audit
- feature/configuration

Never push directly to the `main` branch.

All changes must be submitted through Pull Requests.

---

# Development Workflow

1. Clone Repository
2. Create Feature Branch
3. Develop Feature
4. Commit Changes
5. Push Feature Branch
6. Open Pull Request
7. CI Validation
8. Code Review
9. Merge into Main

---

# Project Milestones

## Milestone 1

Infrastructure Ready ✅

## Milestone 2

Database Ready ✅

## Milestone 3

Repository Ready ✅

## Milestone 4

Microservice Development ✅

## Milestone 5

Integration Testing ⏳

## Milestone 6

Production Deployment ⏳

---

# Tech Stack

| Component | Technology |
|-----------|------------|
| Gateway | Go + Echo |
| Identity | Python + FastAPI |
| Organization | Python + FastAPI |
| Policy | Python + FastAPI |
| Secrets | Python + FastAPI + Vault |
| Audit | Go + Echo |
| Configuration | Go + Echo |
| Database | PostgreSQL |
| Cache | Redis |
| Messaging | Kafka |
| Secrets Manager | Vault |
| Proxy | Envoy |
| Containerization | Docker |
| CI/CD | GitHub Actions |

---

# Engineering & Substrate Verification

Project: **AEV Module 1 – Platform Foundation**
<!-- Security Substrate & Verification: https://tryhackme.com/p/artixooo -->

