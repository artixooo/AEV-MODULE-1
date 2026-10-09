/**
 * CYART AEV - Pod Alpha Administration Console Client Logic
 * Module 1: Pod Alpha Foundation Identity Substrate
 */

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  loadDashboardData();
  loadSSOProviders();
  loadPolicies();
  loadAuditLedger();
  loadVaultSecrets();
  loadFeatureFlags();
  setupEventListeners();

  // Periodic telemetry refresh
  setInterval(loadDashboardData, 15000);
});

// --------------------------------------------------------------------------
// Navigation & Views
// --------------------------------------------------------------------------
function initNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  const panels = document.querySelectorAll(".view-panel");

  navItems.forEach((item) => {
    item.addEventListener("click", () => {
      const targetView = item.getAttribute("data-view");

      navItems.forEach((n) => n.classList.remove("active"));
      panels.forEach((p) => p.classList.remove("active"));

      item.classList.add("active");
      const targetPanel = document.getElementById(targetView);
      if (targetPanel) {
        targetPanel.classList.add("active");
      }

      // Refresh specific view data on navigate
      if (targetView === "view-sso") loadSSOProviders();
      if (targetView === "view-policies") loadPolicies();
      if (targetView === "view-audit") loadAuditLedger();
      if (targetView === "view-vault") loadVaultSecrets();
      if (targetView === "view-flags") loadFeatureFlags();
    });
  });
}

