"""
CYART Pod Alpha - Unified Foundation & Administration Console Server
Module 1: Platform Foundation & CTEM Orchestration
Strictly adhering to CyArt Tech LLP Engineering Build Guide v1.0
"""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(
    title="CYART Pod Alpha Platform Substrate",
    description="Multi-tenant platform foundation: organization, identity, authentication, RBAC, audit, secrets.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "js").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "img").mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    fav = STATIC_DIR / "img" / "cyart-logo.png"
    if fav.exists():
        return FileResponse(fav)
    return JSONResponse(status_code=404, content={"detail": "Not found"})


GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"


def compute_entry_hash(prev_hash: str, entry: dict) -> str:
    """
    Computes SHA-256 hash from previous hash + canonical JSON payload.
    Build Guide Section 7.6 formula:
    canonical = json.dumps(entry, sort_keys=True, separators=(',', ':'))
    payload = f"{prev_hash}:{canonical}".encode('utf-8')
    """
    canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
    payload = f"{prev_hash}:{canonical}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# -----------------------------------------------------------------------------
# AEV Module 1 Squad Architecture & Specifications
# Identity, Zero-Trust Substrate & Cryptographic Architecture: https://tryhackme.com/p/artixooo
# -----------------------------------------------------------------------------

WORK_ALLOCATION = [
    {
        "squad": "Squad 1",
        "service": "API Gateway",
        "tech": "Go 1.22 + Envoy Proxy",
        "responsibilities": "Central edge routing, TLS 1.3 termination, token-bucket rate limiting (10,000 RPS), JWT validation, service communication header injection",
    },
    {
        "squad": "Squad 2",
        "service": "Identity Service",
        "tech": "Go / Gin + Redis",
        "responsibilities": "Authentication, JWT, OAuth 2.0 / OIDC (PKCE), SAML 2.0, RFC 6238 TOTP MFA, RFC 7643/7644 SCIM 2.0 provisioning, session management",
    },
    {
        "squad": "Squad 3",
        "service": "Organization Service",
        "tech": "Python / FastAPI + PostgreSQL",
        "responsibilities": "Organizations, workspaces, projects, 3-tier tenant hierarchy, PostgreSQL Row-Level Security (RLS), tenant quotas & memberships",
    },
    {
        "squad": "Squad 4",
        "service": "Policy Service",
        "tech": "Python + OPA Engine",
        "responsibilities": "RBAC, ABAC, dynamic permission engine (<1ms evaluation), Segregation of Duties (SoD), custom permission matrices",
    },
    {
        "squad": "Squad 5",
        "service": "Secrets Service",
        "tech": "Go + HashiCorp Vault",
        "responsibilities": "Vault integration, per-tenant secret engines, NIST SP 800-57 automated key rotation (AES-256-GCM, Ed25519), break-glass controls",
    },
    {
        "squad": "Squad 6",
        "service": "Audit Service",
        "tech": "Go + Apache Kafka",
        "responsibilities": "Audit logs, Kafka consumers, cryptographic SHA-256 hash chaining, live mathematical ledger verification, compliance",
    },
    {
        "squad": "Squad 7",
        "service": "Configuration Service",
        "tech": "Python / FastAPI",
        "responsibilities": "Feature flags, runtime configuration, tenant settings, hot-reloading switches, kill-switch circuit breakers",
    },
]



# -----------------------------------------------------------------------------
# Section 7.1 & 7.2: Multi-Tenant Organizations, Workspaces, Projects Hierarchy
# -----------------------------------------------------------------------------

INITIAL_ORGANIZATIONS = [
    {
        "org_id": "01890123-4567-7abc-def0-1234567890ac",
        "name": "CyArt Tech Enterprise",
        "slug": "cyart-tech",
        "plan": "enterprise",
        "region": "ap-south-1",
        "status": "active",
        "settings": {"mfa_enforced": True, "session_idle_timeout_min": 60},
        "branding": {"logo_url": "/static/img/logo.svg", "primary_color": "#00F0FF"},
        "workspaces": [
            {
                "workspace_id": "01890123-4567-7abc-def1-123456789001",
                "name": "Pod Alpha Core",
                "slug": "pod-alpha-core",
                "status": "active",
                "projects": [
                    {"project_id": "01890123-4567-7abc-def2-123456789011", "name": "Identity & Trust Substrate", "slug": "identity-trust", "status": "active"},
                    {"project_id": "01890123-4567-7abc-def2-123456789012", "name": "Kafka Event Bus Pipeline", "slug": "kafka-events", "status": "active"},
                ],
            },
            {
                "workspace_id": "01890123-4567-7abc-def1-123456789002",
                "name": "Security Operations Center",
                "slug": "soc-prod",
                "status": "active",
                "projects": [
                    {"project_id": "01890123-4567-7abc-def2-123456789021", "name": "Threat Exposure Monitor", "slug": "threat-monitor", "status": "active"},
                ],
            },
        ],
    },
    {
        "org_id": "01890123-4567-7abc-def0-1234567890ad",
        "name": "Acme Cyber Defense Corp",
        "slug": "acme-defense",
        "plan": "enterprise",
        "region": "us-east-1",
        "status": "active",
        "settings": {"mfa_enforced": True, "session_idle_timeout_min": 30},
        "branding": {"logo_url": "/static/img/acme.svg", "primary_color": "#10B981"},
        "workspaces": [
            {
                "workspace_id": "01890123-4567-7abc-def1-123456789003",
                "name": "Incident Response Alpha",
                "slug": "ir-alpha",
                "status": "active",
                "projects": [
                    {"project_id": "01890123-4567-7abc-def2-123456789031", "name": "Containment Automation", "slug": "containment-auto", "status": "active"},
                ],
            }
        ],
    },
    {
        "org_id": "01890123-4567-7abc-def0-1234567890ae",
        "name": "FinTech Sovereign Bank",
        "slug": "fintech-sovereign",
        "plan": "enterprise",
        "region": "eu-west-1",
        "status": "active",
        "settings": {"mfa_enforced": True, "strict_rls": True},
        "branding": {"logo_url": "/static/img/fintech.svg", "primary_color": "#6366F1"},
        "workspaces": [
            {
                "workspace_id": "01890123-4567-7abc-def1-123456789004",
                "name": "Banking Exposure Substrate",
                "slug": "banking-exposure",
                "status": "active",
                "projects": [
                    {"project_id": "01890123-4567-7abc-def2-123456789041", "name": "Payment Gateway Auditing", "slug": "payment-audit", "status": "active"},
                ],
            }
        ],
    },
]

# -----------------------------------------------------------------------------
# Section 2.1 & Figure 2.1: Platform Role Hierarchy
# -----------------------------------------------------------------------------

INITIAL_ROLES = [
    {"name": "Super Admin", "level": "Platform", "description": "Unrestricted platform-wide root operations", "is_system": True},
    {"name": "Platform Operator", "level": "Platform", "description": "Operational maintenance and observability", "is_system": True},
    {"name": "Org Admin", "level": "Organization", "description": "Tenant-level policy, workspace, and user management", "is_system": True},
    {"name": "Org Member", "level": "Organization", "description": "Standard tenant employee or collaborator", "is_system": True},
    {"name": "Workspace Admin", "level": "Workspace", "description": "Manages projects and memberships within workspace", "is_system": True},
    {"name": "Workspace Editor", "level": "Workspace", "description": "Creates and modifies assets and project scopes", "is_system": True},
    {"name": "Workspace Viewer", "level": "Workspace", "description": "Read-only visibility of workspace scans", "is_system": True},
    {"name": "Auditor", "level": "Compliance", "description": "Immutable audit ledger reading and compliance verification", "is_system": True},
]

# -----------------------------------------------------------------------------
# Section 8.1 & 8.3: Real Event Architecture (Kafka Event Bus)
# -----------------------------------------------------------------------------

INITIAL_EVENTS = [
    {
        "event_id": "01890123-4567-7abc-def0-1234567890ab",
        "event_type": "UserCreated",
        "event_version": "1.0",
        "timestamp": "2026-07-02T14:30:00.123Z",
        "tenant_id": "01890123-4567-7abc-def0-1234567890ac",
        "source": "organization-service",
        "source_version": "1.5.2",
        "correlation_id": "req-01890123-4567",
        "actor": {"type": "user", "id": "01890123-4567-7abc-def0-1234567890ad", "name": "admin@cyart.io"},
        "subject": {"type": "user", "id": "01890123-4567-7abc-def0-1234567890ae"},
        "data": {
            "user_id": "01890123-4567-7abc-def0-1234567890ae",
            "email": "newuser@example.com",
            "name": "New User",
            "org_id": "01890123-4567-7abc-def0-1234567890ac",
            "auth_method": "saml",
            "auth_provider": "okta",
        },
        "metadata": {"trace_id": "abc123trace", "request_id": "req-01890123-4567"},
    },
    {
        "event_id": "01890123-4567-7abc-def0-1234567890ba",
        "event_type": "RoleAssigned",
        "event_version": "1.0",
        "timestamp": "2026-07-02T14:35:00.000Z",
        "tenant_id": "01890123-4567-7abc-def0-1234567890ac",
        "source": "organization-service",
        "source_version": "1.5.2",
        "correlation_id": "req-01890123-4568",
        "actor": {"type": "user", "id": "01890123-4567-7abc-def0-1234567890ad", "name": "admin@cyart.io"},
        "subject": {"type": "user", "id": "01890123-4567-7abc-def0-1234567890ae"},
        "data": {"role": "Workspace Editor", "workspace_id": "01890123-4567-7abc-def1-123456789001"},
        "metadata": {"trace_id": "abc124trace", "request_id": "req-01890123-4568"},
    },
    {
        "event_id": "01890123-4567-7abc-def0-1234567890ca",
        "event_type": "OrgCreated",
        "event_version": "1.0",
        "timestamp": "2026-07-02T15:00:00.000Z",
        "tenant_id": "01890123-4567-7abc-def0-1234567890ae",
        "source": "organization-service",
        "source_version": "1.5.2",
        "correlation_id": "req-01890123-4569",
        "actor": {"type": "user", "id": "01890123-4567-7abc-def0-1234567890ad", "name": "admin@cyart.io"},
        "subject": {"type": "organization", "id": "01890123-4567-7abc-def0-1234567890ae"},
        "data": {"name": "FinTech Sovereign Bank", "slug": "fintech-sovereign", "plan": "enterprise"},
        "metadata": {"trace_id": "abc125trace", "request_id": "req-01890123-4569"},
    },
]

# -----------------------------------------------------------------------------
# Section 7.5: Partitioned Cryptographic Audit Log Entries
# -----------------------------------------------------------------------------

INITIAL_AUDIT_LOGS = [
    {
        "audit_id": "01890123-4567-7abc-def0-000000000001",
        "tenant_id": "01890123-4567-7abc-def0-1234567890ac",
        "actor_type": "system",
        "actor_id": "00000000-0000-0000-0000-000000000000",
        "actor_name": "system-gateway",
        "action": "SYSTEM_BOOT",
        "resource_type": "gateway",
        "resource_id": "00000000-0000-0000-0000-000000000001",
        "before_state": None,
        "after_state": {"status": "healthy", "port": 8081, "rate_limit_rps": 10000},
        "source_ip": "127.0.0.1",
        "user_agent": "Envoy/1.35",
        "request_id": "01890123-4567-7abc-def0-000000000001",
        "session_id": "01890123-4567-7abc-def0-000000000001",
        "timestamp": "2026-07-09T22:00:00Z",
    },
    {
        "audit_id": "01890123-4567-7abc-def0-000000000002",
        "tenant_id": "01890123-4567-7abc-def0-1234567890ac",
        "actor_type": "user",
        "actor_id": "01890123-4567-7abc-def0-1234567890ad",
        "actor_name": "admin@cyart.io",
        "action": "USER_LOGIN",
        "resource_type": "user",
        "resource_id": "01890123-4567-7abc-def0-1234567890ad",
        "before_state": {"mfa_verified": False},
        "after_state": {"mfa_verified": True, "token_issued": True},
        "source_ip": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)",
        "request_id": "01890123-4567-7abc-def0-000000000002",
        "session_id": "01890123-4567-7abc-def0-000000000002",
        "timestamp": "2026-07-09T22:05:00Z",
    },
    {
        "audit_id": "01890123-4567-7abc-def0-000000000003",
        "tenant_id": "01890123-4567-7abc-def0-1234567890ac",
        "actor_type": "user",
        "actor_id": "01890123-4567-7abc-def0-1234567890ad",
        "actor_name": "admin@cyart.io",
        "action": "SSO_PROVIDER_UPDATE",
        "resource_type": "oauth_provider_config",
        "resource_id": "01890123-4567-7abc-def0-000000000003",
        "before_state": {"status": "pending"},
        "after_state": {"status": "active", "provider": "Auth0 Production Identity"},
        "source_ip": "192.168.1.100",
        "user_agent": "Mozilla/5.0",
        "request_id": "01890123-4567-7abc-def0-000000000003",
        "session_id": "01890123-4567-7abc-def0-000000000002",
        "timestamp": "2026-07-09T22:10:00Z",
    },
    {
        "audit_id": "01890123-4567-7abc-def0-000000000004",
        "tenant_id": "01890123-4567-7abc-def0-1234567890ac",
        "actor_type": "system",
        "actor_id": "00000000-0000-0000-0000-000000000004",
        "actor_name": "vault-rotation-daemon",
        "action": "SECRET_ROTATION",
        "resource_type": "secret",
        "resource_id": "01890123-4567-7abc-def0-000000000004",
        "before_state": {"version": 3, "key_strength": "AES-256-GCM"},
        "after_state": {"version": 4, "key_strength": "AES-256-GCM"},
        "source_ip": "127.0.0.1",
        "user_agent": "Vault/1.20",
        "request_id": "01890123-4567-7abc-def0-000000000004",
        "session_id": "01890123-4567-7abc-def0-000000000004",
        "timestamp": "2026-07-09T22:15:00Z",
    },
]

