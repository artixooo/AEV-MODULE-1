<div align="center">

# 🛡️ Policy Service — Pod Alpha (Squad 4)
### *Authorization Service — Week 1 Project Setup*

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20HA-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)

***

<p align="center">
  👑 <b>Squad Lead:</b> Utkarsh Pratham &nbsp;•&nbsp;
  ⚡ <b>Squad Member:</b> Narayanan Varadarajan &nbsp;•&nbsp;
  🌐 <b>Port:</b> <code>8002</code>
</p>

---

</div>

## ⚡ Scope — Issue #5 (Week 1)

The Policy Service will become the centralized authorization authority for the AEV Platform. **This PR covers only Week 1**: project setup and authorization database preparation. Authorization *logic* is Week 2 work and is tracked separately.

### ✅ Prepared / Verified (Week 1 — this PR)
- FastAPI project structure (`app/core`, `app/models`, `app/routers`, plus empty `app/api`, `app/middleware`, `app/schemas`, `app/services`, `app/utils` scaffolding matching the Identity and Organization services)
- Docker configuration (`Dockerfile`, `.dockerignore`)
- Dependencies (`requirements.txt`)
- Database migrations for the authorization schema, under the shared `database/policy/migrations/`
- SQLAlchemy ORM models (`app/models/policy_models.py`) mirroring the migration-defined schema: `Role`, `Permission`, `RolePermission`, `Policy`, `SoDPolicy`
- `/health` and `/ready` endpoints
- Test scaffold with boot/health/readiness tests

### 🔜 Planned / Future (Week 2 — separate PR)
- RBAC role/permission evaluation
- ABAC policy evaluation engine
- Segregation of Duties (SoD) conflict detection
- `/evaluate`, `/permissions`, `/policies`, `/sod-policies` endpoints
- Redis-backed decision caching and invalidation

---

## 🚀 Local Execution

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## 🧪 Tests

```bash
pytest tests/ -v
```

---

<div align="center">

<b>Squad 4 (Policy Service) • CyArt Tech LLP | AEV Platform (Pod Alpha)</b><br>
<i>Utkarsh Pratham (Squad Lead) & Narayanan Varadarajan (Squad Member)</i>

</div>