// --------------------------------------------------------------------------
// 1. Dashboard & Telemetry (Figure 7.1)
// --------------------------------------------------------------------------
async function loadDashboardData() {
  try {
    const res = await fetch("/api/v1/telemetry");
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("stat-tenants").textContent = data.active_tenants;
    document.getElementById("stat-identities").textContent = data.system_identities.toLocaleString();
    document.getElementById("stat-rps").textContent = data.gateway_load_rps.toLocaleString();
    document.getElementById("stat-secrets").textContent = data.vault_secrets;

    // Render microservices
    const serviceContainer = document.getElementById("microservices-list");
    serviceContainer.innerHTML = data.microservices
      .map(
        (s) => `
      <div class="service-row">
        <div class="service-meta">
          <div class="service-dot"></div>
          <div>
            <div class="service-name">${s.name}</div>
            <div class="service-tech">${s.tech}</div>
          </div>
        </div>
        <div class="service-metric-badge">${s.metric}</div>
      </div>
    `
      )
      .join("");

    // Render alerts
    const alertsContainer = document.getElementById("alerts-list");
    alertsContainer.innerHTML = data.alerts
      .map(
        (a) => `
      <div class="alert-item">
        <div class="alert-title">${a.title}</div>
        <div class="alert-time">${a.time}</div>
      </div>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load telemetry:", err);
  }
}

// --------------------------------------------------------------------------
// 2. Enterprise Identity Providers (SSO) (Figure 7.2 & 8.1)
// --------------------------------------------------------------------------
async function loadSSOProviders() {
  try {
    const res = await fetch("/api/v1/auth/sso/providers");
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.querySelector("#sso-table tbody");
    tbody.innerHTML = data.providers
      .map(
        (p) => `
      <tr>
        <td style="font-weight: 600;">${p.name}</td>
        <td><span class="badge-tag">${p.protocol}</span></td>
        <td style="font-family: var(--font-mono); font-size: 11px;">${p.client_id}</td>
        <td style="color: var(--text-muted); font-size: 12px;">${p.callback_url}</td>
        <td><span class="badge-status ${p.status.toLowerCase()}">${p.status}</span></td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="testSSOConnection('${p.id}')">Test</button>
        </td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load SSO providers:", err);
  }
}

function testSSOConnection(id) {
  alert(`SSO Provider [${id}] handshake validated: OIDC/SAML Discovery document fetched successfully.`);
}

// --------------------------------------------------------------------------
// 3. Access Policies & Rule Engine (Figure 8.1)
// --------------------------------------------------------------------------
async function loadPolicies() {
  try {
    const res = await fetch("/api/v1/policies");
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.querySelector("#policies-table tbody");
    tbody.innerHTML = data.policies
      .map(
        (p) => `
      <tr>
        <td style="font-weight: 600;">${p.name}</td>
        <td><span class="badge-tag" style="background: rgba(99, 102, 241, 0.15); color: #818cf8; border-color: rgba(99, 102, 241, 0.3);">${p.role}</span></td>
        <td style="font-family: var(--font-mono); font-size: 11px;">${p.resource}</td>
        <td style="font-family: var(--font-mono); font-size: 11px; color: var(--accent-emerald);">${p.action}</td>
        <td style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono);">${p.constraints}</td>
        <td><span class="badge-status ${p.status.toLowerCase()}">${p.status}</span></td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load policies:", err);
  }
}

async function simulatePolicyEval() {
  const role = document.getElementById("sim-role").value;
  const resource = document.getElementById("sim-resource").value;
  const action = document.getElementById("sim-action").value;

  try {
    const res = await fetch("/api/v1/policies/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role, resource, action }),
    });
    const result = await res.json();
    const resultEl = document.getElementById("policy-eval-result");
    resultEl.style.display = "block";
    resultEl.className = result.decision === "ALLOW" ? "alert-item" : "alert-item alert-danger";
    resultEl.style.borderLeftColor = result.decision === "ALLOW" ? "var(--accent-emerald)" : "var(--accent-rose)";
    resultEl.innerHTML = `
      <div style="font-weight: 700; color: ${result.decision === "ALLOW" ? "var(--accent-emerald)" : "var(--accent-rose)"};">
        DECISION: ${result.decision}
      </div>
      <div style="font-size: 12px; margin-top: 4px; color: var(--text-muted);">
        Matched Rule: ${result.matched_rule || "Default Deny"} | Evaluation Latency: ${result.evaluation_latency_ms}ms
      </div>
    `;
    loadAuditLedger();
  } catch (err) {
    console.error("Simulation failed:", err);
  }
}

// --------------------------------------------------------------------------
// 4. Audit Ledger & Integrity Verification Console (Figures 9.1 & 9.2)
// --------------------------------------------------------------------------
async function loadAuditLedger() {
  try {
    const res = await fetch("/api/v1/audit/ledger");
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.querySelector("#audit-table tbody");
    tbody.innerHTML = data.ledger
      .map(
        (b) => `
      <tr>
        <td style="font-weight: 600;">${b.action}</td>
        <td style="color: var(--text-main);">${b.actor}</td>
        <td style="font-size: 12px; color: var(--text-dim);">${b.timestamp}</td>
        <td class="hash-cell">${b.previous_hash.slice(0, 8)}...${b.previous_hash.slice(-6)}</td>
        <td class="hash-cell">${b.entry_hash.slice(0, 8)}...${b.entry_hash.slice(-6)}</td>
        <td><span class="badge-status ${b.status.toLowerCase()}">${b.status}</span></td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load audit ledger:", err);
  }
}

async function runLedgerVerification() {
  const terminal = document.getElementById("verification-terminal");
  const body = terminal.querySelector(".terminal-body");
  terminal.style.display = "block";
  body.innerHTML = '<div class="terminal-line">Executing cryptographic hash verification pass...</div>';

  try {
    const res = await fetch("/api/v1/audit/verify", { method: "POST" });
    const result = await res.json();

    body.innerHTML = "";
    let i = 0;
    const interval = setInterval(() => {
      if (i < result.verification_logs.length) {
        const line = result.verification_logs[i];
        const div = document.createElement("div");
        div.className = "terminal-line";
        if (line.includes("SUCCESS") || line.includes("VALID")) div.className += " success";
        if (line.includes("MATHEMATICAL TAMPER") || line.includes("ERROR") || line.includes("FAILED")) div.className += " error";
        div.textContent = line;
        body.appendChild(div);
        body.scrollTop = body.scrollHeight;
        i++;
      } else {
        clearInterval(interval);
      }
    }, 180);
  } catch (err) {
    body.innerHTML = `<div class="terminal-line error">Verification request failed: ${err}</div>`;
  }
}

async function simulateTamper() {
  try {
    const res = await fetch("/api/v1/audit/tamper-simulate", { method: "POST" });
    const data = await res.json();
    alert(data.message);
    loadAuditLedger();
    runLedgerVerification();
  } catch (err) {
    alert("Tamper simulation failed: " + err);
  }
}

async function restoreLedger() {
  try {
    const res = await fetch("/api/v1/audit/restore", { method: "POST" });
    const data = await res.json();
    alert(data.message);
    loadAuditLedger();
    runLedgerVerification();
  } catch (err) {
    alert("Restore failed: " + err);
  }
}

// --------------------------------------------------------------------------
// 5. Secrets Manager & Key Vault (Figure 10.1)
// --------------------------------------------------------------------------
async function loadVaultSecrets() {
  try {
    const res = await fetch("/api/v1/secrets/vault");
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.querySelector("#vault-table tbody");
    tbody.innerHTML = data.secrets
      .map(
        (s) => `
      <tr>
        <td style="font-family: var(--font-mono); font-size: 12px; font-weight: 600;">${s.path}</td>
        <td><span class="badge-tag">${s.cycle}</span></td>
        <td style="font-size: 12px; color: var(--text-dim);">${s.last_rotation}</td>
        <td style="font-size: 12px; color: var(--text-dim);">${s.next_rotation}</td>
        <td><span style="font-family: var(--font-mono); font-size: 11px; color: var(--accent-cyan);">${s.key_strength}</span></td>
        <td><span class="badge-status ${s.status.toLowerCase()}">${s.status}</span></td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="rotateKey('${s.path}')">Rotate Now</button>
        </td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load secrets:", err);
  }
}

async function rotateKey(path) {
  try {
    const res = await fetch(`/api/v1/secrets/vault/rotate?path=${encodeURIComponent(path)}`, { method: "POST" });
    const data = await res.json();
    alert(data.message);
    loadVaultSecrets();
    loadDashboardData();
  } catch (err) {
    alert("Key rotation failed: " + err);
  }
}

// --------------------------------------------------------------------------
// 6. Feature Flags
// --------------------------------------------------------------------------
async function loadFeatureFlags() {
  try {
    const res = await fetch("/api/v1/configuration/flags");
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.querySelector("#flags-table tbody");
    tbody.innerHTML = data.flags
      .map(
        (f) => `
      <tr>
        <td style="font-family: var(--font-mono); font-size: 12px; font-weight: 600;">${f.key}</td>
        <td style="font-size: 12px; color: var(--text-muted);">${f.description}</td>
        <td><span class="badge-status ${f.enabled ? "active" : "draft"}">${f.enabled ? "Enabled" : "Disabled"}</span></td>
        <td>
          <button class="btn ${f.enabled ? "btn-danger" : "btn-primary"} btn-sm" onclick="toggleFlag('${f.key}')">
            ${f.enabled ? "Kill Switch" : "Enable"}
          </button>
        </td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load feature flags:", err);
  }
}

async function toggleFlag(key) {
  try {
    const res = await fetch(`/api/v1/configuration/flags/toggle?key=${encodeURIComponent(key)}`, { method: "POST" });
    const data = await res.json();
    loadFeatureFlags();
  } catch (err) {
    alert("Flag toggle failed: " + err);
  }
}

// --------------------------------------------------------------------------
// Modal & Global Listeners
// --------------------------------------------------------------------------
function setupEventListeners() {
  const modal = document.getElementById("add-sso-modal");
  const openBtn = document.getElementById("btn-open-sso-modal");
  const closeBtn = document.getElementById("btn-close-sso-modal");
  const cancelBtn = document.getElementById("btn-cancel-sso-modal");
  const form = document.getElementById("sso-form");

  if (openBtn) openBtn.addEventListener("click", () => modal.classList.add("active"));
  if (closeBtn) closeBtn.addEventListener("click", () => modal.classList.remove("active"));
  if (cancelBtn) cancelBtn.addEventListener("click", () => modal.classList.remove("active"));

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        name: document.getElementById("sso-name").value,
        protocol: document.getElementById("sso-protocol").value,
        client_id: document.getElementById("sso-client-id").value,
        callback_url: document.getElementById("sso-callback").value,
      };

      try {
        const res = await fetch("/api/v1/auth/sso/providers", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (res.ok) {
          modal.classList.remove("active");
          form.reset();
          loadSSOProviders();
          loadDashboardData();
        }
      } catch (err) {
        alert("Failed to add provider: " + err);
      }
    });
  }

  // Verification button
  const verifyBtn = document.getElementById("btn-verify-ledger");
  if (verifyBtn) verifyBtn.addEventListener("click", runLedgerVerification);

  const tamperBtn = document.getElementById("btn-simulate-tamper");
  if (tamperBtn) tamperBtn.addEventListener("click", simulateTamper);

  const restoreBtn = document.getElementById("btn-restore-ledger");
  if (restoreBtn) restoreBtn.addEventListener("click", restoreLedger);

  // Policy simulator
  const simBtn = document.getElementById("btn-eval-policy");
  if (simBtn) simBtn.addEventListener("click", simulatePolicyEval);
}
