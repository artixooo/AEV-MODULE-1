# Secrets Service

## Purpose

Provides secure storage and lifecycle management of secrets using HashiCorp Vault.

---

## Team Ownership

**Squad:** Squad 5

**Lead:** Bezawada Kushal Ram

**Members:**
- Adhithyan Biju

---

## Responsibilities

- Vault Integration
- Secret Storage
- Secret Rotation
- Dynamic Credentials
- Encryption Keys
- Secret Leasing

---

## APIs

| Method | Endpoint      | Description     |
|--------|---------------|-----------------|
| POST   | /secrets      | Store Secret    |
| GET    | /secrets/{id} | Retrieve Secret |
| PUT    | /rotate       | Rotate Secret   |

---

## Database

HashiCorp Vault

---

## Dependencies

- Identity Service

---

## Technology

- Python
- FastAPI
- HashiCorp Vault

---

## Environment Variables

See `.env.example`