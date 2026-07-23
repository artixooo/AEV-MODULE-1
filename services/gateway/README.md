# API Gateway

## Purpose

The API Gateway is the single entry point for all client requests. It routes requests to the appropriate microservices while handling authentication, authorization, rate limiting, logging, and tenant context propagation.

---

## Team Ownership

**Squad:** Squad 1

**Lead:** Shubhradeep Paul

**Members:**
- Rohit Bapu S B
- Sulaiba Saania

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

## APIs

| Method | Endpoint  | Description            |
|--------|-----------|------------------------|
| ALL    | /api/v1/* | Routes client requests |
| ALL    | /health   | Gateway Health Check   |

---

## Database

No dedicated database.

---

## Dependencies

- Identity Service
- Organization Service
- Policy Service
- Configuration Service

---

## Technology

- Go
- Echo Framework
- Envoy Proxy

---

## Environment Variables

See `.env.example`