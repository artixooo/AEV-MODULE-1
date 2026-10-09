# M1 ↔ M2 Configuration Integration Contract

**Between:** Pod Alpha — Configuration Service (M1, Squad 7)
**And:** Pod Beta — Risk Scoring Engine (M2)

## 1. Purpose

Pod Beta's Risk Scoring Engine needs per-organization, customizable risk
weights (Criticality, Threat Intel, Severity, and other factors) to compute
business-aware risk scores, rather than relying on a fixed, one-size-fits-all
formula. This contract defines exactly what Configuration Service provides,
how Beta consumes it, and what happens if Configuration Service is
unavailable.

This is derived from:
- Pod Beta's Project Proposal (Risk Scoring Engine section)
- Pod Alpha's Service Dependency table (Configuration Service row): *"Per-org
  configuration, specifically the custom risk weights (Criticality, Threat
  Intel, Severity, etc.) used by Beta's Risk Scoring Engine."*

---

## 2. Configuration Contract

| Configuration | Scope | Consumer | Sensitive? | Has Default? |
|---|---|---|---|---|
| Risk weight: Criticality | Per organization | Risk Service | No | Yes (25%) |
| Risk weight: Threat Intel | Per organization | Risk Service | No | Yes (20%) |
| Risk weight: Severity | Per organization | Risk Service | No | Yes |
| Other factors | Per organization | Risk Service | No | TBD |

None of these values are sensitive — no `*_ref` / Secrets Service boundary
applies here (unlike the Identity Provider configuration work). These are
plain numeric weights.

---

## 3. Storage Approach

Following the same pattern already used for Identity Provider configuration
(see `docs/config_identity-provider.md`): **no new database table**. Risk
weights are stored as regular rows in the existing `configuration` table,
scoped by `organization_id`, using a namespaced key convention:
config_key = "risk_weight:criticality:{organization_id}"
config_key = "risk_weight:threat_intel:{organization_id}"
config_key = "risk_weight:severity:{organization_id}"

(Same reasoning as before: `config_key` is globally unique, so the
organization is encoded into the key itself. `organization_id` is also set
as a real column for filtering/auditing.)

---

## 4. API Surface

| Method | Endpoint | Description |
|---|---|---|
| GET | `/organizations/{organizationId}/risk-weights` | Returns all configured risk weights for the organization |
| PUT | `/organizations/{organizationId}/risk-weights` | Create or update one or more risk weights for the organization |

Response shape (example):
```json
{
  "organization_id": "org-123",
  "weights": {
    "criticality": 0.25,
    "threat_intel": 0.20,
    "severity": 0.35
  }
}
```

---

## 5. Availability & Fallback Contract

This is the most important part of this contract — **Beta must never block
risk scoring on Configuration Service being up.**

- Configuration Service should respond within **200ms** under normal
  conditions.
- If Configuration Service is **unreachable, times out, or returns an
  error**, Beta falls back to hardcoded default weights:
  - Criticality: 25%
  - Threat Intel: 20%
  - Severity: remaining weight (or a documented default — TBD with Beta squad)
- Beta should **cache** the last successfully-fetched weights per
  organization (recommended TTL: 5 minutes, consistent with other services'
  caching patterns in this project) so a transient Configuration Service
  outage doesn't force an immediate fallback to defaults if a recent value is
  already cached.
- This mirrors the fallback pattern already documented in Pod Alpha's
  Service Dependency table for the Configuration Service row.

---

## 6. Open Items (TBD)

- Exact list and default values for "Other factors" beyond Criticality,
  Threat Intel, and Severity — pending from Pod Beta squad.
- Confirm whether weights should sum to 100% (validation rule) or are
  independent multipliers — needs Risk Scoring Engine team input.
- Confirm exact cache TTL Beta will use on their end (this contract
  recommends 5 minutes to match Policy Service's existing pattern, but Beta
  squad should confirm).

---

## 7. Sign-off

| Squad | Representative | Status |
|---|---|---|
| Pod Alpha — Configuration Service | Pod Alpha Security Engineering | Drafted |
| Pod Beta — Risk Scoring Engine | K. Bharath Veer | Pending review |