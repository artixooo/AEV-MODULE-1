# Secrets Service

The **Secrets Service** is a microservice within the **Pod Alpha** ecosystem responsible for securely managing, retrieving, rotating, and auditing sensitive credentials, API keys, certificates, and environment secrets. It acts as a centralized secret management layer by integrating with **HashiCorp Vault** while storing non-sensitive metadata and version information in **PostgreSQL**.

---

# Team Ownership

| Role | Member |
|------|--------|
| **Squad** | Squad 5 – Secrets |
| **Squad Lead** | Bezawada Kushal Ram |
| **Squad Member** | Adhithyan Biju |

---

# Responsibilities

- Secure integration with HashiCorp Vault
- Store and manage secret metadata
- Secret version management
- Dynamic secret rotation policies
- Automated rotation workflows
- REST APIs for internal microservices
- Audit logging for secret access and rotation events

---

# Architecture

```
                +-------------------------+
                | Internal Microservices |
                +-----------+------------+
                            |
                            v
                    REST API (FastAPI)
                            |
                            v
                  +---------------------+
                  |   Secrets Service   |
                  +----------+----------+
                             |
            +----------------+----------------+
            |                                 |
            v                                 v
   HashiCorp Vault                     PostgreSQL
 (Secret Storage)               (Metadata & Audit Logs)
```

---

# Project Structure

```text
services/secrets/
├── app/
│   ├── api/              # API route handlers
│   ├── core/             # Configuration & settings
│   ├── db/               # Database models & connection
│   ├── middleware/       # Custom FastAPI middleware
│   ├── models/           # ORM & Pydantic models
│   ├── routers/          # API routing modules
│   ├── schemas/          # Request/Response schemas
│   ├── services/         # Business logic
│   ├── utils/            # Helper utilities
│   ├── vault/            # HashiCorp Vault integration
│   ├── __init__.py
│   └── main.py           # FastAPI entrypoint
│
├── configs/              # Configuration files
├── docs/                 # Documentation
├── migrations/           # Database migrations
├── tests/                # Unit & Integration tests
├── .env.example          # Environment template
├── Dockerfile            # Docker image
└── README.md
```

---

# Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12 |
| Framework | FastAPI |
| ASGI Server | Uvicorn |
| Database | PostgreSQL |
| Secret Storage | HashiCorp Vault |
| Vault SDK | hvac |
| Configuration | pydantic-settings |
| Containerization | Docker |

---

# Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| APP_NAME | Service Name | Secrets Service |
| PORT | Service Port | 8003 |
| VAULT_ADDR | Vault Server Address | http://127.0.0.1:8200 |
| VAULT_TOKEN | Vault Access Token | Environment Variable |
| POSTGRES_USER | PostgreSQL Username | postgres |
| POSTGRES_PASSWORD | PostgreSQL Password | postgres |
| POSTGRES_DB | Database Name | pod_alpha |
| POSTGRES_HOST | PostgreSQL Host | postgres |
| POSTGRES_PORT | PostgreSQL Port | 5432 |

Example:

```env
APP_NAME=Secrets Service
PORT=8003

VAULT_ADDR=http://127.0.0.1:8200
VAULT_TOKEN=<your-vault-token>

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=pod_alpha
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

---

# Local Development

## 1. Navigate to the Service

```bash
cd services/secrets
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate
```

### macOS/Linux

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run the Development Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

The API will be available at:

```
http://localhost:8003
```

Swagger UI:

```
http://localhost:8003/docs
```

ReDoc:

```
http://localhost:8003/redoc
```

---

# Docker

## Build Image

```bash
docker build -t secrets-service .
```

## Run Container

```bash
docker run -d \
  --name secrets-service \
  -p 8003:8003 \
  --env-file .env \
  secrets-service
```

---

# API Endpoints

| Method | Endpoint | Description | Status |
|---------|----------|-------------|--------|
| GET | `/health` | Liveness Probe | ✅ Available |
| GET | `/ready` | Readiness Probe (Vault Connectivity) | ✅ Available |
| POST | `/secrets` | Create Secret Version | 🚧 Planned |
| GET | `/secrets/{id}` | Retrieve Secret | 🚧 Planned |
| PUT | `/secrets/{id}/rotate` | Rotate Secret | 🚧 Planned |

---

# Health Checks

### Liveness

```http
GET /health
```

Example Response

```json
{
  "status": "healthy"
}
```

---

### Readiness

```http
GET /ready
```

Example Response

```json
{
  "status": "ready",
  "vault": "connected"
}
```
---

# Future Scope

- [ ] HashiCorp Vault AppRole authentication
- [ ] Automated secret rotation workflows
- [ ] Alembic database migrations
- [ ] Fine-grained audit logging
- [ ] Authentication middleware
- [ ] Authorization (RBAC)
- [ ] Secret version rollback
- [ ] Metrics and monitoring
- [ ] Prometheus integration
- [ ] OpenTelemetry tracing

---

# Week 1 Status

## Sprint

**Week 1 – Secrets Service Project Setup & Vault Integration Preparation**

### Objective

Prepare the Secrets Service foundation and verify the complete development environment for HashiCorp Vault integration.


---

## Component Status

| Component | Status |
|-----------|--------|
| FastAPI Project Setup | ✅ Initialized |
| Project Structure Verification | ✅ Verified |
| Dockerfile Configuration | ✅ Prepared |
| HashiCorp Vault Configuration | ✅ Prepared |
| Application Configuration | ✅ Verified |
| Requirements & Dependencies | ✅ Verified |
| Database Migration Structure | ✅ Initialized |
| Services Layer Structure | ✅ Initialized |
| Schemas & Models | ✅ Initialized |
| Documentation | ✅ Prepared |
| Initial Test Structure | ✅ Initialized |

---

## Tasks Completed

- ✅ Initialized FastAPI project setup
- ✅ Prepared Docker configuration
- ✅ Prepared HashiCorp Vault configuration
- ✅ Verified project dependencies
- ✅ Initialized database migration structure
- ✅ Verified application architecture
- ✅ Initialized service layer structure
- ✅ Initialized schemas and models
- ✅ Prepared project documentation
- ✅ Initialized testing structure

---

## Deliverables

| Deliverable | Status |
|-------------|--------|
| Project Foundation | ✅ Prepared |
| Vault Configuration | ✅ Prepared |
| Documentation | ✅ Prepared |
| Docker Configuration | ✅ Prepared |

---

## Week 1 Outcome

The foundational setup for the **Secrets Service** has been prepared and verified. The service architecture, Docker configuration, Vault integration scaffolding, project structure, and documentation provide a solid foundation for implementing secret management features in future development phases.


**Squad 5 – Secrets**

- **Bezawada Kushal Ram** — Squad Lead
- **Adhithyan Biju** — Squad Member
