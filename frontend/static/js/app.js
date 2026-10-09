/**
 * CYART AEV - Pod Alpha Administration Console Client Logic
 * Master Engineering Spec v1.0 Alignment
 */

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  loadDashboardData();
  loadSquadsArchitecture();
  loadOrganizationsHierarchy();
  loadKafkaEvents();
  loadSCIMUsers();
  loadRoleHierarchy();
  loadAuditLedger();
  loadVaultSecrets();
  loadFeatureFlags();
  setupEventListeners();

  setInterval(loadDashboardData, 15000);
});

// --------------------------------------------------------------------------
// Navigation
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

      if (targetView === "view-squads") loadSquadsArchitecture();
      if (targetView === "view-orgs") loadOrganizationsHierarchy();
      if (targetView === "view-events") loadKafkaEvents();
      if (targetView === "view-scim") loadSCIMUsers();
      if (targetView === "view-roles") loadRoleHierarchy();
      if (targetView === "view-audit") loadAuditLedger();
      if (targetView === "view-vault") loadVaultSecrets();
      if (targetView === "view-flags") loadFeatureFlags();
    });
  });
}

// --------------------------------------------------------------------------
// 1. Dashboard Overview
// --------------------------------------------------------------------------
async function loadDashboardData() {
  try {
    const res = await fetch("/api/v1/telemetry");
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("stat-tenants").textContent = data.active_tenants;
    document.getElementById("stat-workspaces").textContent = data.total_workspaces;
    document.getElementById("stat-rps").textContent = data.gateway_load_rps.toLocaleString();
    document.getElementById("stat-projects").textContent = data.total_projects;

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
// Squads Architecture (No personal names)
// --------------------------------------------------------------------------
async function loadSquadsArchitecture() {
  try {
    const res = await fetch("/api/v1/squads");
    if (!res.ok) return;
    const data = await res.json();
    const tbody = document.getElementById("squads-table-body");
    if (!tbody) return;

    tbody.innerHTML = data.squads
      .map(
        (s) => `
      <tr>
        <td><strong><span class="badge-tag">${s.squad}</span></strong></td>
        <td style="font-weight: 600; color: var(--primary);">${s.service}</td>
        <td><code style="background: var(--bg-card-subtle); padding: 3px 6px; border-radius: 4px; font-size: 12px; border: 1px solid var(--border-color);">${s.tech}</code></td>
        <td style="color: var(--text-main); font-size: 13px; line-height: 1.5;">${s.responsibilities}</td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load squads architecture:", err);
  }
}

// --------------------------------------------------------------------------
// 2. Multi-Tenant Hierarchy (Orgs -> Workspaces -> Projects)
// --------------------------------------------------------------------------
async function loadOrganizationsHierarchy() {
  try {
    const res = await fetch("/api/v1/organizations");
    if (!res.ok) return;
    const data = await res.json();

    const container = document.getElementById("orgs-hierarchy-container");
    const orgSelect = document.getElementById("ws-org-select");

    if (orgSelect) {
      orgSelect.innerHTML = data.organizations
        .map((o) => `<option value="${o.org_id}">${o.name} (${o.region})</option>`)
        .join("");
    }

    container.innerHTML = data.organizations
      .map(
        (org) => `
      <div class="card-panel" style="margin-bottom: 20px;">
        <div class="panel-title">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 15px; font-weight: 600; color: var(--text-main);">${org.name}</span>
            <span class="badge-tag">Region: ${org.region}</span>
            <span class="badge-tag" style="background: var(--success-light); color: var(--success); border: 1px solid var(--success-border); font-weight: 600;">${org.plan.toUpperCase()}</span>
          </div>
          <span style="font-family: var(--font-mono); font-size: 11px; color: var(--text-light);">${org.org_id}</span>
        </div>

        <div style="margin-top: 14px; display: flex; flex-direction: column; gap: 12px;">
          ${org.workspaces
            .map(
              (ws) => `
            <div style="background: #ffffff; border: 1px solid var(--border-light); border-radius: var(--radius-sm); padding: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-weight: 600; color: var(--text-main); font-size: 13.5px;">
                  &bull; Workspace: ${ws.name}
                  <span style="font-size: 11px; color: var(--text-light); font-family: var(--font-mono);">(${ws.slug})</span>
                </div>
                <button class="btn btn-secondary btn-sm" onclick="promptAddProject('${ws.workspace_id}')">+ Add Project</button>
              </div>

              <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
                ${
                  ws.projects.length > 0
                    ? ws.projects
                        .map(
                          (p) => `
                    <span style="font-family: var(--font-mono); font-size: 11px; background: var(--bg-muted); border: 1px solid var(--border-light); padding: 4px 10px; border-radius: 4px; color: var(--text-main);">
                      Project: ${p.name}
                    </span>
                  `
                        )
                        .join("")
                    : '<span style="font-size: 12px; color: var(--text-light);">No projects yet in this workspace.</span>'
                }
              </div>
            </div>
          `
            )
            .join("")}
        </div>
      </div>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load organizations hierarchy:", err);
  }
}

async function promptAddProject(workspaceId) {
  const name = prompt("Enter project name:");
  if (!name) return;
  const slug = name.toLowerCase().replace(/[^a-z0-9]/g, "-");

  try {
    const res = await fetch(`/api/v1/workspaces/${workspaceId}/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, slug }),
    });
    if (res.ok) {
      loadOrganizationsHierarchy();
      loadDashboardData();
      loadKafkaEvents();
      loadAuditLedger();
    }
  } catch (err) {
    alert("Project creation failed: " + err);
  }
}

// --------------------------------------------------------------------------
// 3. Kafka Event Architecture Stream (Section 8.3)
// --------------------------------------------------------------------------
async function loadKafkaEvents() {
  try {
    const res = await fetch("/api/v1/events");
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.querySelector("#events-table tbody");
    tbody.innerHTML = data.events
      .map(
        (e) => `
      <tr>
        <td><span class="badge-tag" style="background: var(--success-light); color: var(--success); border: 1px solid var(--success-border); font-weight: 600;">${e.event_type}</span></td>
        <td style="font-family: var(--font-mono); font-size: 11px; color: var(--text-muted);">${e.correlation_id}</td>
        <td style="font-size: 12px; font-weight: 500; color: var(--text-main);">${e.actor ? e.actor.name : "system"}</td>
        <td style="font-size: 12px; color: var(--primary); font-family: var(--font-mono); font-weight: 500;">${e.source}</td>
        <td style="font-size: 12px; color: var(--text-light);">${e.timestamp}</td>
        <td style="font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
          ${JSON.stringify(e.data)}
        </td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load events:", err);
  }
}

// --------------------------------------------------------------------------
// 4. SCIM 2.0 & Identity Management (Section 6.2)
// --------------------------------------------------------------------------
async function loadSCIMUsers() {
  try {
    const res = await fetch("/api/v1/scim/v2/Users");
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.querySelector("#scim-table tbody");
    tbody.innerHTML = data.Resources.map(
      (u) => `
      <tr>
        <td style="font-family: var(--font-mono); font-size: 12px; font-weight: 600; color: var(--primary);">${u.userName}</td>
        <td style="font-weight: 500; color: var(--text-main);">${u.name ? u.name.formatted : u.userName}</td>
        <td style="font-size: 12px; color: var(--text-muted);">${u.emails && u.emails[0] ? u.emails[0].value : ""}</td>
        <td><span class="badge-tag">${u.roles && u.roles[0] ? u.roles[0].value : "Member"}</span></td>
        <td><span class="badge-status ${u.active ? "active" : "corrupted"}">${u.active ? "Active" : "Deactivated"}</span></td>
        <td style="font-size: 12px; color: var(--text-light);">${u.meta ? u.meta.created.split("T")[0] : ""}</td>
      </tr>
    `
    ).join("");
  } catch (err) {
    console.error("Failed to load SCIM users:", err);
  }
}

async function triggerMfaEnroll() {
  try {
    const res = await fetch("/api/v1/auth/mfa/enroll", { method: "POST" });
    const data = await res.json();
    const box = document.getElementById("mfa-enrollment-box");
    const content = document.getElementById("mfa-enrollment-content");
    box.style.display = "block";
    content.innerHTML = `
      <div style="background: var(--bg-muted); border: 1px solid var(--border-light); padding: 16px; border-radius: var(--radius-sm);">
        <p><strong>TOTP Secret Key:</strong> <code style="font-family: var(--font-mono); color: var(--primary); font-size: 13.5px; font-weight: 600;">${data.secret}</code></p>
        <p style="margin-top: 8px;"><strong>OTPAuth URI:</strong> <code style="font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); word-break: break-all;">${data.otpauth_uri}</code></p>
        <p style="margin-top: 8px; color: var(--success); font-weight: 500; font-size: 12px;">Algorithm: ${data.algorithm} | 6-Digits | 30s Window. Compatible with Google Authenticator, 1Password, and Microsoft Authenticator.</p>
      </div>
    `;
  } catch (err) {
    alert("MFA enrollment failed: " + err);
  }
}

// --------------------------------------------------------------------------
// 5. Platform Role Hierarchy (Figure 2.1)
// --------------------------------------------------------------------------
async function loadRoleHierarchy() {
  try {
    const res = await fetch("/api/v1/roles");
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.querySelector("#roles-table tbody");
    tbody.innerHTML = data.roles
      .map(
        (r) => `
      <tr>
        <td style="font-weight: 600; color: var(--text-main);">${r.name}</td>
        <td><span class="badge-tag">${r.level} Level</span></td>
        <td style="font-size: 12px; color: var(--text-muted);">${r.description}</td>
        <td><span class="badge-status ${r.is_system ? "synced" : "draft"}">${r.is_system ? "System Role" : "Custom"}</span></td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load roles:", err);
  }
}

// --------------------------------------------------------------------------
// 6. Cryptographic Audit Ledger & SHA-256 Verification (Section 7.6)
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
        <td style="font-family: var(--font-mono); font-size: 11px; color: var(--text-dim);">${b.audit_id.slice(0, 18)}...</td>
        <td style="font-weight: 600;">${b.action}</td>
        <td style="color: var(--text-main); font-size: 12px;">${b.actor_name}</td>
        <td><span class="badge-tag">${b.resource_type}</span></td>
        <td class="hash-cell">${b.previous_hash.slice(0, 10)}...${b.previous_hash.slice(-8)}</td>
        <td class="hash-cell">${b.entry_hash.slice(0, 10)}...${b.entry_hash.slice(-8)}</td>
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
  body.innerHTML = '<div class="terminal-line">Executing cryptographic SHA-256 validation pass...</div>';

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
    }, 150);
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
// 7. Key Vault (HashiCorp Vault & NIST SP 800-57)
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
        <td style="font-family: var(--font-mono); font-size: 12px; font-weight: 600; color: var(--text-main);">${s.path}</td>
        <td><span class="badge-tag">${s.cycle}</span></td>
        <td style="font-size: 12px; color: var(--text-light);">${s.last_rotation}</td>
        <td style="font-size: 12px; color: var(--text-light);">${s.next_rotation}</td>
        <td><span style="font-family: var(--font-mono); font-size: 11px; color: var(--primary); font-weight: 600;">${s.key_strength}</span></td>
        <td><span class="badge-status ${s.status.toLowerCase()}">${s.status}</span></td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="rotateKey('${s.path}')">Rotate Key</button>
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
    loadKafkaEvents();
    loadAuditLedger();
  } catch (err) {
    alert("Key rotation failed: " + err);
  }
}

// --------------------------------------------------------------------------
// 8. Feature Flags (Kill Switches)
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
    loadKafkaEvents();
    loadAuditLedger();
  } catch (err) {
    alert("Flag toggle failed: " + err);
  }
}

// --------------------------------------------------------------------------
// Modals & Event Listeners
// --------------------------------------------------------------------------
function setupEventListeners() {
  // Workspace Modal
  const wsModal = document.getElementById("ws-modal");
  const openWsBtn = document.getElementById("btn-open-ws-modal");
  const closeWsBtn = document.getElementById("btn-close-ws-modal");
  const cancelWsBtn = document.getElementById("btn-cancel-ws-modal");
  const wsForm = document.getElementById("ws-form");

  if (openWsBtn) openWsBtn.addEventListener("click", () => wsModal.classList.add("active"));
  if (closeWsBtn) closeWsBtn.addEventListener("click", () => wsModal.classList.remove("active"));
  if (cancelWsBtn) cancelWsBtn.addEventListener("click", () => wsModal.classList.remove("active"));

  if (wsForm) {
    wsForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const orgId = document.getElementById("ws-org-select").value;
      const name = document.getElementById("ws-name").value;
      const slug = document.getElementById("ws-slug").value;

      try {
        const res = await fetch(`/api/v1/organizations/${orgId}/workspaces`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, slug }),
        });
        if (res.ok) {
          wsModal.classList.remove("active");
          wsForm.reset();
          loadOrganizationsHierarchy();
          loadDashboardData();
          loadKafkaEvents();
          loadAuditLedger();
        }
      } catch (err) {
        alert("Failed to create workspace: " + err);
      }
    });
  }

  // Kafka Event Modal
  const evModal = document.getElementById("event-modal");
  const openEvBtn = document.getElementById("btn-open-event-modal");
  const closeEvBtn = document.getElementById("btn-close-event-modal");
  const cancelEvBtn = document.getElementById("btn-cancel-event-modal");
  const evForm = document.getElementById("event-form");

  if (openEvBtn) openEvBtn.addEventListener("click", () => evModal.classList.add("active"));
  if (closeEvBtn) closeEvBtn.addEventListener("click", () => evModal.classList.remove("active"));
  if (cancelEvBtn) cancelEvBtn.addEventListener("click", () => evModal.classList.remove("active"));

  if (evForm) {
    evForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const event_type = document.getElementById("event-type-select").value;
      const actor_email = document.getElementById("event-actor").value;
      const resource_name = document.getElementById("event-resource").value;

      try {
        const res = await fetch("/api/v1/events/publish", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ event_type, actor_email, resource_name }),
        });
        if (res.ok) {
          evModal.classList.remove("active");
          evForm.reset();
          loadKafkaEvents();
          loadAuditLedger();
        }
      } catch (err) {
        alert("Failed to publish event: " + err);
      }
    });
  }

  // SCIM Modal
  const scimModal = document.getElementById("scim-modal");
  const openScimBtn = document.getElementById("btn-open-scim-modal");
  const closeScimBtn = document.getElementById("btn-close-scim-modal");
  const cancelScimBtn = document.getElementById("btn-cancel-scim-modal");
  const scimForm = document.getElementById("scim-form");

  if (openScimBtn) openScimBtn.addEventListener("click", () => scimModal.classList.add("active"));
  if (closeScimBtn) closeScimBtn.addEventListener("click", () => scimModal.classList.remove("active"));
  if (cancelScimBtn) cancelScimBtn.addEventListener("click", () => scimModal.classList.remove("active"));

  if (scimForm) {
    scimForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        userName: document.getElementById("scim-username").value,
        givenName: document.getElementById("scim-given").value,
        familyName: document.getElementById("scim-family").value,
        role: document.getElementById("scim-role").value,
      };

      try {
        const res = await fetch("/api/v1/scim/v2/Users", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (res.ok) {
          scimModal.classList.remove("active");
          scimForm.reset();
          loadSCIMUsers();
          loadKafkaEvents();
          loadAuditLedger();
        }
      } catch (err) {
        alert("Failed to provision user: " + err);
      }
    });
  }

  // Audit Buttons
  const verifyBtn = document.getElementById("btn-verify-ledger");
  if (verifyBtn) verifyBtn.addEventListener("click", runLedgerVerification);

  const tamperBtn = document.getElementById("btn-simulate-tamper");
  if (tamperBtn) tamperBtn.addEventListener("click", simulateTamper);

  const restoreBtn = document.getElementById("btn-restore-ledger");
  if (restoreBtn) restoreBtn.addEventListener("click", restoreLedger);
}
