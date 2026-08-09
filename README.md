# Identity Service

## Purpose

The Identity Service is responsible for authentication, authorization, and identity management within the CTEM Platform.

---

## Technology Stack

- Python 3.12
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Alembic
- Docker

---

## Responsibilities

- User Login
- User Logout
- JWT Token Generation
- Refresh Tokens
- Multi-Factor Authentication (MFA)
- OAuth 2.0
- OpenID Connect (OIDC)
- SAML Authentication
- SCIM Provisioning
- Session Management

---

## Project Structure

```
identity/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── middleware/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   └── utils/
├── configs/
├── docs/
├── migrations/
├── tests/
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Environment Variables

Configuration variables are provided in `.env.example`.

---

## Development Status

### Week 1

- [x] Project structure verified
- [x] Dockerfile verified
- [x] Requirements file prepared
- [x] Environment configuration template prepared
- [x] Migrations folder verified
- [x] Configuration folder verified
- [x] Documentation initialized
- [x] Tests folder initialized

---

## Team

**Lead**

- Farhan Rauf Bahadure

**Members**

- Aditya Tayade
- Batchu Bhanuteja