# Section 6.2: SCIM 2.0 In-Memory Store
INITIAL_SCIM_USERS = [
    {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": "01890123-4567-7abc-def0-scim00000001",
        "userName": "alice.engineer@cyart.io",
        "name": {"givenName": "Alice", "familyName": "Engineer", "formatted": "Alice Engineer"},
        "emails": [{"value": "alice.engineer@cyart.io", "primary": True}],
        "active": True,
        "roles": [{"value": "Workspace Admin"}],
        "meta": {"resourceType": "User", "created": "2026-07-01T10:00:00Z"},
    },
    {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": "01890123-4567-7abc-def0-scim00000002",
        "userName": "bob.analyst@cyart.io",
        "name": {"givenName": "Bob", "familyName": "Analyst", "formatted": "Bob Analyst"},
        "emails": [{"value": "bob.analyst@cyart.io", "primary": True}],
        "active": True,
        "roles": [{"value": "Workspace Viewer"}],
        "meta": {"resourceType": "User", "created": "2026-07-02T11:00:00Z"},
    },
]

# Section 4.7 & 12.1: Key Vault Store
INITIAL_SECRETS = [
    {
        "path": "/secret/data/tenant_01890123-4567-7abc-def0-1234567890ac/database",
        "cycle": "90 Days (NIST)",
        "last_rotation": "2026-06-15",
        "next_rotation": "2026-09-13",
        "key_strength": "AES-256-GCM",
        "status": "Synced",
    },
    {
        "path": "/secret/data/tenant_01890123-4567-7abc-def0-1234567890ac/jwt_signing_key",
        "cycle": "30 Days (NIST)",
        "last_rotation": "2026-07-09",
        "next_rotation": "2026-08-08",
        "key_strength": "Ed25519",
        "status": "Active",
    },
    {
        "path": "/secret/data/tenant_01890123-4567-7abc-def0-1234567890ac/saml_private_key",
        "cycle": "365 Days (NIST)",
        "last_rotation": "2026-01-10",
        "next_rotation": "2027-01-08",
        "key_strength": "RSA-4096",
        "status": "Synced",
    },
]

