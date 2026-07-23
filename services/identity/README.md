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