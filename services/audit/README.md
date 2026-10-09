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

# Week 3 Status

- Go
- PostgreSQL
- Apache Kafka
- Docker

---

# Kafka Integration

Audit Service consumes audit events published by platform services.

Future implementation will include:

- Event consumer
- Topic subscription
- Dead Letter Queue support
- Retry handling

---

# Database

Database Engine:

- PostgreSQL

Migration Scripts:

- 001_create_audit_logs.sql
- 002_create_audit_events.sql
- 003_create_hash_chain.sql

---

# Hash Chain

The Audit Service maintains cryptographic integrity through hash chaining.

Future implementation:

- Previous hash linking
- SHA-256 hashing
- Chain validation
- Tamper detection

---

# REST APIs

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /logs | Retrieve audit logs |
| GET | /logs/{id} | Retrieve specific audit record |
| GET | /search | Search audit records |

---

# Environment Variables

| Variable | Description |
|----------|-------------|
| PORT | Port on which the Audit Service runs |
| DB_HOST | PostgreSQL database host |
| DB_PORT | PostgreSQL database port |
| DB_NAME | Audit database name |
| KAFKA_BROKER | Kafka broker address |
| KAFKA_TOPIC | Kafka topic for audit events |

Example:

```env
PORT=8081

DB_HOST=postgres
DB_PORT=5432
DB_NAME=audit

KAFKA_BROKER=kafka:9092
KAFKA_TOPIC=audit-events
```

---

# Docker

Dockerfile included for containerized deployment.

Build:

```bash
docker build -t audit-service .
```

Run:

```bash
docker run -p 8081:8081 audit-service
```

The Audit Service will be available at:

```
http://localhost:8081
```

---

# Week 2 Status

- PostgreSQL connection configured and verified
- Kafka connectivity configured and verified
- Environment variables configured
- Project settings configured
- `/health` endpoint implemented and verified
- Docker networking verified
- Audit Service startup verified

# Future Scope

As specified in **Issue #7 – Week 1: Audit Service Project Setup & Kafka Infrastructure Preparation**, the following functionality is intentionally deferred to Week 2 and later milestones:

- Kafka event processing
- Audit event persistence
- Hash chain generation
- Business logic implementation
- Search engine implementation
- REST API implementation
- Authentication
- Authorization
- Monitoring
- Metrics

---

# Team

Squad 6

Lead

- Pod Alpha Security Engineering

Members

- Pod Alpha Security Engineering

---

# Week 1 Status

| Component | Status |
|----------|--------|
| Folder Structure | Complete |
| Docker | Verified |
| Kafka | Verified |
| Migrations | Verified |
| Repository Layer | Prepared |
| Handler Layer | Prepared |
| Hash Chain | Prepared |
| Documentation | Updated |
| Tests | Prepared |

---

© AEV Module 1 – Audit Service
| Deliverable | Status |
|---|---|
| Authentication Event Schema | Complete |
| Audit Event Model | Complete |
| Kafka Configuration | Complete |
| Kafka Connectivity | Verified |
| Database Connectivity | Verified |
| API Documentation | Complete |
| README | Updated |
