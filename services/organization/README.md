# AEV Module 1 - POD Alpha

# Organization Service

The Organization Service is a FastAPI-based microservice responsible for organization-related functionality within the POD Alpha platform. It includes database connectivity, authentication, JWT validation, tenant context handling, authorization, health checks, readiness checks, and automated testing.

---

## Project Overview

POD Alpha is a microservices-based application consisting of multiple services that communicate through a shared backend network.

The Organization Service provides the following core capabilities:

- Organization service initialization
- PostgreSQL database connectivity
- JWT-based authentication
- Bearer token extraction
- JWT claim validation
- Tenant context creation
- Permission-based authorization
- Health monitoring
- Database readiness verification
- Automated unit testing

---

# Week 1 - Project and Service Foundation

## Objectives

Week 1 focused on establishing the basic Organization Service structure and ensuring that the service could be developed and executed independently.

## Completed Work

- Created the Organization Service structure.
- Configured the FastAPI application.
- Added application configuration.
- Added database configuration.
- Added SQLAlchemy database integration.
- Added PostgreSQL connectivity.
- Added service health endpoints.
- Added service readiness checks.
- Added initial application models and schemas.
- Added automated tests for the initial service components.
- Integrated the Organization Service into Docker Compose.

## Service Structure

The Organization Service follows a modular structure:

```text
services/organization/
├── app/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   └── service/application components
├── tests/
├── Dockerfile
├── requirements.txt
└── configuration files
```

Week 2 - Authentication, Tenant Context and Authorization
Objectives

Week 2 focused on implementing the security foundation required by the Organization Service.

The main areas were:

Authentication
JWT claims
Tenant context
Permission checking
Authorization
Authentication

The Organization Service uses Bearer token authentication.

The authentication flow is:

Receive an HTTP request.
Extract the Authorization header.
Verify that the authentication scheme is Bearer.
Extract the JWT.
Validate the JWT.
Validate required JWT claims.
Build the tenant context.
Continue the request when authorization requirements are satisfied.
JWT Authentication

JWT validation is implemented through the security layer.

The JWT validation process checks:

JWT signature
Configured signing algorithm
Token validity
Required sub claim
Token expiration
Invalid-token conditions

The service uses the configured JWT secret and algorithm rather than embedding authentication configuration directly into the authentication flow.

Tenant Context

The Organization Service creates a tenant context from JWT claims.

The tenant context contains:

User ID
Tenant ID

A JWT subject (sub) is required.

When a tenant ID is available, the tenant context reports that tenant information is available.

When a tenant ID is not included, the context remains valid but reports that tenant information is unavailable.

When the JWT does not contain a required subject, the context creation process rejects the request.

Authorization

The service implements permission-based authorization.

Permissions follow the organization permission format, for example:

organization:read
organization:write
organization:delete

The authorization layer supports:

Checking whether a permission exists.
Allowing requests with the required permission.
Rejecting requests that do not have the required permission.

Missing permissions result in HTTP 403 Forbidden.

Week 3 - Security Integration, Configuration and Verification
Objectives

Week 3 focused on completing the security integration and addressing configuration, testing, documentation, and service verification requirements.

Week 3 Changes
1. JWT Import Consistency

The authentication implementation was updated to use the JWT validation function provided by the security module.

The security layer provides:

Bearer token extraction
JWT claim validation
Authentication dependency handling

JWT validation is performed through:

validate_jwt_claims()

This resolved the previous mismatch between the authentication and security modules.

2. Environment-Based Database Configuration

Hardcoded PostgreSQL credentials were removed from docker-compose.yml.

The Organization Service now uses:

DATABASE_URL: ${DATABASE_URL}

Database credentials are supplied through environment configuration.

The PostgreSQL service uses environment variables for:

POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB

Local development configuration is maintained through .env.

The .env file contains environment-specific credentials and should not be committed to the repository.

3. Security Test Improvements

Security tests were expanded to verify:

Bearer token extraction
Missing authorization header
Invalid authorization scheme
Valid JWT validation
Invalid JWT rejection
Missing JWT subject rejection

Duplicate security coverage was cleaned up while preserving unique test coverage across:

test_security.py
test_context.py
test_authorization.py
4. README Documentation

The README was cleaned up so that it contains project documentation and verification evidence rather than Python test implementation code.

The documentation covers:

Week 1 work
Week 2 work
Week 3 work
Security architecture
Tenant context
Authorization
Environment configuration
Verification results

Week 3 Verification Evidence