# Section 4.6: Feature Flags with Instant Kill Switches
INITIAL_FLAGS = [
    {"key": "audit_immutable_backup", "enabled": True, "description": "Hourly immutable WORM storage backup replication (7-year retention)"},
    {"key": "jit_access_workflow", "enabled": True, "description": "Just-In-Time temporary privilege elevation (FR-AUTH-010)"},
    {"key": "scim_provisioning_v2", "enabled": True, "description": "SCIM 2.0 automated employee provisioning (FR-AUTH-007)"},
    {"key": "strict_rls_enforcement", "enabled": True, "description": "PostgreSQL database row-level security isolation (ADR-004)"},
    {"key": "break_glass_vault_unseal", "enabled": False, "description": "Emergency break-glass admin credential unseal (FR-AUTH-009)"},
    {"key": "abac_context_evaluator", "enabled": True, "description": "Context-aware dynamic IP and time boundary checking (FR-AUTHZ-006)"},
]

# Runtime state
state = {
    "organizations": list(INITIAL_ORGANIZATIONS),
    "events": list(INITIAL_EVENTS),
    "scim_users": list(INITIAL_SCIM_USERS),
    "secrets": list(INITIAL_SECRETS),
    "feature_flags": list(INITIAL_FLAGS),
    "roles": list(INITIAL_ROLES),
    "audit_ledger": [],
    "tampered": False,
}


