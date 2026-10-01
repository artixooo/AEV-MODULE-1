# Identity Service

The Identity Service provides authentication and identity foundations for Pod Alpha.

It is responsible for user registration, credential verification, JWT-based authentication, refresh-token management, session foundations, and authentication-related API contracts.

---

## Technology

* Python
* FastAPI
* PostgreSQL
* Redis
* SQLAlchemy
* JWT
* bcrypt
* Docker

---

## Service Information

| Item             | Value      |
| ---------------- | ---------- |
| Service          | Identity   |
| Framework        | FastAPI    |
| Internal Port    | `8000`     |
| Docker Host Port | `8002`     |
| Database         | PostgreSQL |
| Cache            | Redis      |
| API Version      | `v1`       |

When running through Pod Alpha Docker Compose, the Identity Service is available at:

```text
http://localhost:8002
```

Swagger/OpenAPI documentation:

```text
http://localhost:8002/docs
```

Health endpoint:

```text
GET /health
```

Readiness endpoint:

```text
GET /ready
```

---

# Authentication APIs

All authentication APIs use the following base path:

```text
/api/v1/auth
```

## Register

```text
POST /api/v1/auth/register
```

Creates a new user for the specified tenant.

The user's password is stored as a bcrypt hash and is never stored as plaintext.

---

## Login

```text
POST /api/v1/auth/login
```

Authenticates a user using their email address and password.

A successful login returns:

```json
{
  "access_token": "<JWT>",
  "refresh_token": "<JWT>",
  "token_type": "bearer",
  "expires_in": 1800
}
```

The access-token expiration is controlled by:

```text
ACCESS_TOKEN_EXPIRE_MINUTES
```

The default configuration is 30 minutes.

| Method | Gateway Endpoint | Identity Service Endpoint | Description |
|--------|------------------|---------------------------|-------------|
| POST | `/api/v1/auth/login` | `/auth/login` | Authenticate user and issue access and refresh tokens |
| POST | `/api/v1/auth/refresh` | `/auth/refresh` | Generate a new access token using a refresh token |

### Login

**POST** `/api/v1/auth/login`

Authenticates a user using their email address and password.

On successful authentication, the service returns an access token and refresh token.

### Refresh Token

**POST** `/api/v1/auth/refresh`

Generates a new access token using a valid refresh token supplied as the `refresh_token` query parameter.

For the complete API contract, see [`docs/API.md`](docs/API.md) and [`docs/openapi.yaml`](docs/openapi.yaml).
---

## Refresh Token

```text
POST /api/v1/auth/refresh
```

Accepts a valid refresh token and issues a new access token and refresh token.

Refresh-token rotation is implemented.

After a successful refresh:

1. The supplied refresh token is validated.
2. The existing refresh token is revoked.
3. A new access token is generated.
4. A new refresh token is generated.
5. The new refresh token is persisted.
6. The new token remains associated with the existing session.

A previously revoked refresh token cannot be reused.

---

## Logout

```text
POST /api/v1/auth/logout
```

Revokes the supplied refresh token after validating the authenticated user's ownership of the token.

A revoked refresh token cannot be used for another refresh operation.

---

## Protected Profile

```text
GET /api/v1/auth/profile
```

Requires:

```text
Authorization: Bearer <access_token>
```

The endpoint verifies the access JWT and returns basic authenticated-user information.

---

# Authentication Flow

The current authentication flow is:

```text
Register
   |
   v
Password hashed with bcrypt
   |
   v
User stored in PostgreSQL
   |
   v
Login
   |
   v
Credentials verified
   |
   +-------------------+
   |                   |
   v                   v
Access JWT         Refresh JWT
   |                   |
   |                   v
   |             SHA-256 hash
   |                   |
   |                   v
   |             PostgreSQL
   |                   |
   +---------+---------+
             |
             v
       Authenticated API
```

---

# JWT Access Token

Access tokens are signed using the configured JWT algorithm and secret key.

Current access-token claims include:

```json
{
  "sub": "<user-id>",
  "email": "<user-email>",
  "tenant_id": "<tenant-id>",
  "exp": "<expiration>",
  "type": "access"
}
```

The Identity Service validates the JWT signature, expiration, token type, and required subject claim.

### Important

The current Week 3 implementation does **not** add a `role` claim to the Identity JWT.

Role and authorization mapping are handled as a later authorization concern and should not be assumed to be part of the Week 3 authentication contract.

---

# Refresh Tokens

Refresh tokens are persisted in PostgreSQL.

The database stores a SHA-256 hash of the refresh token rather than using the raw refresh token as the lookup value in the `refresh_tokens` table.

Each refresh-token record contains:

