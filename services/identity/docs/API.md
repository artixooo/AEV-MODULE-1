# Identity Service API Contracts v1

## Overview

The Identity Service provides authentication APIs for obtaining and refreshing JWT access tokens.

The API Gateway exposes these endpoints under the `/api/v1` prefix and forwards authentication requests to the Identity Service.

### Base URLs

Gateway (local):

`http://localhost:8080`

Identity Service (local):

`http://localhost:8002`

---

## Authentication

### POST /api/v1/auth/login

Authenticates a user using their email address and password.

Authentication is not required for this endpoint.

### Request

**Content-Type:** `application/json`

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

#### Request fields

| Field    | Type   | Required | Description        |
| -------- | ------ | -------- | ------------------ |
| email    | string | Yes      | User email address |
| password | string | Yes      | User password      |

### Successful response

**HTTP 200 OK**

```json
{
  "access_token": "<JWT access token>",
  "refresh_token": "<JWT refresh token>",
  "token_type": "bearer"
}
```

#### Response fields

| Field         | Type   | Description                    |
| ------------- | ------ | ------------------------------ |
| access_token  | string | JWT access token               |
| refresh_token | string | JWT refresh token              |
| token_type    | string | Token type, currently `bearer` |

### Error responses

#### 401 Unauthorized

Returned when the email does not exist or the password is incorrect.

```json
{
  "detail": "Invalid credentials"
}
```

#### 403 Forbidden

Returned when the user's account is not active.

```json
{
  "detail": "User account is not active"
}
```

---

## Refresh Access Token

### POST /api/v1/auth/refresh

Generates a new JWT access token using a valid refresh token.

Authentication is not required for this endpoint.

### Request

The refresh token is currently accepted as a **query parameter**.

```http
POST /api/v1/auth/refresh?refresh_token=<JWT refresh token>
```

### Successful response

**HTTP 200 OK**

```json
{
  "access_token": "<new JWT access token>",
  "token_type": "bearer"
}
```

#### Response fields

| Field        | Type   | Description                      |
| ------------ | ------ | -------------------------------- |
| access_token | string | Newly generated JWT access token |
| token_type   | string | Token type, currently `bearer`   |

### Error responses

#### 401 Unauthorized — Invalid or expired token

```json
{
  "detail": "Invalid or expired refresh token"
}
```

#### 401 Unauthorized — Invalid token type

```json
{
  "detail": "Invalid token type"
}
```

#### 401 Unauthorized — Invalid payload

```json
{
  "detail": "Invalid refresh token payload"
}
```

---

## Token Claims

The tokens generated during login contain:

```json
{
  "sub": "<user UUID>",
  "email": "user@example.com",
  "tenant_id": "<tenant UUID>"
}
```

The refresh token additionally contains:

```json
{
  "type": "refresh"
}
```

---

## Gateway Routing

The API Gateway exposes authentication routes under:

`/api/v1/auth/*`

These routes are public and are proxied to the Identity Service.

The Identity Service router uses the `/auth` prefix.

Therefore:

```text
Client
  |
  | POST /api/v1/auth/login
  v
API Gateway
  |
  | POST /auth/login
  v
Identity Service
```

For refresh:

```text
Client
  |
  | POST /api/v1/auth/refresh
  v
API Gateway
  |
  | POST /auth/refresh
  v
Identity Service
```

---

## Contract Status

**Version:** v1

**Status:** Implemented

This contract reflects the current Identity Service and API Gateway implementation. Any future changes to request or response fields, HTTP status codes, or endpoint paths must update this contract.