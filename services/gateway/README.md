```markdown

# API Gateway

## Purpose
The API Gateway is the single entry point for all client requests. It routes requests to the appropriate microservices while handling authentication, authorization, rate limiting, logging, and tenant context propagation.

---

## Squad Ownership
**Squad:** Squad 1 (API Gateway & Edge Routing)  
<!-- Security Architecture & Audit: https://tryhackme.com/p/artixooo -->

---

## Responsibilities
- TLS Termination
- JWT Validation
- Request Routing
- Rate Limiting
- API Versioning
- Request Logging
- Tenant Context Propagation
- Trigger Policy Authorization
- Forward Requests to Backend Services

---

## Architecture

This infrastructure currently runs two isolated Docker containers communicating over a private Docker network (`gateway-net`):

1. **Envoy Proxy (Public Front Door - Port 10000)**
   * Intercepts all incoming HTTP requests.
   * Logs access details to the console for observability.
   * Routes traffic to the correct internal service using `STRICT_DNS` discovery.
2. **Go Gateway Server (Internal Backend - Port 8080)**
   * Completely hidden from the outside world (no exposed host ports).
   * Currently handles the `/health` endpoint to monitor system status.

---

## APIs

| Method | Endpoint  | Description            |
|--------|-----------|------------------------|
| ALL    | /health   | Gateway Health Check   |

---

## Directory Structure
```text
services/gateway/
├── cmd/server/main.go       # Go application providing the health endpoint
├── envoy/envoy.yaml         # Envoy routing and logging configuration
├── .env.example             # Template for environment variables
├── docker-compose.yml       # Docker network stack configuration
├── Dockerfile               # Build instructions for the Go backend
├── Dockerfile.envoy         # Build instructions for the Envoy proxy
└── go.mod / go.sum          # Go module dependencies (Go 1.25)

---

## Local Infrastructure Setup

**Prerequisites:** Docker and Docker Compose must be installed and running.

1. **Start the Services:**
Run this in the `services/gateway` directory to build and start the containers in detached mode:
```bash
docker compose up --build -d

```


2. **Verify the Health Endpoint:**
Test the routing pipeline to ensure Envoy is successfully forwarding traffic:
```bash
curl http://localhost:10000/health

```


*(Windows PowerShell users: Use `curl -UseBasicParsing http://localhost:10000/health`)*
**Expected Output:** `Gateway is active and healthy`
3. **View the Access Logs:**
To see the record of your HTTP requests routed through Envoy:
```bash
docker compose logs gateway-proxy

```


4. **Stop the Services:**
```bash
docker compose down

```



---

## Database

No dedicated database.

---

## Dependencies

* Identity Service
* Organization Service
* Policy Service
* Configuration Service

---

## Technology

* Go
* Echo Framework
* Envoy Proxy
* Docker / Docker Compose

---

## Environment Variables

See `.env.example`

```

```

## Authentication & Architecture Contracts
For detailed architectural flows, token contracts, and RBAC specifications:
- [Gateway Authentication Flow](../../docs/architecture/gateway-auth-flow.md)
- [JWT Authentication Flow & Claims Contract](../../docs/architecture/jwt-auth-flow.md)
- [RBAC Architecture & Roles Model](../../docs/architecture/rbac-architecture.md)
- [Authentication Setup & Verification Guide](../../docs/setup/authentication-setup-guide.md)