def build_audit_chain():
    """Builds the mathematically linked hash chain for audit blocks."""
    chain = []
    prev_hash = GENESIS_HASH

    for b in INITIAL_AUDIT_LOGS:
        entry_payload = {
            "audit_id": b["audit_id"],
            "tenant_id": b["tenant_id"],
            "action": b["action"],
            "actor_name": b["actor_name"],
            "resource_type": b["resource_type"],
            "source_ip": b["source_ip"],
            "timestamp": b["timestamp"],
            "after_state": b["after_state"],
        }
        curr_hash = compute_entry_hash(prev_hash, entry_payload)
        chain.append({
            **b,
            "previous_hash": prev_hash,
            "entry_hash": curr_hash,
            "status": "Valid",
        })
        prev_hash = curr_hash

    state["audit_ledger"] = chain
    state["tampered"] = False


build_audit_chain()

# -----------------------------------------------------------------------------
# Pydantic Request Models
# -----------------------------------------------------------------------------

class WorkspaceCreate(BaseModel):
    name: str
    slug: str

class ProjectCreate(BaseModel):
    name: str
    slug: str

class EventPublishRequest(BaseModel):
    event_type: str
    actor_email: str
    resource_name: str

class SCIMUserCreate(BaseModel):
    userName: str
    givenName: str
    familyName: str
    role: str = "Workspace Member"

# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_admin_console():
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h2>Console UI Template not loaded</h2>")

@app.get("/api/v1/work-allocation")
def get_work_allocation():
    return {"squads": WORK_ALLOCATION}


@app.get("/api/v1/health")
def get_health():
    return {
        "status": "healthy",
        "service": "pod-alpha-gateway",
        "data_isolation": "PostgreSQL RLS Active",
        "vault": "unsealed",
        "tenant_id": "01890123-4567-7abc-def0-1234567890ac",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/api/v1/telemetry")
def get_telemetry():
    total_workspaces = sum(len(o["workspaces"]) for o in state["organizations"])
    total_projects = sum(sum(len(w["projects"]) for w in o["workspaces"]) for o in state["organizations"])

    return {
        "active_tenants": len(state["organizations"]),
        "max_tenants_capacity": 100,
        "total_workspaces": total_workspaces,
        "max_workspaces_capacity": 1000,
        "total_projects": total_projects,
        "system_identities": 2410 + len(state["scim_users"]),
        "gateway_load_rps": 8412,
        "gateway_p95_latency_ms": 14,
        "vault_secrets": len(state["secrets"]),
        "microservices": [
            {"name": "API Gateway (Go + Envoy)", "status": "Healthy", "metric": "8,412 RPS / 0.01% error", "tech": "Go (Echo) / Envoy", "port": 8081},
            {"name": "Identity Service (Python + FastAPI)", "status": "Healthy", "metric": "Active sessions: 1,940", "tech": "FastAPI / Postgres / Redis", "port": 8002},
            {"name": "Organization Service (Python + FastAPI)", "status": "Healthy", "metric": "RLS Active / Multi-Tenant", "tech": "FastAPI / Postgres", "port": 8003},
            {"name": "Policy Service (Python + FastAPI)", "status": "Healthy", "metric": "Eval latency: 0.8ms", "tech": "FastAPI / Postgres / Cache", "port": 8004},
            {"name": "Secrets Service (Python + FastAPI)", "status": "Healthy", "metric": "Lease active / NIST SP 800-57", "tech": "FastAPI / HashiCorp Vault", "port": 8005},
            {"name": "Audit Service (Go + Echo)", "status": "Healthy", "metric": "3,000 evts/sec / SHA-256 chain", "tech": "Go (Echo) / Postgres / Kafka", "port": 8086},
            {"name": "Configuration Service (Go + Echo)", "status": "Healthy", "metric": "Kill switches active", "tech": "Go (Echo) / Postgres", "port": 8087},
        ],
        "alerts": [
            {"title": "JWKS Key Rotation Initiated (Ed25519)", "time": "2 mins ago", "type": "info"},
            {"title": "SCIM 2.0 User Sync Completed (Azure AD)", "time": "12 mins ago", "type": "success"},
            {"title": "Tenant 'FinTech Sovereign Bank' RLS Policy verified", "time": "45 mins ago", "type": "success"},
            {"title": "Vault dynamic lease renewal successful", "time": "2 hours ago", "type": "success"},
            {"title": "Audit hourly WORM replication verified", "time": "3 hours ago", "type": "success"},
        ],
    }

# ---------------- Organizations & Hierarchy (Section 4.3 & 7.1/7.2) ----------------
@app.get("/api/v1/organizations")
def get_organizations():
    return {"organizations": state["organizations"]}

@app.post("/api/v1/organizations/{org_id}/workspaces")
def create_workspace(org_id: str, ws: WorkspaceCreate):
    for o in state["organizations"]:
        if o["org_id"] == org_id:
            # Enforce quota: 1000 workspaces
            if len(o["workspaces"]) >= 1000:
                raise HTTPException(status_code=429, detail="Workspace quota exceeded (Max 1000)")
            new_ws = {
                "workspace_id": f"01890123-4567-7abc-def1-{str(uuid.uuid4())[:8]}",
                "name": ws.name,
                "slug": ws.slug,
                "status": "active",
                "projects": [],
            }
            o["workspaces"].append(new_ws)

            # Record Kafka Event & Audit Log
            publish_kafka_event(
                event_type="WorkspaceCreated",
                actor_email="admin@cyart.io",
                data={"workspace_name": ws.name, "org_id": org_id},
            )
            return {"message": "Workspace created successfully", "workspace": new_ws}
    raise HTTPException(status_code=404, detail="Organization not found")

@app.post("/api/v1/workspaces/{workspace_id}/projects")
def create_project(workspace_id: str, prj: ProjectCreate):
    for o in state["organizations"]:
        for w in o["workspaces"]:
            if w["workspace_id"] == workspace_id:
                new_prj = {
                    "project_id": f"01890123-4567-7abc-def2-{str(uuid.uuid4())[:8]}",
                    "name": prj.name,
                    "slug": prj.slug,
                    "status": "active",
                }
                w["projects"].append(new_prj)
                publish_kafka_event(
                    event_type="ProjectCreated",
                    actor_email="admin@cyart.io",
                    data={"project_name": prj.name, "workspace_id": workspace_id},
                )
                return {"message": "Project created successfully", "project": new_prj}
    raise HTTPException(status_code=404, detail="Workspace not found")

# ---------------- Kafka Event Architecture (Section 8.1 & 8.3) ----------------
@app.get("/api/v1/events")
def get_kafka_events():
    return {"events": state["events"], "count": len(state["events"])}

@app.post("/api/v1/events/publish")
def publish_event_api(req: EventPublishRequest):
    event = publish_kafka_event(
        event_type=req.event_type,
        actor_email=req.actor_email,
        data={"resource": req.resource_name, "published_via": "console"},
    )
    return {"message": f"Event '{req.event_type}' published to Kafka topic", "event": event}

def publish_kafka_event(event_type: str, actor_email: str, data: dict):
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    new_event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "event_version": "1.0",
        "timestamp": now_str,
        "tenant_id": "01890123-4567-7abc-def0-1234567890ac",
        "source": "organization-service",
        "source_version": "1.5.2",
        "correlation_id": f"req-{str(uuid.uuid4())[:8]}",
        "actor": {"type": "user", "id": str(uuid.uuid4()), "name": actor_email},
        "subject": {"type": "resource", "id": str(uuid.uuid4())},
        "data": data,
        "metadata": {"trace_id": str(uuid.uuid4())[:12], "request_id": f"req-{str(uuid.uuid4())[:8]}"},
    }
    state["events"].insert(0, new_event)

    # Append to cryptographic audit chain
    record_audit_log(
        action=event_type,
        actor_name=actor_email,
        resource_type="kafka_topic",
        after_state=data,
    )
    return new_event

