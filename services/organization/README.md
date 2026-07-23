# Organization Service

## Purpose

Manages organizations, workspaces, projects, tenant hierarchy, and user memberships for multi-tenant environments.

---

## Team Ownership

**Squad:** Squad 3

**Lead:** Anubhav Dubey

**Members:**
- Angu Raksha Saravanan
- Bhavnish Koli

---

## Responsibilities

- Organization Management
- Workspace Management
- Project Management
- Tenant Hierarchy
- User Membership
- Tenant Isolation

---

## APIs

| Method | Endpoint       | Description         |
|--------|----------------|---------------------|
| POST   | /organizations | Create Organization |
| GET    | /organizations | List Organizations  |
| POST   | /workspaces    | Create Workspace    |
| POST   | /projects      | Create Project      |
| POST   | /members       | Add Member          |

---

## Database

PostgreSQL

---

## Dependencies

- Identity Service

---

## Technology

- Python
- FastAPI
- PostgreSQL

---

## Environment Variables

See `.env.example`