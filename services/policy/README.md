# Policy Service

## Purpose

Evaluates authorization requests and manages access control using RBAC and ABAC policies.

---

## Team Ownership

**Squad:** Squad 4

**Lead:** Utkarsh Pratham

**Members:**
- Ayush Bind
- Narayanan Varadarajan

---

## Responsibilities

- RBAC
- ABAC
- Role Management
- Permission Evaluation
- Policy Engine
- Access Decisions

---

## APIs

| Method | Endpoint     | Description         |
|--------|--------------|---------------------|
| POST   | /evaluate    | Evaluate Permission |
| POST   | /roles       | Create Role         |
| GET    | /roles       | List Roles          |
| POST   | /permissions | Create Permission   |

---

## Database

PostgreSQL

---

## Dependencies

- Identity Service
- Organization Service

---

## Technology

- Python
- FastAPI

---

## Environment Variables

See `.env.example`