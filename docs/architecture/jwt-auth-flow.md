```markdown
# JWT Authentication & Token Lifecycle Contract

## Overview
This document specifies the JSON Web Token (JWT) architecture, claim schema, cryptographic validation rules, and lifecycle controls enforced across the platform.

---

## Token Specifications

- **Signature Algorithm:** HMAC-SHA256 (`HS256`)
- **Access Token Expiry:** 30 minutes (1800 seconds)
- **Refresh Token Expiry:** 7 days
- **Issuer (`iss`):** `identity`
- **Audience (`aud`):** `gateway`

---

## Claims Schema

> **Implementation Status:** The current Identity Service implementation issues a basic JWT containing only `sub`, `iat`, and `exp`. The schema below represents the **target v1 contract** required for the upcoming RBAC integration.

```json
{
  "iss": "identity",
  "aud": "gateway",
  "sub": "usr_c48a73b2-7934-4b52-9bf0-b1d5952db71a",
  "tenant_id": "ten_91823ab4-8392-4f10-9c21-ef1294812a01",
  "roles": "admin",
  "permissions": "all",
  "iat": 1788873598,
  "exp": 1788877198
}

```

### Claim Definitions

| Claim | Type | Required | Description |
| --- | --- | --- | --- |
| `iss` | string | Yes | Must match `identity`. Rejects unauthorized issuers. |
| `aud` | string | Yes | Must match `gateway`. Rejects tokens not intended for edge ingress. |
| `sub` | string | Yes | Subject identifier representing the unique User UUID. |
| `tenant_id` | string | Yes | Unique Organization/Tenant UUID for multi-tenant isolation. |
| `roles` | string | Yes | Comma-delimited list of roles assigned to the user. |
| `permissions` | string | Yes | Permission scope or wildcard (`all`). |
| `iat` | int64 | Yes | Issued-at UNIX timestamp. Rejects tokens with future `iat`. |
| `exp` | int64 | Yes | Expiration UNIX timestamp. Rejects expired tokens. |

---

## Gateway Validation Pipeline

The Gateway evaluates tokens through a sequential validation pipeline:

1. **Header Extraction:** Extracts the bearer token from `Authorization: Bearer <token>`. Returns `401 Unauthorized` if missing or malformed.
2. **Signature Verification:** Validates the signature against `JWT_SECRET_KEY`.
3. **Issuer & Audience Check:** Verifies `iss == "identity"` and `aud == "gateway"`.
4. **Time Boundaries:** Verifies `exp > time.Now()` and `iat <= time.Now()`.
5. **Context Injection:** Extracts verified claims into standard HTTP headers for downstream propagation.

```

```