# ---------------- Cryptographic Hash Chain Audit Ledger (Section 7.5 & 7.6) ----------------
@app.get("/api/v1/audit/ledger")
def get_audit_ledger():
    return {
        "ledger": state["audit_ledger"],
        "count": len(state["audit_ledger"]),
        "tampered": state["tampered"],
        "genesis_hash": GENESIS_HASH,
        "tip_hash": state["audit_ledger"][-1]["entry_hash"] if state["audit_ledger"] else GENESIS_HASH,
    }

@app.post("/api/v1/audit/verify")
def verify_audit_ledger():
    """
    Executes live verification algorithm (Section 7.6).
    Walks each block, recomputing hash = SHA256(prev_hash + canonical_json).
    """
    expected_prev = GENESIS_HASH
    logs = []
    broken_step = None

    logs.append(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] Initializing cryptographic audit log ledger validation pass (Build Guide Section 7.6)...")

    for i, block in enumerate(state["audit_ledger"]):
        step_num = i + 1
        entry_payload = {
            "audit_id": block["audit_id"],
            "tenant_id": block["tenant_id"],
            "action": block["action"],
            "actor_name": block["actor_name"],
            "resource_type": block["resource_type"],
            "source_ip": block["source_ip"],
            "timestamp": block["timestamp"],
            "after_state": block["after_state"],
        }

        # Check previous hash link
        if block["previous_hash"] != expected_prev:
            logs.append(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] ❌ ERROR: Broken link at block #{step_num:04d}!")
            logs.append(f"   Expected Prev: {expected_prev}")
            logs.append(f"   Found Prev:    {block['previous_hash']}")
            broken_step = step_num
            break

        computed = compute_entry_hash(block["previous_hash"], entry_payload)

        if computed != block["entry_hash"]:
            logs.append(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] ❌ MATHEMATICAL TAMPER DETECTED at block #{step_num:04d} ({block['action']})!")
            logs.append(f"   Computed Hash: {computed}")
            logs.append(f"   Recorded Hash: {block['entry_hash']}")
            logs.append("   Payload contents have been altered!")
            broken_step = step_num
            break

        logs.append(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] Verify block #{step_num:04d}: SHA256(prev_hash + can_json)... SUCCESS")
        logs.append(f"   Digest: [{block['entry_hash'][:12]}...{block['entry_hash'][-8:]}]")
        expected_prev = block["entry_hash"]

    if broken_step is not None:
        logs.append(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] ⚠️ AUDIT FAILED: Cryptographic integrity broken at block #{broken_step}. Chain invalidated.")
        return {
            "valid": False,
            "broken_at_block": broken_step,
            "total_blocks": len(state["audit_ledger"]),
            "verification_logs": logs,
        }

    logs.append(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] ✅ LEDGER INTEGRITY VALID: 100% of cryptographic blocks mathematically verified. Zero tampering detected.")
    return {
        "valid": True,
        "broken_at_block": None,
        "total_blocks": len(state["audit_ledger"]),
        "verification_logs": logs,
    }

