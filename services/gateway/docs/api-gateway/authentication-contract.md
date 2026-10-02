# API Gateway Authentication Contract

## Identity Service

### Docker Internal URL

http://identity:8000

### Local Host URL

http://localhost:8002

---

## JWT Configuration

Algorithm:

HS256

JWT secret:

Managed through environment configuration / Vault.
Never commit the actual secret to Git.

The API Gateway and Identity Service must use
the same JWT signing configuration.

---

## Authentication Header

Clients must send:

Authorization: Bearer <access_token>

---

## Public Endpoints

The following endpoints do not require authentication:

GET /health
GET /docs
GET /openapi.json
GET /redoc

Identity authentication/token endpoints should also remain
public where required for obtaining an access token.

---

## Protected Endpoints

Protected service routes require a valid JWT.

Examples:

/api/v1/organizations/*
/api/v1/policies/*
/api/v1/configuration/*
/api/v1/audit/*
/api/v1/secrets/*

---

## JWT Claims

The Gateway should validate and extract:

sub
tenant_id
roles
permissions
exp
iat
iss
aud

Only claims defined and issued by Identity should be trusted.

---

## Authentication Flow

Client
  |
  v
API Gateway
  |
  v
JWT Middleware
  |
  +-- Invalid/Missing Token --> 401
  |
  v
JWT Validation
  |
  v
Claim Extraction
  |
  v
Downstream Service

---

## Identity Flow

Client
  |
  v
API Gateway
  |
  v
Identity Service
  |
  v
Access Token
  |
  v
Client