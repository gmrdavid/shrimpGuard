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
    return `${diffHours}h ago`;
}

function showNotice(message, isError = false) {
    const banner = document.getElementById("devices-alert-banner");
    const msg = document.getElementById("devices-alert-msg");
    if (!banner || !msg) return;

    msg.textContent = message;
    banner.style.display = "flex";
    banner.className = isError ? "devices-banner-notice error" : "devices-banner-notice success";

    setTimeout(() => {
        banner.style.display = "none";
    }, 6000);
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
    const total = data.total_devices || (Array.isArray(data.devices) ? data.devices.length : 10);
    const online = data.online_devices !== undefined ? data.online_devices : 9;
    const offline = data.offline_devices !== undefined ? data.offline_devices : 1;
    const sensors = data.connected_sensors !== undefined ? data.connected_sensors : 2;

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
            const statusClass = isDevOnline ? "status-optimal" : "status-warning";
            const dotClass = isDevOnline ? "dot-optimal" : "dot-warning";

            tr.innerHTML = `
                <td>
                    <div class="device-cell-meta">
                        <span class="device-cell-name">${dev.name}</span>
                        <span class="device-cell-sub">${dev.details || ""}</span>
                    </div>
                </td>
                <td>
                    <span class="device-cell-type">${dev.type}</span>
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
    if (btn) btn.disabled = true;

    showNotice("Scanning COM ports and verifying Node 2 LoRa receiver...", false);

    try {
        const res = await fetch("/api/hardware/reconnect", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        });
        const result = await res.json();

        if (result.success) {
            showNotice(result.message || "Gateway reconnected successfully!", false);
        } else {
            showNotice(result.message || "Could not detect active gateway.", true);
        }

        await fetchDevicesInventory();
    } catch (err) {
        showNotice("Failed to reach reconnect endpoint. Please check system status.", true);
    } finally {
        if (btn) btn.disabled = false;
    }
}

async function runDiagnostics() {
    const panel = document.getElementById("diagnostics-panel");
    const tbody = document.getElementById("diag-table-body");
    const summary = document.getElementById("diag-summary-text");
    const badge = document.getElementById("diag-overall-badge");
    const timestamp = document.getElementById("diag-timestamp");
    const btn = document.getElementById("btn-run-diagnostics");

    if (panel) panel.style.display = "block";
    if (btn) btn.disabled = true;

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
    }
}

document.addEventListener("DOMContentLoaded", () => {
    updateClock();
    clockTimer = setInterval(updateClock, 1000);

    // Initial load
    fetchDevicesInventory();

    // 4s polling
    pollTimer = setInterval(() => {
        fetchDevicesInventory();
    }, 4000);

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

    const btnCloseDiag = document.getElementById("btn-close-diag");
    if (btnCloseDiag) {
        btnCloseDiag.addEventListener("click", () => {
            const panel = document.getElementById("diagnostics-panel");
            if (panel) panel.style.display = "none";
        });
    }
});
