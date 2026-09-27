```markdown
# Authentication Setup & Verification Guide

This guide details how to configure, boot, and verify the authentication infrastructure across the API Gateway and Identity microservices.

---

## 1. Prerequisites

- Docker and Docker Compose (v2.20+)
- Go (v1.22+)
- Python (v3.11+)
- `curl` CLI

---

## 2. Environment Configuration

### Gateway Environment (`services/gateway/.env`)
The Gateway operates with the following default environment configuration:
```env
PORT=8080
ENV=development
JWT_SECRET_KEY=change_this_secret_key
JWT_SECRET=change_this_secret_key
IDENTITY_SERVICE_URL=http://identity:8000
SERVICE_API_KEY=dev_internal_key_123
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=aev_db

### Identity Service Environment (`services/identity/.env`)
The Identity service operates with the following environment configuration (initialize by copying `.env.example` to `.env`):
```env
APP_NAME=Identity Service
APP_ENV=development
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=identity_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_me
DATABASE_URL=postgresql://postgres:change_me@localhost:5432/identity_db
REDIS_HOST=redis
REDIS_PORT=6379
JWT_SECRET_KEY=change_this_secret_key_at_least_32_characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7


Integration Requirement: In end-to-end integrated environments, JWT_SECRET_KEY must be manually aligned to be identical across both services for edge signature verification to succeed.