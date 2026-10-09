# AEV Module 1 - Pod Alpha

## Foundation & Trust Layer

Pod Alpha is the **Foundation & Trust Layer** of the AEV Module 1 platform.

It provides the core infrastructure required for secure identity, organization management, policy enforcement, secrets management, auditing, configuration, and API gateway functionality.

The project follows a **microservices architecture**, with each service independently responsible for a specific domain while communicating through well-defined APIs and infrastructure components.

---

# Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Services](#services)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Service Ports](#service-ports)
- [Infrastructure Components](#infrastructure-components)
- [Docker Architecture](#docker-architecture)
- [Database Strategy](#database-strategy)
- [Service Communication](#service-communication)
- [Week 1 Completion](#week-1-completion)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Environment Configuration](#environment-configuration)
- [Starting the Platform](#starting-the-platform)
- [Health Checks](#health-checks)
- [Vault Setup](#vault-setup)
- [Kafka Setup](#kafka-setup)
- [Database](#database)
- [Redis](#redis)
- [Development Workflow](#development-workflow)
- [Branching Strategy](#branching-strategy)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Workflow](#pull-request-workflow)
- [Week 2 Development](#week-2-development)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Team Responsibilities](#team-responsibilities)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

# Project Overview

Pod Alpha establishes the foundational services required by the AEV Module 1 platform.

The platform consists of seven primary microservices:

1. API Gateway
2. Identity Service
3. Organization Service
4. Policy Service
5. Secrets Service
6. Audit Service
7. Configuration Service

The supporting infrastructure includes:

- PostgreSQL
- Redis
- Apache Kafka
- Apache ZooKeeper
- HashiCorp Vault
- Envoy

The services are containerized using Docker and communicate over a dedicated Docker bridge network.

---

# Architecture

```text
                         ┌───────────────────────┐
                         │       Client          │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │        Envoy          │
                         │       :8080           │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │     API Gateway       │
                         │       :8081           │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
       │  Identity   │       │Organization │       │   Policy    │
       │   :8002     │       │   :8003     │       │   :8004     │
       └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                                    ▼
                             ┌─────────────┐
                             │ PostgreSQL  │
                             │    :5432    │
                             └─────────────┘


       ┌─────────────┐       ┌─────────────┐
       │   Secrets   │──────▶│    Vault    │
       │   :8005     │       │    :8200    │
       └─────────────┘       └─────────────┘


       ┌─────────────┐
       │    Audit    │
       │   :8086     │
       └──────┬──────┘
              │
              ▼
       ┌─────────────┐
       │    Kafka    │
       │    :9092    │
       └──────┬──────┘
              │
              ▼
       ┌─────────────┐
       │  ZooKeeper  │
       │    :2181    │
       └─────────────┘


       ┌─────────────┐
       │Configuration│
       │   :8087     │
       └─────────────┘


       ┌─────────────┐
       │    Redis    │
       │    :6379    │
       └─────────────┘

Services
1. API Gateway

Technology: Go + Echo

The API Gateway provides the central entry point for client requests.

Responsibilities
Request routing
Service discovery through configured service URLs
API aggregation
Authentication integration
Authorization integration
Policy integration
Audit integration
Configuration integration
Secrets integration
Internal Port
8080
Host Port
8081
2. Identity Service

Technology: Python + FastAPI

The Identity Service is responsible for identity and authentication-related functionality.

Responsibilities
User management
Authentication
Authorization foundation
JWT
OAuth2
OIDC
SCIM
Session management
Refresh tokens
MFA
Password reset
Internal Port
8000
Host Port
8002
Health Endpoint
GET /health

Example response:

{
  "status": "healthy",
  "service": "identity"
}
3. Organization Service

Technology: Python + FastAPI

The Organization Service manages organization and tenant-related functionality.

Responsibilities
Organization management
Tenant management
Organization membership
Organization-level data
Integration with Identity Service
Internal Port
8001
Host Port
8003
Health Endpoint
GET /health
4. Policy Service

Technology: Python + FastAPI

The Policy Service provides policy and authorization-related functionality.

Responsibilities
Policy management
Policy evaluation
Authorization rules
Organization-aware policies
Identity integration
Policy caching
Internal Port
8002
Host Port
8004
Health Endpoint
GET /health
5. Secrets Service

Technology: Python + FastAPI

The Secrets Service provides a controlled interface for application secrets and integrates with HashiCorp Vault.

Responsibilities
Secret retrieval
Secret storage integration
Vault integration
Secret caching
Centralized secret access
Internal Port
8003
Host Port
8005
Health Endpoint
GET /health

Example response:

{
  "status": "healthy",
  "service": "secrets-service"
}
6. Audit Service

Technology: Go + Echo

The Audit Service provides centralized audit event processing.

Responsibilities
Audit event ingestion
Audit event processing
Kafka integration
Event batching
Audit integrity
Hash-based audit processing
Internal Port
8082
Host Port
8086
Configuration
AUDIT_BATCH_SIZE=100
AUDIT_HASH_ALGORITHM=SHA256
KAFKA_TOPIC_AUDIT=audit-events
Health Endpoint
GET /health
7. Configuration Service

Technology: Go + Echo

The Configuration Service manages application and feature configuration.

Responsibilities
Configuration management
Feature flags
Configuration caching
Organization-aware configuration
Organization Service integration
Internal Port
8083
Host Port
8087
Health Endpoint
GET /health

Technology Stack

| Component               | Technology          |
| ----------------------- | ------------------- |
| API Gateway             | Go + Echo           |
| Identity                | Python + FastAPI    |
| Organization            | Python + FastAPI    |
| Policy                  | Python + FastAPI    |
| Secrets                 | Python + FastAPI    |
| Audit                   | Go + Echo           |
| Configuration           | Go + Echo           |
| Database                | PostgreSQL 17       |
| Cache                   | Redis 8             |
| Messaging               | Apache Kafka        |
| Kafka Coordination      | ZooKeeper           |
| Secrets Management      | HashiCorp Vault     |
| Proxy                   | Envoy               |
| Containers              | Docker              |
| Container Orchestration | Docker Compose      |
| Source Control          | Git                 |
| Repository              | GitHub              |
| Authentication          | JWT / OAuth2 / OIDC |
| Authorization           | RBAC / Policy-based |
| Identity Provisioning   | SCIM                |

Repository Structure

AEV-Module1_POD-Alpha/
│
├── .github/
│   ├── workflows/
│   └── ...
│
├── docker/
│   ├── envoy/
│   │   └── envoy.yaml
│   │
│   ├── postgres/
│   │   └── init.sql
│   │
│   ├── redis/
│   │   └── redis.conf
│   │
│   └── vault/
│       └── config.hcl
│
├── services/
│   │
│   ├── gateway/
│   │   ├── Dockerfile
│   │   └── ...
│   │
│   ├── identity/
│   │   ├── Dockerfile
│   │   ├── app/
│   │   ├── requirements.txt
│   │   └── ...
│   │
│   ├── organization/
│   │   ├── Dockerfile
│   │   └── ...
│   │
│   ├── policy/
│   │   ├── Dockerfile
│   │   └── ...
│   │
│   ├── secrets/
│   │   ├── Dockerfile
│   │   └── ...
│   │
│   ├── audit/
│   │   ├── Dockerfile
│   │   ├── go.mod
│   │   ├── cmd/
│   │   └── ...
│   │
│   └── configuration/
│       ├── Dockerfile
│       └── ...
│
├── docker-compose.yml
├── README.md
└── ...

Service Ports

| Service       | Internal Port | Host Port |
| ------------- | ------------: | --------: |
| Envoy         |          8080 |      8080 |
| Gateway       |          8080 |      8081 |
| Identity      |          8000 |      8002 |
| Organization  |          8001 |      8003 |
| Policy        |          8002 |      8004 |
| Secrets       |          8003 |      8005 |
| Audit         |          8082 |      8086 |
| Configuration |          8083 |      8087 |
| PostgreSQL    |          5432 |      5432 |
| Redis         |          6379 |      6379 |
| Kafka         |          9092 |      9092 |
| ZooKeeper     |          2181 |      2181 |
| Vault         |          8200 |      8200 |


Infrastructure Components
PostgreSQL

PostgreSQL is the primary relational database.

Current development configuration:

Host: postgres
Port: 5432
Database: pod_alpha
User: postgres

The database is exposed locally on:

localhost:5432
Redis

Redis provides caching functionality for services that require fast access to frequently used data.

Host: redis
Port: 6379

Local access:

localhost:6379

Redis data is persisted through the Docker volume:

pod-alpha_redis_data
Kafka

Kafka is used for asynchronous event communication.

The primary audit topic is:

audit-events

Kafka:

Host: kafka
Port: 9092

Local access:

localhost:9092
ZooKeeper

ZooKeeper is currently used for Kafka coordination.

Host: zookeeper
Port: 2181
HashiCorp Vault

Vault is used as the secrets management layer.

Host: vault
Port: 8200

Local access:

http://localhost:8200

Vault uses file storage for the current development environment.

The Vault data is persisted through:

pod-alpha_vault_data
Important

Vault uses Shamir Secret Sharing.

The current development Vault was initialized with:

Total Shares: 5
Threshold: 3

This means three valid unseal keys are required to unseal Vault.

Never commit Vault unseal keys or root credentials to Git.

Docker Architecture

All services are connected through the Docker network:

pod-alpha_backend

The network uses the Docker bridge driver.

Services communicate using Docker service names rather than localhost.

For example:

identity:8000
organization:8001
policy:8002
secrets:8003
postgres:5432
redis:6379
kafka:9092
vault:8200

Inside a container:

localhost

refers to the current container.

Therefore, service-to-service communication must use the Docker service name.

Example:

http://identity:8000

instead of:

http://localhost:8000
Database Strategy

The project uses PostgreSQL as the primary database infrastructure.

The current Docker setup provides a PostgreSQL container with persistent storage.

Database connection:

postgresql://postgres:postgres@postgres:5432/pod_alpha

Database initialization scripts are located under:

docker/postgres/
Service Communication

The current service communication model is HTTP-based for synchronous communication.

Example:

Gateway
   │
   ├── Identity Service
   ├── Organization Service
   ├── Policy Service
   ├── Secrets Service
   ├── Audit Service
   └── Configuration Service

Asynchronous audit/event processing uses Kafka.

Example:

Application
    │
    ▼
Audit Service
    │
    ▼
Kafka
    │
    ▼
audit-events
Week 1 Completion

Week 1 focused on establishing the foundation required for further development.

Completed Components
Docker Architecture
Docker Compose configuration established.
Service containers defined.
Service networking established.
Persistent Docker volumes configured.
Healthchecks configured for infrastructure and application services.
Service dependencies configured using depends_on.
Infrastructure

The following infrastructure components are operational:

PostgreSQL
Redis
Kafka
ZooKeeper
HashiCorp Vault
Envoy
Application Services

The following services have been containerized and health-checked:

API Gateway
Identity Service
Organization Service
Policy Service
Secrets Service
Audit Service
Configuration Service
Identity Service

Week 1 foundation includes:

FastAPI application setup
Docker configuration
PostgreSQL connectivity configuration
Redis configuration
JWT configuration
Application settings management
Health endpoint
Container healthcheck
Secrets Service

Week 1 foundation includes:

FastAPI application setup
Docker configuration
Vault dependency
Vault connectivity configuration
Secret service configuration
Health endpoint
Container healthcheck
Vault

Week 1 Vault work includes:

Vault container configuration
Persistent Vault storage
Vault configuration
Vault initialization
Vault unseal process
Vault health verification
Secrets Service integration
Audit Service

Week 1 includes:

Go service setup
Dockerfile configuration
Go module configuration
Server entry point
Kafka configuration
PostgreSQL configuration
Health endpoint
Current Health Verification

The following services have been verified as healthy in the local Docker environment:

audit          healthy
identity       healthy
kafka          healthy
postgres       healthy
redis          healthy
secrets        healthy
vault          healthy
zookeeper      healthy

Example:

docker compose ps

Expected status:

healthy

for the services that expose Docker healthchecks.

Prerequisites

Before starting development, install:

Git
Docker Desktop
Docker Compose
Python 3.12+
Go
PostgreSQL client tools (optional)
Redis CLI (optional)

Docker Desktop must be running.

Verify Docker:

docker --version

Verify Docker Compose:

docker compose version

Verify Git:

git --version
Local Setup

Clone the repository:

git clone https://github.com/Farhan15914/AEV-Module1_POD-Alpha.git

Move into the repository:

cd AEV-Module1_POD-Alpha

Check the current branch:

git branch

Update the repository:

git fetch origin

Update develop:

git checkout develop
git pull origin develop
Environment Configuration

Each service may have its own environment configuration.

Development configuration should be maintained through environment variables or appropriate local .env files.

Do not commit sensitive credentials.

Examples of sensitive values include:

JWT_SECRET
VAULT_TOKEN
VAULT_UNSEAL_KEYS
DATABASE_PASSWORD
API_KEYS
OAUTH_CLIENT_SECRET

Use .env.example files to document required variables without exposing real credentials.

Starting the Platform

From the project root:

docker compose up -d

Check the running services:

docker compose ps

View logs:

docker compose logs

View logs for one service:

docker compose logs identity

Follow logs:

docker compose logs -f identity
Rebuilding Services

After changing a service:

docker compose up -d --build <service>

Example:

docker compose up -d --build identity

For a complete rebuild:

docker compose build

Then:

docker compose up -d
Health Checks
Identity
curl.exe http://localhost:8002/health

Expected:

{
  "status": "healthy",
  "service": "identity"
}
Secrets
curl.exe http://localhost:8005/health

Expected:

{
  "status": "healthy",
  "service": "secrets-service"
}
Vault
curl.exe http://localhost:8200/v1/sys/health

Check:

initialized: true
sealed: false
Docker Health Status
docker compose ps
Vault Setup

Vault must be initialized and unsealed before services that depend on it can use it.

Check Vault status:

docker exec vault vault status

A healthy, unsealed Vault should show:

Initialized     true
Sealed          false

If Vault is sealed, unseal it using the required unseal keys:

docker exec -it vault vault operator unseal

The current development configuration requires three of the five generated unseal key shares.

Important

Do not store the unseal keys in:

Git
GitHub
README
Docker Compose
.env committed to the repository
Team chat

Store sensitive Vault credentials securely.

Kafka Setup

Check Kafka:

docker compose ps kafka

Kafka should report:

healthy

Kafka topics can be inspected using:

docker exec kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --list

The audit topic is:

audit-events
Database

Check PostgreSQL:

docker compose ps postgres

Connect to PostgreSQL:

docker exec -it postgres psql -U postgres -d pod_alpha

List databases:

\l

List tables:

\dt

Exit:

\q
Redis

Check Redis:

docker compose ps redis

Test Redis:

docker exec redis redis-cli ping

Expected:

PONG
Development Workflow

The project uses Git-based feature development.

Developers should not work directly on main or develop.

The standard workflow is:

main
  │
  ▼
develop
  │
  ├── feature/service-developer
  │
  ├── feature/service-developer
  │
  └── feature/service-developer
           │
           ▼
        Pull Request
           │
           ▼
        develop
           │
           ▼
          main
Branching Strategy
Main

main contains stable, reviewed code.

Developers should not directly commit to main.

Develop

develop is the primary integration branch.

Feature branches are created from develop.

Feature Branches

Feature branches should follow:

feature/<service>-<developer>

Examples:

feature/identity-auth
feature/secrets-vault
feature/policy-engine
feature/audit-ledger
feature/gateway-routing
feature/config-flags
Creating a Feature Branch

Start from the latest develop:

git checkout develop
git pull origin develop

Create the feature branch:

git checkout -b feature/<service>-<feature>

Example:

git checkout -b feature/identity-auth

Push the branch:

git push -u origin feature/identity-auth
Keeping a Feature Branch Updated

Before starting work:

git checkout develop
git pull origin develop

Switch back:

git checkout feature/<service>-<name>

Merge the latest development changes:

git merge develop

Resolve conflicts if required.

Commit Guidelines

Use clear and meaningful commit messages.

Examples:

feat: add user authentication endpoint
fix: resolve Vault healthcheck configuration
refactor: restructure identity service configuration
test: add authentication service tests
docs: update identity service documentation

Avoid commits such as:

update
changes
final
working
Pull Request Workflow

When the feature is complete:

git status

Stage changes:

git add .

Commit:

git commit -m "feat: <description>"

Push:

git push

Create a Pull Request:

feature/<service>-<developer>
             │
             ▼
          develop

The PR should be reviewed before merging.

Pull Request Requirements

Every PR should include:

Clear title
Description of changes
Related GitHub Issue
Testing performed
Docker verification where applicable
API verification where applicable
Database migration details where applicable
Security considerations
Breaking changes, if any

Before requesting review:

docker compose config

and:

docker compose ps

should be checked.

Week 2 Development

Week 2 builds on the foundation established during Week 1.

The development focus includes implementation of application functionality on top of the established infrastructure.

Developers should:

Update develop.
Create a feature branch.
Implement the assigned task.
Add or update tests.
Verify Docker integration.
Verify service health.
Commit changes.
Push the feature branch.
Open a PR into develop.
Resolve review comments.
Merge after approval.
Troubleshooting
Check all services
docker compose ps
View service logs
docker compose logs --tail=100 <service>

Example:

docker compose logs --tail=100 secrets
Restart a service
docker compose restart <service>

Example:

docker compose restart identity
Recreate a service
docker compose up -d --force-recreate <service>
Rebuild and recreate
docker compose up -d --build --force-recreate <service>
Check the resolved Docker Compose configuration
docker compose config

This is useful for identifying:

Incorrect environment variables
Incorrect service dependencies
Incorrect ports
Incorrect volume mappings
Incorrect healthchecks
Incorrect network configuration
Vault Troubleshooting

Check status:

docker exec vault vault status

If:

Sealed: true

Vault needs to be unsealed.

Use:

docker exec -it vault vault operator unseal

Three valid key shares are required for the current development configuration.

If Vault reports:

A storage backend must be specified

check:

Get-Content .\docker\vault\config.hcl

and verify the Vault configuration defines the required storage backend and listener configuration.

Secrets Healthcheck Troubleshooting

The Secrets Service runs internally on:

8003

and is exposed on the host as:

8005

Test from the host:

curl.exe http://localhost:8005/health

Test from inside the container:

docker exec secrets python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8003/health').read().decode())"

If the Docker healthcheck fails because wget is unavailable, use a healthcheck compatible with the service image.

Security Considerations

Security is a core requirement of Pod Alpha.

Never commit secrets

Never commit:

.env
Vault unseal keys
Vault root tokens
JWT production secrets
Database production passwords
OAuth client secrets
API keys
Private keys
Certificates containing private keys
Development Secrets

Development secrets may use placeholder values where appropriate.

Example:

change-me

must never be used as a production secret.

Vault

Vault should be used as the centralized secrets management layer.

Applications should retrieve sensitive values through the Secrets Service rather than hardcoding secrets.

JWT

JWT signing secrets must be:

Strong
Randomly generated
Stored securely
Different between environments

Never use a development JWT secret in production.

Team Responsibilities

Pod Alpha is divided into service-focused squads.

Service	Primary Responsibilities
API Gateway	Routing, gateway integration, request handling
Identity	Authentication, authorization foundation, users, sessions
Organization	Organizations, tenants, memberships
Policy	Policies, authorization rules, policy evaluation
Secrets	Vault integration and secret management
Audit	Audit events and Kafka integration
Configuration	Application configuration and feature flags

Each squad is responsible for:

Service implementation
Unit testing
Integration testing
Docker compatibility
Documentation
Code review
Security considerations
API contract compliance
Development Rules

The following rules apply to all contributors.

Rule 1

Do not commit directly to main.

Rule 2

Do not commit directly to develop.

Rule 3

Always create a feature branch from the latest develop.

Rule 4

Keep feature branches focused on the assigned task.

Rule 5

Do not commit secrets.

Rule 6

Test the service locally before opening a PR.

Rule 7

Keep Docker configuration working.

Rule 8

Update documentation when functionality or configuration changes.

Rule 9

PRs must be reviewed before merging.

Rule 10

Do not force-push shared branches.

Roadmap
Week 1 - Foundation

Completed:

Repository setup
Microservice structure
Docker architecture
Docker Compose
PostgreSQL
Redis
Kafka
ZooKeeper
Vault
Envoy
Service Dockerfiles
Service healthchecks
Initial service configurations
Initial service integration
Development branch workflow
Week 2 - Core Service Development

Planned areas include:

Identity functionality
Authentication foundation
Organization functionality
Policy foundation
Secrets integration
Audit integration
Configuration functionality
API contracts
Testing
Service integration
Future Phases

Future development will include:

Complete authentication flows
JWT access and refresh tokens
RBAC
OAuth2
OIDC
SCIM
MFA
Session management
Policy enforcement
Centralized secrets management
Audit event processing
Configuration management
Gateway authorization
Service-to-service security
Observability
Production hardening
CI/CD improvements
Contributing
Clone the repository.
Checkout develop.
Pull the latest changes.
Create a feature branch.
Implement the assigned task.
Write/update tests.
Verify the service locally.
Commit changes using the project's commit conventions.
Push the feature branch.
Open a Pull Request into develop.
Address review comments.
Merge only after approval.
Useful Commands
Start everything
docker compose up -d
Stop everything
docker compose down
Check services
docker compose ps
View logs
docker compose logs
Follow logs
docker compose logs -f
Rebuild
docker compose build
Rebuild and start
docker compose up -d --build
Validate Compose
docker compose config
Git status
git status
Update develop
git checkout develop
git pull origin develop
Create feature branch
git checkout -b feature/<service>-<name>
Push feature branch
git push -u origin feature/<service>-<name>
Project Status
Week 1 Status: COMPLETED

The Pod Alpha foundation has been established and the core development infrastructure is operational.

Current local Docker environment provides:

PostgreSQL    ✓ Healthy
Redis         ✓ Healthy
Kafka         ✓ Healthy
ZooKeeper     ✓ Healthy
Vault         ✓ Healthy
Identity      ✓ Healthy
Secrets       ✓ Healthy
Audit         ✓ Healthy

The project is ready to proceed with Week 2 feature development.

Maintainers

AEV Module 1 - Pod Alpha

Foundation & Trust Layer

Repository:

AEV-Module1_POD-Alpha

Development branch:

develop

Stable branch:

main
Final Note

Pod Alpha is being developed as a modular foundation for the larger AEV Module 1 platform.

All services should remain independently maintainable while following the common project standards for:

Security
API contracts
Docker
Database management
Testing
Logging
Configuration
Git workflow
Code review

The Week 1 foundation provides the infrastructure required for the team to begin implementing the next layer of functionality during Week 2.


### One thing I would change before you commit this

Your current README should **not claim that every service is fully implemented** just because every container is healthy. A healthy container only proves the service starts and its health endpoint responds.

So I deliberately used wording like **"foundation established," "containerized," "configuration," and "health-checked"** rather than claiming that authentication, RBAC, OAuth, policy evaluation, etc. are already complete.

For the Week 1 PR, that's much more accurate and defensible.

# Week 3 - Security Integration, Configuration and Verification

## Objectives

Week 3 focused on completing the Organization Service security integration, improving configuration management, cleaning up test coverage, and completing service verification.

## Completed Work

### JWT Authentication

- Resolved the JWT import mismatch between the authentication and security modules.
- Standardized JWT validation through `validate_jwt_claims()`.
- Added validation for required JWT claims.
- Added rejection of invalid JWTs.
- Added rejection of JWTs missing the required `sub` claim.

### Bearer Authentication

- Verified extraction of Bearer tokens from the `Authorization` header.
- Verified rejection when the Authorization header is missing.
- Verified rejection when an invalid authentication scheme is supplied.

### Tenant Context

- Verified tenant context creation from JWT claims.
- Verified user ID extraction from the `sub` claim.
- Verified tenant ID extraction when `tenant_id` is present.
- Verified behavior when `tenant_id` is not present.
- Verified rejection when the required JWT subject is missing.

### Authorization

- Verified permission-based authorization.
- Verified that users with the required permission are allowed.
- Verified that users without the required permission are rejected.
- Verified HTTP `403 Forbidden` for missing permissions.

### Database Configuration

Hardcoded PostgreSQL credentials were removed from `docker-compose.yml`.

Database configuration now uses environment variables:

- `DATABASE_URL`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

Local development values are provided through `.env`, which is excluded from source control.

### Testing

Security test coverage was expanded to include:

- Bearer token extraction
- Missing Authorization header
- Invalid authorization scheme
- Valid JWT validation
- Invalid JWT rejection
- Missing `sub` claim rejection

Duplicate coverage was cleaned up while preserving unique security, tenant context, and authorization tests.

## Week 3 Verification Evidence

| Verification | Result |
|---|---|
| Bearer token extraction | PASSED |
| Invalid authorization scheme rejection | PASSED |
| JWT validation | PASSED |
| Invalid JWT rejection | PASSED |
| Missing `sub` rejection | PASSED |
| Tenant context with tenant | PASSED |
| Tenant context without tenant | PASSED |
| Permission granted | PASSED |
| Permission denied | PASSED |
| HTTP 403 authorization | PASSED |
| Organization service startup | PASSED |
| `/health` endpoint | PASSED |
| `/ready` endpoint | PASSED |
| Database connectivity | PASSED |
| Full pytest suite | **23 PASSED** |

## Service Verification

The Organization Service was started through Docker Compose and verified as healthy.

### Health Check

`GET /health`

Result:

`HTTP 200 OK`

Response:

`{"status":"healthy","service":"organization-service"}`

### Readiness Check

`GET /ready`

Result:

`HTTP 200 OK`

Response:

`{"status":"ready","database":"connected"}`

## Final Test Result

The complete Organization Service test suite was executed with:

`python -m pytest -v`

Final result:

**23 passed in 4.58s**

## Week 3 Status

Week 3 security integration, environment-based database configuration, authorization verification, service startup verification, and automated testing have been completed.
