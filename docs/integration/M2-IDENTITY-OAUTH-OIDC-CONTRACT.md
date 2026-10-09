# Identity Service — OAuth 2.0 and OIDC Foundation Contract

## Purpose

This document defines the Week 4 OAuth 2.0 and OpenID Connect (OIDC)
foundation for the Identity Service.

The implementation provides provider configuration models, validation,
authorization URL construction, callback validation, and OIDC discovery
validation.

Provider credentials and secrets are not stored in the Identity database.
Only references to externally managed secrets are stored.

---

## Tenant Awareness

OAuth and OIDC provider configurations are tenant-scoped.

Each provider configuration contains:

- `tenant_id`
- `provider`

The database enforces uniqueness per tenant and provider:

`(tenant_id, provider)`

This allows different tenants to configure the same provider independently.

---

## OAuth 2.0 Provider Configuration

### Required fields

| Field | Type | Description |
|---|---|---|
| `tenant_id` | UUID | Owning tenant |
| `provider` | string | Provider identifier |
| `client_id` | string | OAuth client identifier |
| `client_secret_ref` | string | Reference to externally managed client secret |
| `authorization_url` | HTTPS URL | OAuth authorization endpoint |
| `token_url` | HTTPS URL | OAuth token endpoint |
| `redirect_uri` | HTTPS URL | Registered callback URI |
| `scopes` | string[] | Requested OAuth scopes |

### Security requirements

- OAuth endpoint URLs must use HTTPS.
- `client_secret_ref` contains only a secret reference.
- Actual client secrets must not be committed to source control.
- At least one OAuth scope is required.

Example:

```json
{
  "tenant_id": "00000000-0000-0000-0000-000000000001",
  "provider": "example-oauth",
  "client_id": "example-client-id",
  "client_secret_ref": "secret/oauth/example/client-secret",
  "authorization_url": "https://provider.example.com/oauth/authorize",
  "token_url": "https://provider.example.com/oauth/token",
  "redirect_uri": "https://identity.example.com/oauth/callback",
  "scopes": ["openid", "profile", "email"]
}
```

The values above are examples/placeholders only.

---

## OIDC Provider Configuration

### Required fields

| Field | Type | Description |
|---|---|---|
| `tenant_id` | UUID | Owning tenant |
| `provider` | string | Provider identifier |
| `issuer` | HTTPS URL | OIDC issuer |
| `client_id` | string | OIDC client identifier |
| `client_secret_ref` | string | Reference to externally managed client secret |
| `redirect_uri` | HTTPS URL | Registered callback URI |
| `scopes` | string[] | OIDC scopes |

`discovery_url` is optional.

If `discovery_url` is not supplied, it is derived as:

```text
{issuer}/.well-known/openid-configuration
```

OIDC configuration must include the `openid` scope.

Example:

```json
{
  "tenant_id": "00000000-0000-0000-0000-000000000001",
  "provider": "example-oidc",
  "issuer": "https://issuer.example.com",
  "client_id": "example-client-id",
  "client_secret_ref": "secret/oidc/example/client-secret",
  "redirect_uri": "https://identity.example.com/oidc/callback",
  "scopes": ["openid", "profile", "email"]
}
```

---

## API Foundation

### OAuth authorization

```text
POST /oauth/authorize
```

Current status: **Foundation/deferred integration**

`OAuthService.build_authorization_url()` can construct an authorization URL from a validated provider configuration.

The HTTP route currently returns `501 Not Implemented` because provider configuration lookup and secret/configuration infrastructure integration are not part of the current Week 4 foundation.

### OAuth callback

```text
POST /oauth/callback
```

The callback foundation validates:

- authorization code presence
- state presence and minimum length
- provider error responses

Token exchange and session creation are deferred.

### OIDC validation

```text
POST /oidc/validate
```

The endpoint validates an OIDC provider configuration and returns the derived discovery URL.

OIDC discovery validation also verifies that the issuer returned by the discovery document matches the configured issuer.

---

## Validation Rules

### OAuth

- Required provider fields must be present.
- URLs must be valid HTTP URLs and must use HTTPS.
- OAuth scopes cannot be empty.
- Callback state must be at least 16 characters.
- Callback authorization code is required.

### OIDC

- Required provider fields must be present.
- Issuer, redirect URI, and discovery URL must use HTTPS.
- The `openid` scope is mandatory.
- Discovery issuer must match the configured issuer.
- Discovery endpoints must use HTTPS.

---

## Database

The following Identity migrations provide persistence for the provider configuration models:

```text
004_create_oauth_provider_configs.sql
005_create_oidc_provider_configs.sql
```

The SQLAlchemy models are registered with the Identity application metadata and imported during application startup.

Identity migrations are executed through the existing custom migration runner during application startup.

---

## Secret Management

The Identity Service stores references rather than secret values.

Example:

```text
client_secret_ref = secret/oauth/example/client-secret
```

The actual secret is expected to remain in the project external secrets/configuration infrastructure.

No real client secrets, tokens, passwords, or provider credentials belong in this repository.

---

## Week 4 Scope

### Included

- Tenant-aware OAuth provider model
- Tenant-aware OIDC provider model
- OAuth/OIDC Pydantic schemas
- HTTPS URL validation
- Required-field validation
- OAuth authorization URL construction
- OAuth callback validation foundation
- OIDC discovery URL construction
- OIDC issuer validation
- OIDC discovery issuer matching
- Database migrations
- Unit tests for validation and service behavior

### Deferred

- Provider configuration CRUD/API
- Runtime tenant configuration lookup
- Configuration Service integration
- Secrets Service/Vault secret retrieval
- OAuth authorization redirect execution
- OAuth authorization-code token exchange
- OIDC authorization-code token exchange
- OAuth/OIDC state persistence and correlation storage
- Full external-provider login/session integration
- Production provider onboarding

These items can be implemented in subsequent integration work without changing the Week 4 foundation contract.
