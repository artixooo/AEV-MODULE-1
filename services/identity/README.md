# Identity Service

## Purpose

Provides authentication and identity management for users. Responsible for secure login, token generation, session management, and identity federation.

---

## Team Ownership

**Squad:** Squad 2

**Lead:** Farhan Rauf Bahadure

**Members:**
- Aditya Tayade
- Batchu Bhanuteja

---

## Responsibilities

- Login
- Logout
- JWT Generation
- Refresh Tokens
- MFA
- OAuth 2.0
- OpenID Connect (OIDC)
- SAML Authentication
- SCIM Provisioning
- Session Management

---

## APIs

| Method | Endpoint   | Description          |
|--------|------------|----------------------|
| POST   | /login     | User Login           |
| POST   | /logout    | Logout User          |
| POST   | /refresh   | Refresh Access Token |
| GET    | /userinfo  | User Profile         |
| POST   | /mfa/verify| Verify MFA           |

---

## Database

- PostgreSQL
- Redis (Session Storage)

---

## Dependencies

- Organization Service
- Policy Service
- Secrets Service

---

## Technology

- Python
- FastAPI
- PostgreSQL
- Redis

---

## Environment Variables

See `.env.example`

---

## Infrastructure

- PostgreSQL connection configured through environment variables
- Redis connection configured through environment variables
- Database tables initialized during application startup
- Redis connectivity verified during application startup
- Graceful Redis connection shutdown on application termination

## Health Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Service health check |
| GET | /ready | Database and Redis readiness check |

## Local Service Startup

```bash
uvicorn app.main:app --reload
```

PostgreSQL and Redis must be available before starting the Identity Service.
