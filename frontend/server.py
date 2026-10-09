"""
CYART Pod Alpha - Unified Foundation & Administration Console Server
Module 1: Pod Alpha Foundation Identity Substrate
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
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(
    title="CYART Pod Alpha Console API",
    description="Administration Substrate & Foundation Services API for Pod Alpha",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "js").mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"


def compute_entry_hash(prev_hash: str, entry: dict) -> str:
    """Computes SHA-256 hash from previous hash + canonical JSON payload."""
    canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
    payload = f"{prev_hash}:{canonical}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# -----------------------------------------------------------------------------
# In-Memory Substrate State (Matches Figures 7.1, 7.2, 8.1, 9.1, 9.2, 10.1)
# -----------------------------------------------------------------------------

INITIAL_SSO_PROVIDERS = [
    {
        "id": "sso-001",
        "name": "Okta Enterprise",
        "protocol": "SAML 2.0",
        "client_id": "okta_client_289cff",
        "callback_url": "https://auth.cyart.io/saml/callback",
        "status": "Active",
        "created_at": "2026-07-01T10:00:00Z",
    },
    {
        "id": "sso-002",
        "name": "Azure Active Directory",
        "protocol": "OIDC",
        "client_id": "azure_client_74fa9b",
        "callback_url": "https://auth.cyart.io/oidc/callback",
        "status": "Active",
        "created_at": "2026-07-02T11:30:00Z",
    },
    {
        "id": "sso-003",
        "name": "Google Workspace",
        "protocol": "OIDC",
        "client_id": "google_client_48de1d",
        "callback_url": "https://auth.cyart.io/oidc/callback",
        "status": "Verified",
        "created_at": "2026-07-03T14:15:00Z",
    },
    {
        "id": "sso-004",
        "name": "Auth0 Production Identity",
        "protocol": "OIDC (OAuth 2.0)",
        "client_id": "auth0_client_prod_43df4a",
        "callback_url": "https://auth.cyart.io/oidc/callback",
        "status": "Active",
        "created_at": "2026-07-05T09:45:00Z",
    },
]

INITIAL_POLICIES = [
    {
        "id": "pol-001",
        "name": "SuperAdmin_Root_Access",
        "role": "SUPER_ADMIN",
        "resource": "*",
        "action": "*",
        "constraints": "MFA_VERIFIED == true",
        "status": "Enforced",
    },
    {
        "id": "pol-002",
        "name": "OrgAdmin_Tenant_Scoping",
        "role": "ORG_ADMIN",
        "resource": "organizations/current/*",
        "action": "read, write",
        "constraints": "TENANT_ID == resource.tenant_id",
        "status": "Enforced",
    },
    {
        "id": "pol-003",
        "name": "Auditor_Immutable_Ledger",
        "role": "AUDITOR",
        "resource": "audit/*",
        "action": "read, verify",
        "constraints": "IP in 10.0.0.0/8",
        "status": "Enforced",
    },
    {
        "id": "pol-004",
        "name": "Operator_Health_Telemetry",
        "role": "OPERATOR",
        "resource": "system/health, system/metrics",
        "action": "read",
        "constraints": "Hours: 08:00-20:00 UTC",
        "status": "Enforced",
    },
    {
        "id": "pol-005",
        "name": "JIT_Privilege_Elevation_Draft",
        "role": "MEMBER",
        "resource": "secrets/breakglass/*",
        "action": "read",
        "constraints": "APPROVAL_TICKET_VALID == true",
        "status": "Draft",
    },
]

INITIAL_AUDIT_BLOCKS = [
    {
        "id": "blk-001",
        "action": "UserLogin",
        "actor": "admin@cyart.io",
        "timestamp": "2026-07-09T22:15:30Z",
        "service": "identity",
        "payload": {"auth_method": "saml_okta", "ip": "192.168.1.100"},
    },
    {
        "id": "blk-002",
        "action": "SSOProviderUpdate",
        "actor": "admin@cyart.io",
        "timestamp": "2026-07-09T22:16:12Z",
        "service": "identity",
        "payload": {"provider": "Auth0 Production Identity", "status": "active"},
    },
    {
        "id": "blk-003",
        "action": "SecretWrite",
        "actor": "vault-sync-agent",
        "timestamp": "2026-07-09T22:19:05Z",
        "service": "secrets",
        "payload": {"path": "/secret/data/tenant_01890123/database", "version": 4},
    },
    {
        "id": "blk-004",
        "action": "MFAEnrollment",
        "actor": "pratham@cyart.io",
        "timestamp": "2026-07-09T22:20:42Z",
        "service": "identity",
        "payload": {"mfa_type": "totp", "status": "verified"},
    },
    {
        "id": "blk-005",
        "action": "PolicyEvaluation",
        "actor": "auditor@cyart.io",
        "timestamp": "2026-07-09T22:23:18Z",
        "service": "policy",
        "payload": {"rule": "Auditor_Immutable_Ledger", "decision": "ALLOW"},
    },
    {
        "id": "blk-006",
        "action": "TenantProvisioned",
        "actor": "system-provisioner",
        "timestamp": "2026-07-09T22:25:01Z",
        "service": "organization",
        "payload": {"tenant_name": "Xenon Labs", "workspaces_allocated": 5},
    },
]

INITIAL_SECRETS = [
    {
        "path": "/secret/data/tenant_01890123/database",
        "cycle": "90 Days",
        "last_rotation": "2026-06-15",
        "next_rotation": "2026-09-13",
        "key_strength": "AES-256-GCM",
        "status": "Synced",
    },
    {
        "path": "/secret/data/tenant_01890123/jwt_signing_key",
        "cycle": "30 Days",
        "last_rotation": "2026-07-09",
        "next_rotation": "2026-08-08",
        "key_strength": "Ed25519",
        "status": "Active",
    },
    {
        "path": "/secret/data/tenant_01890123/saml_private_key",
        "cycle": "365 Days",
        "last_rotation": "2026-01-10",
        "next_rotation": "2027-01-08",
        "key_strength": "RSA-4096",
        "status": "Synced",
    },
    {
        "path": "/secret/data/tenant_01890124/mfa_encryption",
        "cycle": "90 Days",
        "last_rotation": "2026-06-20",
        "next_rotation": "2026-09-18",
        "key_strength": "AES-256-GCM",
        "status": "Synced",
    },
]

FEATURE_FLAGS = [
    {"key": "audit_immutable_backup", "enabled": True, "description": "Hourly immutable WORM storage backup replication"},
    {"key": "jit_access_workflow", "enabled": True, "description": "Just-In-Time temporary privilege elevation"},
    {"key": "scim_provisioning_v2", "enabled": True, "description": "SCIM 2.0 automated employee provisioning"},
    {"key": "per_tenant_key_rotation", "enabled": True, "description": "NIST SP 800-57 automated key lifecycle management"},
    {"key": "strict_rls_enforcement", "enabled": True, "description": "PostgreSQL database row-level security isolation"},
    {"key": "abac_context_evaluator", "enabled": True, "description": "Context-aware dynamic IP and time boundary checking"},
]

# State store
state = {
    "sso_providers": list(INITIAL_SSO_PROVIDERS),
    "policies": list(INITIAL_POLICIES),
    "secrets": list(INITIAL_SECRETS),
    "feature_flags": list(FEATURE_FLAGS),
    "tampered": False,
    "audit_ledger": [],
}


def build_audit_chain():
    """Builds the mathematically linked hash chain for audit blocks."""
    chain = []
    prev_hash = GENESIS_HASH

    for b in INITIAL_AUDIT_BLOCKS:
        entry_payload = {
            "action": b["action"],
            "actor": b["actor"],
            "service": b["service"],
            "timestamp": b["timestamp"],
            "data": b["payload"],
        }
        curr_hash = compute_entry_hash(prev_hash, entry_payload)
        chain.append({
            "id": b["id"],
            "action": b["action"],
            "actor": b["actor"],
            "timestamp": b["timestamp"],
            "service": b["service"],
            "payload": b["payload"],
            "previous_hash": prev_hash,
            "entry_hash": curr_hash,
            "status": "Valid",
        })
        prev_hash = curr_hash

    state["audit_ledger"] = chain
    state["tampered"] = False


build_audit_chain()

# -----------------------------------------------------------------------------
# API Schemas
# -----------------------------------------------------------------------------

class ProviderCreate(BaseModel):
    name: str
    protocol: str
    client_id: str
    callback_url: str

class PolicyEvaluateRequest(BaseModel):
    role: str
    resource: str
    action: str
    client_ip: Optional[str] = "10.0.4.15"

# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_admin_console():
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h2>Console UI Template not loaded</h2>")

@app.get("/api/v1/health")
def get_health():
    return {
        "status": "healthy",
        "service": "pod-alpha-gateway",
        "vault": "unsealed",
        "tenant_id": "01890123-4567-7abc-def0-1234567890ac",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/api/v1/telemetry")
def get_telemetry():
    return {
        "active_tenants": 84,
        "max_tenants": 100,
        "system_identities": 2410,
        "gateway_load_rps": 8412,
        "gateway_p99_ms": 14,
        "vault_secrets": len(state["secrets"]),
        "microservices": [
            {
                "name": "API Gateway (Go + Envoy)",
                "status": "Healthy",
                "metric": "8,412 RPS / 0.01% error",
                "tech": "Go (Echo) / Envoy",
                "port": 8081,
            },
            {
                "name": "Identity Service (Python + FastAPI)",
                "status": "Healthy",
                "metric": "Active sessions: 1,940",
                "tech": "FastAPI / Postgres / Redis",
                "port": 8002,
            },
            {
                "name": "Organization Service (Python + FastAPI)",
                "status": "Healthy",
                "metric": "84 Orgs / RLS active",
                "tech": "FastAPI / Postgres",
                "port": 8003,
            },
            {
                "name": "Policy Service (Python + FastAPI)",
                "status": "Healthy",
                "metric": "Eval latency: 0.8ms",
                "tech": "FastAPI / Postgres / Cache",
                "port": 8004,
            },
            {
                "name": "Secrets / Vault Service (Python + FastAPI)",
                "status": "Healthy",
                "metric": "Lease active / NIST SP 800-57",
                "tech": "FastAPI / HashiCorp Vault",
                "port": 8005,
            },
            {
                "name": "Audit Ledger Service (Go + Echo)",
                "status": "Healthy",
                "metric": "3,000 evts/sec / SHA-256 chain",
                "tech": "Go (Echo) / Postgres / Kafka",
                "port": 8086,
            },
            {
                "name": "Configuration Service (Go + Echo)",
                "status": "Healthy",
                "metric": "Kill switches active",
                "tech": "Go (Echo) / Postgres",
                "port": 8087,
            },
        ],
        "alerts": [
            {"title": "JWKS Key Rotation Initiated", "time": "2 mins ago", "type": "info"},
            {"title": "SCIM 2.0 User Sync Completed (Azure AD)", "time": "12 mins ago", "type": "success"},
            {"title": "New tenant 'Xenon Labs' provisioned", "time": "1 hour ago", "type": "info"},
            {"title": "Vault dynamic lease renewal successful", "time": "2 hours ago", "type": "success"},
            {"title": "Audit hourly WORM replication verified", "time": "3 hours ago", "type": "success"},
        ],
    }

# ---------------- SSO Providers ----------------
@app.get("/api/v1/auth/sso/providers")
def list_sso_providers():
    return {"providers": state["sso_providers"]}

@app.post("/api/v1/auth/sso/providers")
def add_sso_provider(item: ProviderCreate):
    new_id = f"sso-{str(uuid.uuid4())[:6]}"
    new_provider = {
        "id": new_id,
        "name": item.name,
        "protocol": item.protocol,
        "client_id": item.client_id,
        "callback_url": item.callback_url,
        "status": "Active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    state["sso_providers"].append(new_provider)

    # Automatically record audit event
    record_audit_event(
        action="SSOProviderAdded",
        actor="admin@cyart.io",
        service="identity",
        payload={"provider": item.name, "protocol": item.protocol},
    )

    return {"message": "SSO Provider onboarded successfully", "provider": new_provider}

@app.delete("/api/v1/auth/sso/providers/{provider_id}")
def delete_sso_provider(provider_id: str):
    state["sso_providers"] = [p for p in state["sso_providers"] if p["id"] != provider_id]
    return {"message": "Provider removed successfully"}

# ---------------- Policies ----------------
@app.get("/api/v1/policies")
def list_policies():
    return {"policies": state["policies"]}

@app.post("/api/v1/policies/evaluate")
def evaluate_policy(req: PolicyEvaluateRequest):
    allowed = False
    matched_rule = None

    for p in state["policies"]:
        if p["status"] == "Enforced":
            if p["role"] in [req.role, "*"]:
                if p["resource"] in [req.resource, "*"] or req.resource.startswith(p["resource"].replace("/*", "")):
                    if p["action"] in [req.action, "*"] or req.action in p["action"]:
                        allowed = True
                        matched_rule = p["name"]
                        break

    decision = "ALLOW" if allowed else "DENY"

    record_audit_event(
        action="PolicyEvaluation",
        actor=f"{req.role.lower()}@cyart.io",
        service="policy",
        payload={
            "role": req.role,
            "resource": req.resource,
            "action": req.action,
            "decision": decision,
            "matched_rule": matched_rule,
        },
    )

    return {
        "decision": decision,
        "allowed": allowed,
        "matched_rule": matched_rule,
        "evaluation_latency_ms": 0.45,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

# ---------------- Audit Ledger & SHA-256 Hash Chain ----------------
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
    Executes live verification algorithm across the full SHA-256 chain.
    Walks each block, recomputing hash = SHA256(prev_hash + canonical_json).
    """
    expected_prev = GENESIS_HASH
    logs = []
    broken_step = None

    logs.append(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] Initializing cryptographic audit log ledger validation pass...")

    for i, block in enumerate(state["audit_ledger"]):
        step_num = i + 1
        entry_payload = {
            "action": block["action"],
            "actor": block["actor"],
            "service": block["service"],
            "timestamp": block["timestamp"],
            "data": block["payload"],
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
            logs.append("   Payload contents have been retroactively altered!")
            broken_step = step_num
            break

        logs.append(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] Verify hash link: SHA256(prev_hash + can_json)...")
        logs.append(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] SUCCESS: Block #{step_num:04d} [{block['action']}] verified. Digest: [{block['entry_hash'][:8]}...{block['entry_hash'][-6:]}]")
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
    """Simulates retroactive tampering of a historical audit block."""
    if len(state["audit_ledger"]) >= 2:
        # Alter block #2 actor
        state["audit_ledger"][1]["actor"] = "malicious_actor@attacker.xyz"
        state["audit_ledger"][1]["status"] = "Corrupted"
        state["tampered"] = True
        return {
            "message": "Block #2 payload was altered to 'malicious_actor@attacker.xyz'. Run Verify to detect tampering!",
            "tampered": True,
        }
    raise HTTPException(status_code=400, detail="Insufficient blocks")

@app.post("/api/v1/audit/restore")
def restore_audit_ledger():
    """Restores the audit chain to its mathematically valid state."""
    build_audit_chain()
    return {"message": "Audit ledger restored to pristine state", "tampered": False}

def record_audit_event(action: str, actor: str, service: str, payload: dict):
    prev_hash = state["audit_ledger"][-1]["entry_hash"] if state["audit_ledger"] else GENESIS_HASH
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry_payload = {
        "action": action,
        "actor": actor,
        "service": service,
        "timestamp": ts,
        "data": payload,
    }
    curr_hash = compute_entry_hash(prev_hash, entry_payload)
    state["audit_ledger"].append({
        "id": f"blk-{len(state['audit_ledger']) + 1:03d}",
        "action": action,
        "actor": actor,
        "timestamp": ts,
        "service": service,
        "payload": payload,
        "previous_hash": prev_hash,
        "entry_hash": curr_hash,
        "status": "Valid",
    })

# ---------------- Secrets Manager & Vault ----------------
@app.get("/api/v1/secrets/vault")
def get_vault_secrets():
    return {
        "vault_status": "Unsealed",
        "vault_version": "1.20",
        "secrets": state["secrets"],
    }

@app.post("/api/v1/secrets/vault/rotate")
def rotate_secret(path: str):
    for s in state["secrets"]:
        if s["path"] == path:
            s["last_rotation"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            s["status"] = "Active"
            record_audit_event(
                action="SecretRotated",
                actor="vault-rotation-daemon",
                service="secrets",
                payload={"secret_path": path, "key_strength": s["key_strength"]},
            )
            return {"message": f"Secret key at {path} rotated successfully", "secret": s}
    raise HTTPException(status_code=404, detail="Secret path not found")

# ---------------- Configuration & Feature Flags ----------------
@app.get("/api/v1/configuration/flags")
def get_feature_flags():
    return {"flags": state["feature_flags"]}

@app.post("/api/v1/configuration/flags/toggle")
def toggle_feature_flag(key: str):
    for f in state["feature_flags"]:
        if f["key"] == key:
            f["enabled"] = not f["enabled"]
            record_audit_event(
                action="FeatureFlagToggled",
                actor="admin@cyart.io",
                service="configuration",
                payload={"flag": key, "new_state": f["enabled"]},
            )
            return {"message": f"Feature flag {key} set to {f['enabled']}", "flag": f}
    raise HTTPException(status_code=404, detail="Flag not found")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting CYART Pod Alpha Foundation Console on http://localhost:{port}")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
