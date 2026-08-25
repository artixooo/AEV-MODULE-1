# Audit Service

## Overview

The Audit Service provides the infrastructure foundation for audit event processing in the AEV Platform.

The Week 2 implementation focuses on service configuration, PostgreSQL connectivity, Kafka connectivity/configuration, health verification, Docker networking, and service startup.

Audit event consumption, event processing, persistence workflows, and audit APIs are planned for future milestones and are not implemented as part of Week 2.

---

## Week 2 Scope

### Configured / Verified

- Go module and service dependencies
- Environment-based configuration
- PostgreSQL configuration and connectivity
- Kafka configuration and connectivity
- `/health` endpoint
- Docker configuration
- Docker networking
- Service startup

### Not Implemented in Week 2

- Kafka event consumer
- Kafka event processing
- Audit event persistence/business workflows
- Audit log retrieval APIs
- Audit log search APIs
- Hash-chain processing
- Audit event business logic

---

## Project Structure

```text
services/audit/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── config/
│   ├── handlers/
│   └── repository/
├── .env.example
├── Dockerfile
├── go.mod
├── go.sum
└── README.md


---

© AEV Module 1 – Audit Service