* User ID
* Session ID
* Token hash
* Expiration time
* Revocation status
* Revocation timestamp
* Creation timestamp

Refresh tokens are rotated during refresh operations.

---

# Session Foundation

Identity maintains a session foundation in PostgreSQL.

The `sessions` table contains:

* Session ID
* User ID
* Tenant ID
* Session token
* Device information
* IP address
* User agent
* Active status
* Expiration time
* Last activity
* Creation timestamp

Refresh tokens are associated with sessions through:

```text
refresh_tokens.session_id
        |
        v
sessions.id
```

The session repository also provides session lookup, validity checking, and revocation operations.

---

# Database

Identity uses PostgreSQL.

Migration files are located at:

```text
database/identity/migrations/
```

Current migrations:

```text
001_create_users.sql
002_create_sessions.sql
003_create_refresh_tokens.sql
004_fix_users_schema.sql
```

The Identity Service executes the migration files during application startup.

---

# Password Security

Passwords are never stored directly.

The authentication service uses bcrypt through Passlib:

```text
Plaintext password
        |
        v
      bcrypt
        |
        v
 password_hash
        |
        v
   PostgreSQL
```

During login, the submitted password is verified against the stored password hash.

---

# Error Handling

Authentication failures use a structured error response:

```json
{
  "detail": "Authentication error",
  "error_code": "ERROR_CODE"
}
```

Authentication-related failures include cases such as:

* Invalid credentials
* Invalid access token
* Invalid refresh token
* Expired refresh token
* Revoked refresh token
* Invalid token payload
* Inactive user
* User not found
* Token ownership validation failure

---

# Testing

Identity repository and transaction tests are located under:

```text
services/identity/tests/
```

The current Week 3 test suite covers:

* Refresh-token hashing
* Refresh-token creation
* Refresh-token lookup
* Refresh-token validity
* Expired refresh tokens
* Revoked refresh tokens
* Session creation
* Session lookup
* Session validity
* Expired sessions
* Revoked sessions
* Transaction rollback
* User lookup by email
* User lookup by username
* User lookup by email or username

Run the test suite from the Identity directory:

```powershell
cd services/identity
python -m pytest tests -v
```

Current verification:

```text
16 passed
```

---

# Docker

Identity is included in the Pod Alpha Docker Compose environment.

Build:

```powershell
docker compose build identity
```

Start:

```powershell
docker compose up -d identity
```

Check status:

```powershell
docker compose ps
```

Identity should report:

```text
healthy
```

View logs:

```powershell
docker compose logs identity --tail=100
```

The service performs database migrations and checks Redis connectivity during startup.

---

# Configuration

Identity configuration is provided through environment variables.

Important settings include:

```text
APP_NAME
APP_ENV

POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD

REDIS_HOST
REDIS_PORT

JWT_SECRET_KEY
JWT_ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS
```

The database connection URL is constructed by the Identity configuration from the PostgreSQL settings.

Secrets such as `JWT_SECRET_KEY` and database passwords must not be committed to the repository.

---

# Week 3 Scope

Week 3 establishes the authentication foundation.

### Completed

* User registration
* Password hashing
* Password verification
* Login
* JWT access-token generation
* JWT validation
* JWT refresh-token generation
* Refresh-token persistence
* Refresh-token hashing
* Refresh-token rotation
* Refresh-token revocation
* Logout
* Protected authentication endpoint
* Authentication error handling
* Repository tests
* Transaction rollback testing
* Docker validation
* OpenAPI/API contract foundation

### Out of Scope for Week 3

The following features are not implemented as part of the Week 3 authentication foundation:

* OAuth 2.0 provider integration
* OpenID Connect provider integration
* SAML integration
* SCIM integration
* MFA implementation
* Advanced RBAC/ABAC authorization
* Enterprise Identity Provider integrations

These capabilities belong to later Identity and authorization work.

---

# Week 3 Verification Status

| Area                      | Status             |
| ------------------------- | ------------------ |
| Registration              | Verified           |
| Login                     | Verified           |
| Password hashing          | Verified           |
| Access JWT                | Verified           |
| Refresh JWT               | Verified           |
| JWT validation            | Verified           |
| Refresh-token persistence | Verified           |
| Refresh-token hashing     | Verified           |
| Refresh-token rotation    | Verified           |
| Refresh-token revocation  | Verified           |
| Logout                    | Verified           |
| Repository tests          | Verified           |
| Transaction rollback      | Verified           |
| Docker build              | Verified           |
| Identity container health | Verified           |
| PostgreSQL connectivity   | Verified           |
| Redis connectivity        | Verified           |
| Database migrations       | Verified           |
| OpenAPI                   | Final verification |
| E2E authentication        | Verified           |
| Week 3 PR                 | Final review       |
