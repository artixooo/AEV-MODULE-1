# Configuration Service: Tenant Identity Provider Configuration

## 1. Purpose

This document defines how the Configuration Service represents and manages
tenant-specific Identity Provider (IdP) configuration for the Identity Service.

**Core boundary:** Configuration Service stores tenant-scoped configuration
and references to secrets. Secrets Service stores the actual sensitive
values. Identity Service consumes the configuration.

The Configuration Service stores configuration metadata and non-sensitive
configuration values. Actual secrets and credentials must be stored in the
Secrets Service.

---

## 2. Scope

This Week 4 implementation covers:

1. Tenant configuration structure
2. Identity Provider configuration structure
3. Configuration validation
4. Tenant-scoped configuration retrieval
5. Tenant-scoped configuration updates
6. Cross-tenant isolation
7. Sensitive configuration detection
8. Secrets Service boundary
9. API documentation
10. Configuration Service tests

This implementation does **not** implement authentication flows (OIDC, OAuth,
SAML), SCIM provisioning logic, user authentication, token issuance, or IdP
login redirects — those belong to the Identity Service. The Configuration
Service only provides the configuration those components need.

---

## 3. Tenant Model

For Phase 1, `tenant` maps to the existing `organization_id` used by the
Configuration Service. **No separate Tenant entity is introduced for Week 4.**

organization_id
|
+-- configuration
+-- feature_flags
+-- configuration_history
+-- identity_provider_configuration


`tenant_id = organization_id` within this service. Conceptually the terms
may be used differently by other services, but within the Configuration
Service, `organization_id` is the source of truth for tenant isolation.

---

## 4. Tenant Configuration

Each configuration record must belong to exactly one organization.

```json
{
  "organization_id": "org-123",
  "key": "identity.provider",
  "value": {
    "provider_type": "oidc",
    "enabled": true
  }
}
```

Configuration belonging to one organization must never be returned to another
organization. A request authenticated for Organization A must only be able
to access Organization A's configuration.

---

## 5. Identity Provider Configuration — Generic Model

The IdP configuration is designed as a **generic and extensible** model — not
hard-coded to Okta, Auth0, or Azure AD. Supported provider types initially:
`oidc`, `oauth2`, `saml`. Future providers can be added without redesigning
the tenant configuration model.

**Recommended structure:**

```json
{
  "organization_id": "org-123",
  "provider": {
    "type": "oidc",
    "name": "company-oidc",
    "enabled": true,
    "issuer_url": "https://identity.example.com",
    "authorization_url": "https://identity.example.com/authorize",
    "token_url": "https://identity.example.com/token",
    "userinfo_url": "https://identity.example.com/userinfo",
    "jwks_url": "https://identity.example.com/.well-known/jwks.json",
    "client_id": "client-123",
    "client_secret_ref": "secret://identity/org-123/client-secret",
    "scopes": ["openid", "profile", "email"]
  }
}
```

The exact provider fields may vary depending on provider type. The
Configuration Service allows provider-specific optional fields while
maintaining validation for required/common fields.

---

## 6. Supported Provider Types

### OIDC
`provider_type`, `issuer_url`, `authorization_url`, `token_url`, `userinfo_url`, `jwks_url`, `client_id`, `client_secret_ref`, `scopes`

```json
{
  "type": "oidc",
  "issuer_url": "https://login.example.com",
  "authorization_url": "https://login.example.com/authorize",
  "token_url": "https://login.example.com/token",
  "userinfo_url": "https://login.example.com/userinfo",
  "jwks_url": "https://login.example.com/jwks",
  "client_id": "application-client-id",
  "client_secret_ref": "secret://identity/org-123/client-secret",
  "scopes": ["openid", "profile", "email"]
}
```

### OAuth 2.0
`provider_type`, `authorization_url`, `token_url`, `client_id`, `client_secret_ref`, `scopes`

