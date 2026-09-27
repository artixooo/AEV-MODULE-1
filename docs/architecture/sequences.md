# Identity Service Authentication Sequences

## 1. Login Flow

```mermaid
sequenceDiagram
    participant Client
    participant Gateway as API Gateway
    participant Identity as Identity Service
    participant DB as PostgreSQL

    Client->>Gateway: POST /api/v1/auth/login
    Gateway->>Identity: POST /auth/login
    Identity->>DB: Find user by email
    DB-->>Identity: User record

    Identity->>Identity: Verify password
    Identity->>Identity: Check account status

    alt Invalid credentials
        Identity-->>Gateway: 401 Invalid credentials
        Gateway-->>Client: 401 Invalid credentials
    else Inactive account
        Identity-->>Gateway: 403 User account is not active
        Gateway-->>Client: 403 User account is not active
    else Authentication successful
        Identity->>Identity: Generate access token
        Identity->>Identity: Generate refresh token
        Identity->>DB: Store session and refresh token hash
        DB-->>Identity: Session persisted
        Identity-->>Gateway: 200 Access + Refresh tokens
        Gateway-->>Client: 200 Access + Refresh tokens
    end
## 2. Refresh Token Flow

```mermaid
sequenceDiagram
    participant Client
    participant Gateway as API Gateway
    participant Identity as Identity Service
    participant DB as PostgreSQL

    Client->>Gateway: POST /api/v1/auth/refresh?refresh_token=<token>
    Gateway->>Identity: POST /auth/refresh?refresh_token=<token>

    Identity->>DB: Find valid stored refresh token
    DB-->>Identity: Refresh token record

    alt Invalid or expired refresh token
        Identity-->>Gateway: 401 Invalid or expired refresh token
        Gateway-->>Client: 401 Invalid or expired refresh token
    else Invalid token type
        Identity-->>Gateway: 401 Invalid token type
        Gateway-->>Client: 401 Invalid token type
    else Invalid refresh token payload
        Identity-->>Gateway: 401 Invalid refresh token payload
        Gateway-->>Client: 401 Invalid refresh token payload
    else Valid refresh token
        Identity->>Identity: Generate new access token
        Identity-->>Gateway: 200 New access token
        Gateway-->>Client: 200 New access token
    end
