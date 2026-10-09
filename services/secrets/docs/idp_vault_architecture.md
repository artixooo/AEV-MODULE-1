# Identity Provider (IdP) Secret Architecture & Tenant Isolation

## 1. Overview
This document specifies the Vault storage architecture, path naming conventions, and tenant isolation policies for external Identity Provider credentials (OAuth 2.0, OpenID Connect, SAML 2.0).

---

## 2. Vault Path Conventions & Naming Standard

All external provider secrets are stored under the KV version 2 secret engine using the normalized path hierarchy:

```text
secret/data/tenants/{tenant_id}/idp/{provider_type}