```json
{
  "type": "oauth2",
  "authorization_url": "https://provider.example.com/authorize",
  "token_url": "https://provider.example.com/token",
  "client_id": "application-client-id",
  "client_secret_ref": "secret://identity/org-123/client-secret",
  "scopes": ["profile", "email"]
}
```

### SAML
`provider_type`, `entity_id`, `sso_url`, `certificate`, `metadata_url`, `signing_key_ref`

```json
{
  "type": "saml",
  "entity_id": "https://service.example.com/saml",
  "sso_url": "https://idp.example.com/sso",
  "metadata_url": "https://idp.example.com/metadata",
  "certificate": "-----BEGIN CERTIFICATE-----...",
  "signing_key_ref": "secret://identity/org-123/signing-key"
}
```

Private keys and other sensitive credentials must **not** be stored directly
in Configuration Service.

### SCIM
`type`, `base_url`, `enabled`, `token_ref`

```json
{
  "type": "scim",
  "base_url": "https://provider.example.com/scim",
  "enabled": true,
  "token_ref": "secret://identity/org-123/scim-token"
}
```

The actual SCIM token must be stored in the Secrets Service. The
Configuration Service stores only the reference.

---

## 7. Sensitive Configuration Boundary

**The Configuration Service must never store actual credentials or secrets.**
Sensitive values must be delegated to the Secrets Service.

| Configuration Service stores | Secrets Service stores |
|---|---|
| client_id, issuer_url, authorization_url, token_url, userinfo_url, jwks_url, scopes, provider_type, enabled, secret reference | client_secret, api_key, private_key, signing_key, SCIM token, access token, refresh token, password, credential material |

**Sensitive field list** (must be rejected if submitted directly):
`client_secret`, `clientSecret`, `api_key`, `apiKey`, `secret`, `password`,
`private_key`, `privateKey`, `signing_key`, `signingKey`, `access_token`,
`accessToken`, `refresh_token`, `refreshToken`, `scim_token`, `scimToken`

The exact implementation may use a normalized field-name comparison or a
controlled sensitive-field list. The important requirement is that sensitive
values must not be persisted in Configuration Service storage.

---

## 8. Secret Reference

Instead of storing:
```json
{ "client_secret": "super-secret-value" }
```

Store:
```json
{ "client_secret_ref": "secret://identity/org-123/client-secret" }
```

The reference identifies the secret stored by the Secrets Service. The
Configuration Service must not resolve the secret and persist the actual
value. The Identity Service uses the reference to obtain the secret through
the appropriate Secrets Service integration.

---

## 9. Secrets Service Boundary

             +----------------------+
             |   Identity Service   |
             +----------+-----------+
                        |
              Configuration lookup
                        |
                        v
             +----------------------+
             | Configuration Service|
             +----------+-----------+
                        |
                 secret reference
                        |
                        v
             +----------------------+
             |    Secrets Service   |
             +----------------------+
                        |
                  actual secret
                        |
                        v
                     Vault


Configuration Service holds: `"client_secret_ref": "secret://identity/org-123/client-secret"`
Secrets Service holds: the actual client secret behind that reference.

---

## 10. Validation Rules

**Common validation:**
- `organization_id` required, must identify a valid organization
- `provider type` required, must be one of `oidc`, `oauth2`, `saml`
- `enabled` required

**URL validation** — the following fields must contain valid URLs:
`issuer_url`, `authorization_url`, `token_url`, `userinfo_url`, `jwks_url`,
`metadata_url`, `sso_url`, `base_url`

Invalid: `"issuer_url": "not-a-url"`
Valid: `"issuer_url": "https://example.com"`

**Client ID validation:** `client_id` must not be empty when required by
the provider.

**Secret reference validation:** must identify a Secrets Service reference
(e.g. `secret://identity/org-123/client-secret`), not an actual value.

**Provider-specific required fields:**
- OIDC: `issuer_url`, `client_id`, `client_secret_ref`
- OAuth2: `authorization_url`, `token_url`, `client_id`, `client_secret_ref`
- SAML: `entity_id`, `sso_url`, `certificate` or `metadata_url`, `signing_key_ref`

