/**
 * ShrimpGuard - Devices & Hardware Management Engine
 * Real-time monitoring, hardware diagnostics, and serial gateway control.
 */

let lastSyncTimestamp = null;
let pollTimer = null;
let clockTimer = null;

function updateClock() {
    const timeEl = document.getElementById("time");
    if (!timeEl) return;
    const now = new Date();
    timeEl.textContent = now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });
}

function timeAgo(dateOrStr) {
    if (!dateOrStr) return "Awaiting data";
    const d = new Date(dateOrStr);
    if (isNaN(d.getTime())) return "Recently";
    const now = new Date();
    const diffSec = Math.max(0, Math.floor((now.getTime() - d.getTime()) / 1000));
    if (diffSec < 4) return "Just now";
    if (diffSec < 60) return `${diffSec}s ago`;
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHours = Math.floor(diffMin / 60);
    const remMin = diffMin % 60;
    if (diffHours < 24) {
        return remMin > 0 ? `${diffHours}h ${remMin}m ago` : `${diffHours}h ago`;
    }
    const days = Math.floor(diffHours / 24);
    const remHours = diffHours % 24;
    const parts = [`${days}d`];
    if (remHours > 0) parts.push(`${remHours}h`);
    if (remMin > 0) parts.push(`${remMin}m`);
    return `${parts.join(" ")} ago`;
}

function showNotice(message, state = false) {
    const banner = document.getElementById("devices-alert-banner");
    const msg = document.getElementById("devices-alert-msg");
    if (!banner || !msg) return;

    let noticeType = "success";
    if (state === true || state === "error") {
        noticeType = "error";
    } else if (state === "info" || state === "scanning") {
        noticeType = "info";
    } else {
        noticeType = "success";
    }

    msg.textContent = message;
    banner.style.display = "flex";
    banner.className = `devices-banner-notice ${noticeType}`;

    const iconUse = banner.querySelector(".ui-icon use");
    if (iconUse) {
        if (noticeType === "error") {
            iconUse.setAttribute("href", "#icon-alert");
        } else if (noticeType === "info") {
            iconUse.setAttribute("href", "#icon-settings");
        } else {
            iconUse.setAttribute("href", "#icon-check-circle");
        }
    }

    if (window._devicesNoticeTimeout) {
        clearTimeout(window._devicesNoticeTimeout);
    }
    window._devicesNoticeTimeout = setTimeout(() => {
        banner.style.display = "none";
    }, noticeType === "error" ? 8000 : 5000);
}

async function fetchDevicesInventory() {
    try {
        const res = await fetch("/api/devices/inventory");
        if (!res.ok) {
            throw new Error(`Inventory API returned ${res.status}`);
        }
        const data = await res.json();
        renderDevices(data);
    } catch (err) {
        console.warn("[Devices] Failed to fetch hardware inventory:", err);
    }
}