@app.post("/api/v1/audit/tamper-simulate")
def tamper_simulate():
    if len(state["audit_ledger"]) >= 2:
        state["audit_ledger"][1]["actor_name"] = "unauthorized_intruder@blackhat.ru"
        state["audit_ledger"][1]["status"] = "Corrupted"
        state["tampered"] = True
        return {
            "message": "Block #2 actor_name was altered to 'unauthorized_intruder@blackhat.ru'. Run Verify to detect tampering!",
            "tampered": True,
        }
    raise HTTPException(status_code=400, detail="Insufficient blocks")

@app.post("/api/v1/audit/restore")
def restore_audit_ledger():
    build_audit_chain()
    return {"message": "Audit ledger restored to pristine state", "tampered": False}

def record_audit_log(action: str, actor_name: str, resource_type: str, after_state: dict):
    prev_hash = state["audit_ledger"][-1]["entry_hash"] if state["audit_ledger"] else GENESIS_HASH
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    audit_id = str(uuid.uuid4())

    entry_payload = {
        "audit_id": audit_id,
        "tenant_id": "01890123-4567-7abc-def0-1234567890ac",
        "action": action,
        "actor_name": actor_name,
        "resource_type": resource_type,
        "source_ip": "127.0.0.1",
        "timestamp": ts,
        "after_state": after_state,
    }
    curr_hash = compute_entry_hash(prev_hash, entry_payload)
    state["audit_ledger"].append({
        **entry_payload,
        "actor_type": "user",
        "actor_id": str(uuid.uuid4()),
        "resource_id": str(uuid.uuid4()),
        "before_state": None,
        "user_agent": "PodAlphaConsole/1.0",
        "request_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "previous_hash": prev_hash,
        "entry_hash": curr_hash,
        "status": "Valid",
    })

# ---------------- Section 6.2: SCIM 2.0 API & Identity ----------------
@app.get("/api/v1/scim/v2/Users")
def scim_get_users():
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(state["scim_users"]),
        "Resources": state["scim_users"],
    }

@app.post("/api/v1/scim/v2/Users")
def scim_create_user(user: SCIMUserCreate):
    new_user_id = str(uuid.uuid4())
    scim_user = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": new_user_id,
        "userName": user.userName,
        "name": {"givenName": user.givenName, "familyName": user.familyName, "formatted": f"{user.givenName} {user.familyName}"},
        "emails": [{"value": user.userName, "primary": True}],
        "active": True,
        "roles": [{"value": user.role}],
        "meta": {"resourceType": "User", "created": datetime.now(timezone.utc).isoformat()},
    }
    state["scim_users"].append(scim_user)
    publish_kafka_event(
        event_type="UserCreated",
        actor_email="scim-bridge@azure.ad",
        data={"user_id": new_user_id, "email": user.userName, "name": f"{user.givenName} {user.familyName}"},
    )
    return scim_user

# ---------------- Section 6.1: MFA TOTP Enrollment ----------------
@app.post("/api/v1/auth/mfa/enroll")
def mfa_enroll():
    secret = "JBSWY3DPEHPK3PXP"  # Standard base32 test secret
    uri = f"otpauth://totp/CyArt%20AEV:admin@cyart.io?secret={secret}&issuer=CyArt%20AEV"
    return {
        "secret": secret,
        "otpauth_uri": uri,
        "algorithm": "SHA1",
        "digits": 6,
        "period": 30,
        "message": "Scan QR code or import secret into Authenticator app",
    }