The validation layer should remain extensible for future providers.

---

## 11. Tenant Isolation

Tenant isolation is a mandatory requirement. Every configuration operation
must be scoped by `organization_id`.

GET /configurations?organization_id=org-123


The service must ensure the caller is authorized to access `org-123`. A
request for `org-456` must never return `org-123`'s configuration.

**Example:**

Organization A = org-123 → provider = oidc, issuer = https://company-a.example.com
Organization B = org-456 → provider = saml, issuer = https://company-b.example.com

GET /configurations?organization_id=org-123 → only org-123 configuration
GET /configurations?organization_id=org-456 → only org-456 configuration


The service must never return both configurations to a single tenant-scoped
request.

---

## 12. Configuration Retrieval

Identity Service
|
| organization_id
v
Configuration Service
|
| tenant-scoped lookup
v
Configuration


**Example response:**
```json
{
  "organization_id": "org-123",
  "provider": {
    "type": "oidc",
    "enabled": true,
    "issuer_url": "https://identity.example.com",
    "client_id": "client-123",
    "client_secret_ref": "secret://identity/org-123/client-secret"
  }
}
```

Actual secret values must never appear in the response.

---

## 13. Configuration Update

Updates must also be tenant-scoped:

PUT /configurations/{configuration_id}

The service must verify the configuration belongs to the caller's
organization before updating it. A user belonging to `org-123` must not be
able to update `org-456`'s configuration.

---

## 14. Sensitive Field Handling

The API must reject or sanitize attempts to submit actual secret values.

**Bad request:**
```json
{ "client_id": "client-123", "client_secret": "super-secret" }
```
**Expected behavior:** `400 Bad Request` or an equivalent validation error.

**Client should instead provide:**
```json
{ "client_id": "client-123", "client_secret_ref": "secret://identity/org-123/client-secret" }
```

---

## 15. Database Considerations

Do **not** create a separate Tenant table for this task. Use the existing
organization-based configuration model. If a dedicated Identity Provider
configuration table is required, it should retain the organization
relationship:

identity_provider_configuration
id, organization_id, provider_type, provider_name,
enabled, configuration, created_at, updated_at


The exact implementation should follow existing Configuration Service
database conventions. If JSON/JSONB is already used for flexible
configuration values, provider-specific settings may reuse that mechanism
rather than introducing unnecessary schema duplication.

---

## 16. Responsibility Matrix

| Responsibility | Configuration Service | Identity Service | Secrets Service |
|---|---|---|---|
| Tenant configuration | Yes | Consume | No |
| Organization scoping | Yes | Yes | Yes |
| IdP configuration | Yes | Consume | No |
| OIDC authentication | No | Yes | No |
| OAuth authentication | No | Yes | No |
| SAML authentication | No | Yes | No |
| SCIM functionality | No | Yes | No |
| Client ID storage | Yes | Consume | No |
| Client secret storage | No | Consume | Yes |
| Private key storage | No | Consume | Yes |
| API key storage | No | Consume | Yes |
| Secret reference | Yes | Consume | Yes |
| Tenant isolation | Yes | Yes | Yes |

---

## 17. Implementation Guidance

1. **Reuse existing organization scoping** — do not introduce a new tenant entity for Week 4. Use `organization_id` as the tenant boundary.
2. **Keep provider configuration extensible** — avoid provider-specific database designs such as `okta_configuration`, `auth0_configuration`, `azure_configuration`. Prefer a generic provider model.
3. **Never store secrets** — use `*_ref` fields for credentials.
4. **Validate before persistence** — invalid provider configurations must be rejected before being stored.
5. **Enforce tenant isolation** — every read/update operation must enforce organization ownership.
6. **Do not implement authentication logic** — the Configuration Service provides configuration only; authentication belongs to the Identity Service.

---

**Note:** This document describes the security boundary and data model. It
must never contain real Vault tokens, client secrets, private keys, API keys,
or other actual credentials.