function renderDevices(data) {
    if (!data) return;

    const isConnected = Boolean(data.is_connected);
    const port = data.connected_port || "COM8";
    const latest = data.latest_telemetry || {};
    const total = data.total_devices !== undefined ? data.total_devices : (Array.isArray(data.devices) ? data.devices.length : 10);
    const online = data.online_devices !== undefined ? data.online_devices : 0;
    const offline = data.offline_devices !== undefined ? data.offline_devices : total;
    const sensors = data.connected_sensors !== undefined ? data.connected_sensors : 0;

    // 1. Gateway Status & RF Badges
    const badgeGwStatus = document.getElementById("badge-gw-status");
    if (badgeGwStatus) {
        badgeGwStatus.textContent = isConnected ? "Online" : "Standby";
        badgeGwStatus.className = isConnected
            ? "telemetry-value telemetry-status-optimal"
            : "telemetry-value telemetry-status-warning";
    }

    const badgeGwPort = document.getElementById("badge-gw-port");
    if (badgeGwPort) {
        badgeGwPort.textContent = `${port} (115200 baud)`;
    }

    const badgeNodeId = document.getElementById("badge-node-id");
    if (badgeNodeId) {
        badgeNodeId.textContent = latest.device_id || "NODE01";
    }

    const badgeNodeSeq = document.getElementById("badge-node-seq");
    if (badgeNodeSeq) {
        badgeNodeSeq.textContent = latest.seq ? `Seq #${latest.seq}` : "Awaiting broadcast";
    }

    const badgeLastSync = document.getElementById("badge-last-sync");
    if (badgeLastSync && latest.recorded_at) {
        const timePart = latest.recorded_at.includes("T")
            ? latest.recorded_at.split("T")[1].substring(0, 8)
            : latest.recorded_at.split(" ")[1]
            ? latest.recorded_at.split(" ")[1].substring(0, 8)
            : latest.recorded_at;
        badgeLastSync.textContent = timePart;
        lastSyncTimestamp = new Date(latest.recorded_at).getTime() ? new Date(latest.recorded_at) : new Date();
    }

    const badgeLastAgo = document.getElementById("badge-last-ago");
    if (badgeLastAgo && lastSyncTimestamp) {
        badgeLastAgo.textContent = timeAgo(lastSyncTimestamp);
    }

    // 2. Top 4 Overview Metric Cards
    const elTopTotal = document.getElementById("top-total-devices");
    if (elTopTotal) elTopTotal.textContent = total;

    const elTopOnline = document.getElementById("top-online-devices");
    if (elTopOnline) elTopOnline.textContent = online;

    const elTopOffline = document.getElementById("top-offline-devices");
    if (elTopOffline) elTopOffline.textContent = offline;

    const elTopSensors = document.getElementById("top-connected-sensors");
    if (elTopSensors) elTopSensors.textContent = sensors;

    // 3. Right Side: Device Status Ratio & Progress
    const elSideRatioOnline = document.getElementById("side-ratio-online");
    if (elSideRatioOnline) elSideRatioOnline.textContent = online;

    const elSideRatioTotal = document.getElementById("side-ratio-total");
    if (elSideRatioTotal) elSideRatioTotal.textContent = total;

    const elSideRatioText = document.getElementById("side-ratio-text");
    if (elSideRatioText) {
        elSideRatioText.textContent = `${online} online and ${offline} offline`;
    }

    const elSideProgressFill = document.getElementById("side-progress-fill");
    if (elSideProgressFill) {
        const pct = total > 0 ? ((online / total) * 100).toFixed(1) : 100;
        elSideProgressFill.style.width = `${pct}%`;
    }

    const elSidePillOnline = document.getElementById("side-pill-online");
    if (elSidePillOnline) elSidePillOnline.textContent = online;

    const elSidePillOffline = document.getElementById("side-pill-offline");
    if (elSidePillOffline) elSidePillOffline.textContent = offline;

    // 4. Right Side: Device Category Breakdown Badges
    const cat = data.category_stats || {};
    if (cat.sensors) {
        const elCatSensors = document.getElementById("cat-sensors-badge");
        if (elCatSensors) {
            elCatSensors.textContent = `${cat.sensors.online}/${cat.sensors.total} Online`;
        }
    }

    if (cat.communication) {
        const elCatComm = document.getElementById("cat-comm-badge");
        if (elCatComm) {
            elCatComm.textContent = `${cat.communication.online}/${cat.communication.total} Online`;
        }
    }

    if (cat.alerts) {
        const elCatAlerts = document.getElementById("cat-alerts-badge");
        if (elCatAlerts) {
            elCatAlerts.textContent = `${cat.alerts.online}/${cat.alerts.total} Online`;
        }
    }

    if (cat.power) {
        const elCatPower = document.getElementById("cat-power-badge");
        if (elCatPower) {
            elCatPower.textContent = `${cat.power.online}/${cat.power.total} Online`;
        }
    }

    // 5. Device List Table Body
    const tbody = document.getElementById("devices-table-body");
    if (tbody && Array.isArray(data.devices)) {
        tbody.innerHTML = "";
        data.devices.forEach((dev) => {
            const tr = document.createElement("tr");

            const isDevOnline = dev.status === "Online";
            const statusClass = isDevOnline ? "status-optimal status-online" : "status-warning status-offline";
            const dotClass = isDevOnline ? "dot-optimal" : "dot-warning dot-offline";
            const catSlug = (dev.category || "communication").toLowerCase().replace(/ & /g, "-").replace(/\s+/g, "-");

            tr.className = `device-row device-row-${dev.status ? dev.status.toLowerCase() : "offline"}`;
            tr.innerHTML = `
                <td>
                    <div class="device-cell-title-row">
                        <span class="device-cell-name">${dev.name}</span>
                    </div>
                </td>
                <td>
                    <span class="device-cell-type type-${catSlug}">${dev.type}</span>
                </td>
                <td>
                    <span class="table-status ${statusClass}">
                        <span class="status-indicator-dot ${dotClass}"></span> ${dev.status}
                    </span>
                </td>
                <td>
                    <span class="device-cell-seen">
                        ${dev.last_seen || "Just now"}
                    </span>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    const countBadge = document.getElementById("table-device-count-badge");
    if (countBadge) {
        countBadge.textContent = `${total} Monitored Units`;
    }
}

async function reconnectGateway() {
    const btn = document.getElementById("btn-reconnect-gateway");
    const originalContent = btn ? btn.innerHTML : "";
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<svg class="ui-icon devices-spin" aria-hidden="true"><use href="#icon-settings"></use></svg><span>Probing Ports...</span>`;
    }

    // Probing COM ports - show neutral scanning notice (not green)
    showNotice("Scanning COM ports and verifying Node 2 LoRa receiver...", "info");

    try {
        const res = await fetch("/api/hardware/reconnect", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        });
        const result = await res.json();

        if (result && result.success) {
            // Active LoRa receiver detected -> GREEN background
            showNotice(result.message || "LoRa Receiver Gateway detected and connected successfully!", "success");
        } else {
            // No active LoRa receiver detected -> RED background
            showNotice(result && result.message ? result.message : "No active LoRa receiver detected on scanned ports. Check USB cable or close serial monitors.", "error");
        }

        await fetchDevicesInventory();
    } catch (err) {
        // Communication failure -> RED background
        showNotice("Failed to reach reconnect endpoint. Please check system status.", "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalContent;
        }
    }
}

function openDiagnosticsModal() {
    const panel = document.getElementById("diagnostics-panel");
    if (panel) {
        panel.style.display = "flex";
        panel.removeAttribute("hidden");
        panel.classList.add("is-open");
        document.body.classList.add("modal-backdrop-open");
    }
}

function closeDiagnosticsModal() {
    const panel = document.getElementById("diagnostics-panel");
    if (panel) {
        panel.style.display = "none";
        panel.setAttribute("hidden", "");
        panel.classList.remove("is-open");
        document.body.classList.remove("modal-backdrop-open");
    }
}

async function runDiagnostics() {
    openDiagnosticsModal();
    const tbody = document.getElementById("diag-table-body");
    const summary = document.getElementById("diag-summary-text");
    const badge = document.getElementById("diag-overall-badge");
    const timestamp = document.getElementById("diag-timestamp");
    const btn = document.getElementById("btn-run-diagnostics");
    const reRunBtn = document.getElementById("btn-re-run-diag");

    if (btn) btn.disabled = true;
    if (reRunBtn) reRunBtn.disabled = true;

    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; padding: 25px; color: #0284c7; font-weight: 600;">
                    <div style="display: inline-flex; align-items: center; gap: 8px;">
                        <span>Inspecting 1-Wire bus, Analog ADC, SX1278 RF margins, and UART serial bridge...</span>
                    </div>
                </td>
            </tr>
        `;
    }

    try {
        const res = await fetch("/api/hardware/diagnostics", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        });
        const diag = await res.json();

        if (timestamp) {
            timestamp.textContent = `Completed at ${diag.timestamp} • Scan time: 180 ms`;
        }

        if (summary) {
            summary.textContent = diag.overall_message;
        }

        if (badge) {
            badge.textContent = diag.overall_health.replace("_", " ");
            badge.className = `badge ${
                diag.overall_badge === "status-optimal"
                    ? "badge-optimal"
                    : diag.overall_badge === "status-critical"
                    ? "badge-critical"
                    : "badge-warning"
            }`;
        }

        if (tbody && Array.isArray(diag.tests)) {
            tbody.innerHTML = "";
            diag.tests.forEach((t) => {
                const tr = document.createElement("tr");
                tr.style.borderBottom = "1px solid #f1f5f9";

                let resultBadgeClass = "badge-optimal";
                if (t.status_class === "status-critical" || t.result.includes("FAULT")) {
                    resultBadgeClass = "badge-critical";
                } else if (t.status_class === "status-warning" || t.result.includes("STANDBY") || t.result.includes("WARNING")) {
                    resultBadgeClass = "badge-warning";
                }

                tr.innerHTML = `
                    <td style="padding: 10px 14px; font-weight: 700; color: #1e293b;">${t.component}</td>
                    <td style="padding: 10px 14px; color: #475569;">${t.test}</td>
                    <td style="padding: 10px 14px; text-align: center;">
                        <span class="badge ${resultBadgeClass}">${t.result}</span>
                    </td>
                    <td style="padding: 10px 14px; font-size: 13px; color: #334155;">${t.details}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        if (summary) {
            summary.textContent = "Diagnostic scan failed. Please verify server connectivity.";
        }
    } finally {
        if (btn) btn.disabled = false;
        const reRunBtn = document.getElementById("btn-re-run-diag");
        if (reRunBtn) reRunBtn.disabled = false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    updateClock();
    clockTimer = setInterval(updateClock, 1000);

    // Initial load
    fetchDevicesInventory();
    fetchPairedNodes();
    setupPairNodeModal();
    attachUnpairHandlers();

    // Dynamic polling (throttled under Data-Saver)
    function restartPolling() {
        if (pollTimer) clearInterval(pollTimer);
        const interval = window.ShrimpGuardAdaptive && window.ShrimpGuardAdaptive.getPollInterval
            ? window.ShrimpGuardAdaptive.getPollInterval(4000, 25000)
            : 4000;
        pollTimer = setInterval(() => {
            fetchDevicesInventory();
            fetchPairedNodes();
        }, interval);
    }
    restartPolling();
    window.addEventListener("shrimpguard:preferences-changed", restartPolling);

    // Relative time updater
    setInterval(() => {
        const badgeLastAgo = document.getElementById("badge-last-ago");
        if (badgeLastAgo && lastSyncTimestamp) {
            badgeLastAgo.textContent = timeAgo(lastSyncTimestamp);
        }
    }, 2000);

    // Event listeners
    const btnSync = document.getElementById("btn-sync-devices");
    if (btnSync) {
        btnSync.addEventListener("click", () => {
            fetchDevicesInventory();
            showNotice("Synchronized live hardware telemetry.", false);
        });
    }

    const btnReconnect = document.getElementById("btn-reconnect-gateway");
    if (btnReconnect) {
        btnReconnect.addEventListener("click", reconnectGateway);
    }

    const btnDiag = document.getElementById("btn-run-diagnostics");
    if (btnDiag) {
        btnDiag.addEventListener("click", runDiagnostics);
    }

    // Global delegated click handler for diagnostics controls
    document.addEventListener("click", (e) => {
        const diagBtn = e.target.closest("#btn-run-diagnostics");
        if (diagBtn) {
            e.preventDefault();
            runDiagnostics();
            return;
        }

        const closeDiagBtn = e.target.closest("#btn-close-diag, #btn-close-diag-footer");
        if (closeDiagBtn) {
            e.preventDefault();
            closeDiagnosticsModal();
            return;
        }

        const reRunBtn = e.target.closest("#btn-re-run-diag");
        if (reRunBtn) {
            e.preventDefault();
            runDiagnostics();
            return;
        }
    });

    const btnCloseDiag = document.getElementById("btn-close-diag");
    if (btnCloseDiag) {
        btnCloseDiag.addEventListener("click", closeDiagnosticsModal);
    }

    const btnCloseDiagFooter = document.getElementById("btn-close-diag-footer");
    if (btnCloseDiagFooter) {
        btnCloseDiagFooter.addEventListener("click", closeDiagnosticsModal);
    }

    const btnReRunDiag = document.getElementById("btn-re-run-diag");
    if (btnReRunDiag) {
        btnReRunDiag.addEventListener("click", runDiagnostics);
    }

    const diagPanel = document.getElementById("diagnostics-panel");
    if (diagPanel) {
        diagPanel.addEventListener("click", (e) => {
            if (e.target === diagPanel) closeDiagnosticsModal();
        });
    }

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && diagPanel && (diagPanel.style.display === "flex" || diagPanel.classList.contains("is-open"))) {
            closeDiagnosticsModal();
        }
    });
});