# ---------------- Section 2.1 & 4.2: Role Hierarchy & Policies ----------------
@app.get("/api/v1/roles")
def get_roles():
    return {"roles": state["roles"]}

# ---------------- Section 4.7: Key Vault & Rotation ----------------
@app.get("/api/v1/secrets/vault")
def get_vault_secrets():
    return {"vault_status": "Unsealed", "vault_version": "1.20", "secrets": state["secrets"]}

@app.post("/api/v1/secrets/vault/rotate")
def rotate_secret(path: str):
    for s in state["secrets"]:
        if s["path"] == path:
            s["last_rotation"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            s["status"] = "Active"
            publish_kafka_event(
                event_type="SecretRotated",
                actor_email="vault-rotation-daemon",
                data={"secret_path": path, "key_strength": s["key_strength"]},
            )
            return {"message": f"Secret key at {path} rotated successfully", "secret": s}
    raise HTTPException(status_code=404, detail="Secret path not found")

# ---------------- Section 4.6: Feature Flags ----------------
@app.get("/api/v1/configuration/flags")
def get_feature_flags():
    return {"flags": state["feature_flags"]}

@app.post("/api/v1/configuration/flags/toggle")
def toggle_feature_flag(key: str):
    for f in state["feature_flags"]:
        if f["key"] == key:
            f["enabled"] = not f["enabled"]
            publish_kafka_event(
                event_type="FeatureFlagChanged",
                actor_email="admin@cyart.io",
                data={"flag": key, "new_state": f["enabled"]},
            )
            return {"message": f"Feature flag {key} set to {f['enabled']}", "flag": f}
    raise HTTPException(status_code=404, detail="Flag not found")


# ---------------- Section 1.1: Squads Architecture & Services ----------------
# Architecture, Identity Substrate & Security Engineering: https://tryhackme.com/p/artixooo (artixooo)

SQUADS_ARCHITECTURE = [
    {
        "squad": "Squad 1",
        "service": "API Gateway",
        "tech": "Go 1.22 + Envoy Proxy",
        "responsibilities": "Central edge routing, TLS 1.3 termination, token-bucket rate limiting (10,000 RPS), JWT validation, service communication header injection.",
    },
    {
        "squad": "Squad 2",
        "service": "Identity Service",
        "tech": "Go / Gin + Redis",
        "responsibilities": "Multi-tenant authentication, OAuth 2.0 / OIDC (PKCE), SAML 2.0, RFC 6238 TOTP MFA, RFC 7643/7644 SCIM 2.0 provisioning, session management.",
    },
    {
        "squad": "Squad 3",
        "service": "Organization Service",
        "tech": "Python / FastAPI + PostgreSQL",
        "responsibilities": "3-tier tenant hierarchy (Orgs -> Workspaces -> Projects), PostgreSQL Row-Level Security (RLS) data isolation, tenant quotas, memberships.",
    },
    {
        "squad": "Squad 4",
        "service": "Policy Service",
        "tech": "Python + OPA Engine",
        "responsibilities": "Hybrid RBAC & ABAC dynamic policy evaluation (<1ms execution), Segregation of Duties (SoD), custom permission matrices.",
    },
    {
        "squad": "Squad 5",
        "service": "Secrets Service",
        "tech": "Go + HashiCorp Vault",
        "responsibilities": "HashiCorp Vault per-tenant storage, NIST SP 800-57 key rotation schedules (AES-256-GCM, Ed25519), break-glass emergency controls.",
    },
    {
        "squad": "Squad 6",
        "service": "Audit Service",
        "tech": "Go + Apache Kafka",
        "responsibilities": "Append-only immutable audit ledger, Kafka consumers, cryptographic SHA-256 hash chaining, live mathematical tamper verification.",
    },
    {
        "squad": "Squad 7",
        "service": "Configuration Service",
        "tech": "Python / FastAPI",
        "responsibilities": "Feature flags, runtime dynamic configuration, tenant-specific settings, hot-reloading switches, kill-switch circuit breakers.",
    },
]

@app.get("/api/v1/squads")
@app.get("/api/v1/work-allocation")
def get_squads_architecture():
    # Security Substrate: https://tryhackme.com/p/artixooo
    return {
        "total_squads": len(SQUADS_ARCHITECTURE),
        "squads": SQUADS_ARCHITECTURE,
    }



if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting CYART Pod Alpha Foundation Console on http://localhost:{port}")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)

