# Identity Service

The Identity Service provides authentication and identity capabilities for the AEV platform.

Current capabilities include:

- User management
- Authentication foundation
- JWT and refresh-token support
- Session management
- OAuth 2.0 foundation
- OpenID Connect (OIDC) foundation

## Infrastructure

- PostgreSQL connection configured through environment variables
- Redis connection configured through environment variables
- Redis connectivity verified during application startup
- Graceful Redis connection shutdown on application termination
- Identity database migrations executed during application startup

## Health Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Service status |
| GET | /health | Service health check |
| GET | /ready | Database/Redis readiness status |

## OAuth 2.0 and OIDC

Week 4 provides the OAuth 2.0 and OIDC foundation.

Provider configurations are tenant-aware through `tenant_id + provider`.

OAuth and OIDC configurations store only `client_secret_ref` values. Actual client secrets must remain in the external secrets/configuration infrastructure.

### OAuth

`POST /oauth/authorize`

`POST /oauth/callback`

The OAuth service can construct authorization URLs and validate callback payloads.

`/oauth/authorize` currently returns `501` because runtime provider configuration lookup and configuration/secrets infrastructure integration are deferred. This keeps the Week 4 implementation limited to the foundation layer.

### OIDC

`POST /oidc/validate`

OIDC configuration validation includes HTTPS enforcement, required-field validation, mandatory `openid` scope, discovery URL construction, and discovery issuer matching.

See `docs/integration/M2-IDENTITY-OAUTH-OIDC-CONTRACT.md` for the complete API contract and deferred-scope definition.

## Database Migrations

Identity migrations are stored under `database/identity/migrations/`.

OAuth/OIDC provider configuration migrations:

- `004_create_oauth_provider_configs.sql`
- `005_create_oidc_provider_configs.sql`

The application runs the Identity migration runner during startup.

## Testing

Run the OAuth/OIDC foundation tests:

```bash
python -m pytest -v tests/oauth tests/oidc
```

The tests cover valid provider configurations, required fields, HTTPS URL validation, OAuth authorization URL construction, OAuth callback validation, callback state validation, OIDC issuer validation, discovery URL construction, discovery issuer mismatch, and the required OIDC `openid` scope.

## Local Service Startup

```bash
uvicorn app.main:app --reload
```

PostgreSQL and Redis must be available before starting the Identity Service.

Do not place real passwords, client secrets, access tokens, or provider credentials in source code or configuration examples committed to the repository.