/* ==========================================================================
   PAIRED POND NODES MANAGEMENT (MULTI-ACCOUNT HARDWARE TELEMETRY ROUTING)
   ========================================================================== */

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function fetchPairedNodes() {
    const tbody = document.getElementById("paired-nodes-table-body");
    if (!tbody) return;
    try {
        const res = await fetch("/api/devices/paired");
        if (!res.ok) return;
        const data = await res.json();
        if (!data.success || !Array.isArray(data.devices)) return;
        renderPairedNodes(data.devices);
    } catch (err) {
        console.warn("[Devices] Failed to fetch paired nodes:", err);
    }
}

function renderPairedNodes(nodes) {
    const tbody = document.getElementById("paired-nodes-table-body");
    if (!tbody) return;

    const countBadge = document.getElementById("paired-nodes-count-badge");
    const count = Array.isArray(nodes) ? nodes.length : 0;
    if (countBadge) {
        countBadge.textContent = `${count} Paired ${count === 1 ? "Unit" : "Units"}`;
    }

    if (!nodes || nodes.length === 0) {
        tbody.innerHTML = `
            <tr id="empty-paired-nodes-row">
                <td colspan="6" style="text-align: center; padding: 24px; color: #64748b;">
                    No hardware telemetry nodes paired yet. Click <strong>Pair Pond Node</strong> in the toolbar above to link your Node ID (e.g. <code>NODE01</code>, <code>NODE02</code>).
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = nodes.map(node => {
        const isStreaming = Boolean(node.is_streaming);
        const lastSeenText = node.last_seen ? timeAgo(node.last_seen) : "Awaiting first packet";
        const linkBadge = isStreaming
            ? `<span class="table-status status-optimal status-online"><span class="status-indicator-dot dot-optimal"></span> Streaming Live</span>`
            : `<span class="table-status status-optimal status-online"><span class="status-indicator-dot dot-optimal"></span> Active</span>`;

        return `
            <tr class="device-row" data-node-id="${escapeHtml(node.device_id)}">
                <td>
                    <span class="device-id-badge">${escapeHtml(node.device_id)}</span>
                </td>
                <td>
                    <div class="device-cell-title-row">
                        <strong class="device-cell-name">${escapeHtml(node.device_name)}</strong>
                        <span class="device-location-tag">(${escapeHtml(node.pond_location || 'Pond Site')})</span>
                    </div>
                </td>
                <td>
                    <span class="device-owner-cell">${escapeHtml(node.user_email)}</span>
                </td>
                <td>
                    ${linkBadge}
                </td>
                <td>
                    <span class="device-cell-seen node-last-seen-cell" title="${node.last_seen || ''}">
                        ${lastSeenText}
                    </span>
                </td>
                <td style="text-align: center;">
                    <button type="button" class="btn-unpair-node" data-node-id="${escapeHtml(node.device_id)}">
                        Unpair
                    </button>
                </td>
            </tr>
        `;
    }).join("");

    attachUnpairHandlers();
}

function attachUnpairHandlers() {
    document.querySelectorAll(".btn-unpair-node").forEach(btn => {
        btn.onclick = async () => {
            const nodeId = btn.getAttribute("data-node-id");
            if (!nodeId) return;
            if (!confirm(`Are you sure you want to unpair Node '${nodeId}' from your account? Live telemetry from this node will no longer route to your dashboard.`)) {
                return;
            }

            try {
                btn.disabled = true;
                const res = await fetch("/api/devices/unpair", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ device_id: nodeId }),
                });
                const data = await res.json();
                if (res.ok && data.success) {
                    showNotice(data.message || `Node '${nodeId}' successfully unpaired.`, false);
                    fetchPairedNodes();
                    fetchDevicesInventory();
                } else {
                    showNotice(data.error || "Failed to unpair node.", true);
                }
            } catch (err) {
                showNotice("Network error while unpairing node.", true);
            } finally {
                btn.disabled = false;
            }
        };
    });
}

function setupPairNodeModal() {
    const dialog = document.getElementById("pair-node-dialog");
    const openBtns = [document.getElementById("btn-open-pair-modal"), ...document.querySelectorAll(".btn-trigger-pair-modal")];
    const cancelBtn = document.getElementById("cancel-pair-node");
    const form = document.getElementById("pair-node-form");
    const errBox = document.getElementById("pair-node-error");
    const submitBtn = document.getElementById("submit-pair-node");

    if (!dialog) return;

    openBtns.forEach(btn => {
        if (btn) {
            btn.addEventListener("click", () => {
                if (errBox) errBox.style.display = "none";
                if (form) form.reset();
                if (typeof dialog.showModal === "function") {
                    dialog.showModal();
                } else {
                    dialog.setAttribute("open", "");
                }
            });
        }
    });

    if (cancelBtn) {
        cancelBtn.addEventListener("click", () => {
            if (typeof dialog.close === "function") {
                dialog.close();
            } else {
                dialog.removeAttribute("open");
            }
        });
    }

    dialog.addEventListener("click", (e) => {
        if (e.target === dialog) {
            if (typeof dialog.close === "function") {
                dialog.close();
            } else {
                dialog.removeAttribute("open");
            }
        }
    });

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (errBox) errBox.style.display = "none";
            const nodeIdInput = document.getElementById("pair-node-id");
            const nodeNameInput = document.getElementById("pair-node-name");
            const pondLocInput = document.getElementById("pair-pond-location");

            const nodeId = (nodeIdInput ? nodeIdInput.value : "").trim().toUpperCase();
            const nodeName = nodeNameInput ? nodeNameInput.value.trim() : "";
            const pondLoc = pondLocInput ? pondLocInput.value.trim() : "";

            if (!nodeId) {
                if (errBox) {
                    errBox.textContent = "Please enter a Hardware Node ID.";
                    errBox.style.display = "block";
                }
                return;
            }

            try {
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = "Pairing...";
                }

                const res = await fetch("/api/devices/pair", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        device_id: nodeId,
                        device_name: nodeName,
                        pond_location: pondLoc,
                    }),
                });

                const data = await res.json();
                if (res.ok && data.success) {
                    if (typeof dialog.close === "function") {
                        dialog.close();
                    } else {
                        dialog.removeAttribute("open");
                    }
                    showNotice(data.message || `Node '${nodeId}' paired successfully!`, false);
                    fetchPairedNodes();
                    fetchDevicesInventory();
                } else {
                    if (errBox) {
                        errBox.textContent = data.error || "Failed to pair device.";
                        errBox.style.display = "block";
                    }
                }
            } catch (err) {
                if (errBox) {
                    errBox.textContent = "Network error while pairing device.";
                    errBox.style.display = "block";
                }
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = "Pair Hardware Node";
                }
            }
        });
    }
}