The following verification was completed for the Organization Service.

1. Bearer Token Extraction

Verified that a valid Authorization header using the Bearer scheme correctly extracts the token.

Result: PASSED

Test:

test_bearer_token_extraction

2. JWT Validation

Verified that a correctly signed JWT can be decoded and validated using the configured JWT secret and algorithm.

Result: PASSED

Test:

test_valid_jwt_claims

3. Invalid JWT Rejection

Verified that an invalid JWT is rejected by the authentication layer.

Result: PASSED

Test:

test_invalid_jwt_is_rejected

4. Missing sub Claim Rejection

Verified that a JWT without the required sub claim is rejected.

Result: PASSED

Test:

test_jwt_missing_sub_is_rejected

5. Tenant Context Creation

Verified tenant context behavior for:

JWT containing a tenant ID
JWT without a tenant ID
JWT without the required subject

Result: PASSED

Verified behavior includes:

Correct user ID extraction
Correct tenant ID extraction
Tenant availability detection
Required subject validation
6. Permission Authorization

Verified that users with the required permission are allowed access.

Result: PASSED

Also verified that users without the required permission are rejected.

Result: PASSED

Expected denial response:

HTTP 403 Forbidden

Test:

test_require_permission_denies_access

Service Verification
Organization Container

The Organization Service was successfully started through Docker Compose.

The service exposes host port:

8003

which maps to the Organization Service application port:

8001

Docker Compose mapping:

8003:8001

Health Check

The Organization Service health endpoint was verified using:

GET /health

Result: HTTP 200 OK

Response:

{"status":"healthy","service":"organization-service"}

Readiness Check

The Organization Service readiness endpoint was verified using:

GET /ready

Result: HTTP 200 OK

Response:

{"status":"ready","database":"connected"}

This confirms that the Organization Service is running and can connect to the PostgreSQL database.

Automated Test Verification

The Organization Service test suite was executed using:

python -m pytest -v

Final Verification Result

23 passed in 4.95s

Full terminal output:

```text
============================================================================= test session starts =============================================================================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
collected 23 items

tests/test_authorization.py::test_permission_is_granted PASSED
tests/test_authorization.py::test_permission_is_denied PASSED
tests/test_authorization.py::test_require_permission_allows_access PASSED
tests/test_authorization.py::test_require_permission_denies_access PASSED
tests/test_config.py::TestConfig::test_config_loading PASSED
tests/test_config.py::TestConfig::test_custom_settings_instantiation PASSED
tests/test_context.py::test_build_tenant_context_with_tenant PASSED
tests/test_context.py::test_build_tenant_context_without_tenant PASSED
tests/test_context.py::test_build_tenant_context_requires_subject PASSED
tests/test_db.py::TestDatabase::test_db_setup PASSED
tests/test_db.py::TestDatabase::test_get_db_generator PASSED
tests/test_health.py::TestHealthEndpoints::test_health_endpoint PASSED
tests/test_health.py::TestHealthEndpoints::test_ready_endpoint PASSED
tests/test_health.py::TestHealthEndpoints::test_root_endpoint PASSED
tests/test_imports.py::TestImports::test_imports PASSED
tests/test_models_schemas.py::TestModelsAndSchemas::test_organization_model_instantiation PASSED
tests/test_models_schemas.py::TestModelsAndSchemas::test_organization_schemas PASSED
tests/test_security.py::test_bearer_token_extraction PASSED
tests/test_security.py::test_missing_authorization_header PASSED
tests/test_security.py::test_invalid_authorization_scheme PASSED
tests/test_security.py::test_valid_jwt_claims PASSED
tests/test_security.py::test_invalid_jwt_is_rejected PASSED
tests/test_security.py::test_jwt_missing_sub_is_rejected PASSED

============================================================================= 23 passed in 4.95s =============================================================================
```

**Result: 23/23 tests passed successfully.**
```text

Test coverage includes:

Authorization
Configuration
Tenant context
Database
Health checks
Imports
Models and schemas
Security
JWT validation
Bearer authentication

## Authentication & Architecture Contracts
For detailed architectural flows, token contracts, and RBAC specifications:
- [Gateway Authentication Flow](../../docs/architecture/gateway-auth-flow.md)
- [JWT Authentication Flow & Claims Contract](../../docs/architecture/jwt-auth-flow.md)
- [RBAC Architecture & Roles Model](../../docs/architecture/rbac-architecture.md)
- [Authentication Setup & Verification Guide](../../docs/setup/authentication-setup-guide.md)
