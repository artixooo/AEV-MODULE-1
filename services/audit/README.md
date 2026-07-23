# Audit Service

## Purpose

Captures immutable audit events from all services to provide compliance, traceability, and security monitoring.

---

## Team Ownership

**Squad:** Squad 6

**Lead:** Bhumika Ghimire

**Members:**
- Sumedha Shree

---

## Responsibilities

- Immutable Audit Logs
- Kafka Consumer
- Hash Chaining
- Compliance Reporting
- Log Search
- Audit Verification

---

## APIs

| Method | Endpoint   | Description       |
|--------|------------|-------------------|
| GET    | /logs      | List Audit Logs   |
| GET    | /logs/{id} | Get Audit Record  |
| GET    | /search    | Search Audit Logs |

---

## Database

PostgreSQL

---

## Dependencies

- Kafka
- All Services (consume audit events)

---

## Technology

- Go
- PostgreSQL
- Kafka

---

## Environment Variables

See `.env.example`