let cachedAlertsData = null;
let cachedHistory = [];
let currentFilter = {
    type: "all",
    todayOnly: true,
    customDate: "",
    status: "all",
    search: ""
};
let filterDrawerOpen = false;
let alertControlsInitialized = false;

function updateDeviceTime() {
    const timeEl = document.getElementById("time");
    if (timeEl) {
        timeEl.textContent = new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });
    }
}

function formatDateTime(isoString) {
    if (!isoString) return "-";
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return isoString;
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

function updateSummaryCards(alertsData) {
    if (!alertsData || !alertsData.summary) return;

    const summary = alertsData.summary;
    const critEl = document.getElementById("critical-alerts-count");
    const warnEl = document.getElementById("warning-alerts-count");
    const resEl = document.getElementById("resolved-alerts-count");
    const unreadEl = document.getElementById("unread-notifications-count");

    if (critEl) critEl.textContent = summary.critical_count ?? 0;
    if (warnEl) warnEl.textContent = summary.warning_count ?? 0;
    if (resEl) resEl.textContent = summary.resolved_count ?? 0;
    if (unreadEl) unreadEl.textContent = summary.unread_notifications ?? 0;

    // 1. Active Alerts
    const activeAlerts = alertsData.active_alerts || [];
    const activeAlertsContainer = document.getElementById("active-alerts");

    if (activeAlertsContainer) {
        if (activeAlerts.length === 0) {
            activeAlertsContainer.innerHTML = `
                <div class="status-box">
                    <svg class="ui-icon"><use href="#icon-check-circle"></use></svg> No active alerts right now. All monitored parameters are within the recommended range.
                </div>
            `;
        } else {
            activeAlertsContainer.innerHTML = activeAlerts.map((item) => `
                <div class="alert">
                    <svg class="ui-icon"><use href="${item.severity === "Critical" ? "#icon-alert" : "#icon-bell"}"></use></svg> <strong>${item.title}</strong>
                    <br>
                    ${item.message}
                    <br><br>
                    <strong>Notification:</strong> ${item.notification}
                </div>
            `).join("");
        }
    }

    // 2. Notification Delivery Status (Live from Database)
    const statusContainer = document.getElementById("notification-status");
    if (statusContainer) {
        const stats = summary.dispatch_stats || { sent: 0, delivered: 0, failed: 0 };
        statusContainer.className = "notification-status-panel";
        statusContainer.innerHTML = `
            <div class="notification-status-header">
                <h3>Notification Status</h3>
                <span class="notification-badge-live" style="font-size: 11px; color: #16a34a; font-weight: 750;">Connected to Database</span>
            </div>

            <div class="notification-status-subtitle">Push Notification (ntfy.sh Telemetry)</div>

            <div class="notification-status-row">
                <div class="notification-status-main">
                    <div class="notification-status-icon success"><svg class="ui-icon"><use href="#icon-check"></use></svg></div>
                    <div class="notification-status-copy">
                        <div class="notification-status-value">${stats.sent}</div>
                        <div class="notification-status-label">Sent</div>
                    </div>
                </div>
                <div class="notification-status-date">Telemetry Active</div>
            </div>

            <div class="notification-status-row">
                <div class="notification-status-main">
                    <div class="notification-status-icon success"><svg class="ui-icon"><use href="#icon-check"></use></svg></div>
                    <div class="notification-status-copy">
                        <div class="notification-status-value">${stats.delivered}</div>
                        <div class="notification-status-label">Delivered</div>
                    </div>
                </div>
                <div class="notification-status-date">Verified</div>
            </div>

            <div class="notification-status-row">
                <div class="notification-status-main">
                    <div class="notification-status-icon ${stats.failed > 0 ? "danger" : "success"}"><svg class="ui-icon"><use href="${stats.failed > 0 ? "#icon-x" : "#icon-check"}"></use></svg></div>
                    <div class="notification-status-copy">
                        <div class="notification-status-value">${stats.failed}</div>
                        <div class="notification-status-label">Failed</div>
                    </div>
                </div>
                <div class="notification-status-date">No errors</div>
            </div>
        `;
    }
}

function renderRecentNotifications(notifications) {
    const container = document.getElementById("recent-notifications");
    if (!container) return;

    if (!Array.isArray(notifications) || notifications.length === 0) {
        container.innerHTML = `
            <div class="status-box">
                No recent notifications recorded. All parameters are optimal.
            </div>
        `;
        return;
    }

    container.innerHTML = notifications.map((item) => `
        <div class="alert">
            <svg class="ui-icon"><use href="${item.severity === "Critical" ? "#icon-alert" : "#icon-bell"}"></use></svg>
            <strong>${item.title}</strong>
            <br>
            ${item.message}
            <br>
            <small style="color: #6d8477; display: block; margin-top: 4px;">${formatDateTime(item.recorded_at)}</small>
        </div>
    `).join("");
}

function filterAlertHistory(history) {
    if (!Array.isArray(history)) return [];

    return history.filter((item) => {
        const readingDateObj = new Date(item.recorded_at);
        const hasDate = !isNaN(readingDateObj.getTime());

        // 1. Timeframe filter (Today)
        if (currentFilter.todayOnly && !currentFilter.customDate && hasDate) {
            const today = new Date();
            const isSameDay =
                readingDateObj.getFullYear() === today.getFullYear() &&
                readingDateObj.getMonth() === today.getMonth() &&
                readingDateObj.getDate() === today.getDate();
            if (!isSameDay) return false;
        }

        // 2. Custom Date filter (YYYY-MM-DD)
        if (currentFilter.customDate && hasDate) {
            const localReadingDate = `${readingDateObj.getFullYear()}-${String(readingDateObj.getMonth() + 1).padStart(2, "0")}-${String(readingDateObj.getDate()).padStart(2, "0")}`;
            if (localReadingDate !== currentFilter.customDate) return false;
        }

        // 3. Type filter
        if (currentFilter.type === "critical") {
            if (item.severity !== "Critical") return false;
        } else if (currentFilter.type === "warning") {
            if (item.severity !== "Warning") return false;
        } else if (currentFilter.type === "temperature") {
            if (!item.alerts || !item.alerts.some((a) => a.type === "temperature" || a.type === "combined")) return false;
        } else if (currentFilter.type === "ph") {
            if (!item.alerts || !item.alerts.some((a) => a.type === "ph" || a.type === "combined")) return false;
        } else if (currentFilter.type === "resolved") {
            if (item.status !== "Resolved" && item.alert_count > 0) return false;
        }

        // 4. Status filter
        if (currentFilter.status === "Active" && item.status !== "Active") return false;
        if (currentFilter.status === "Resolved" && item.status !== "Resolved") return false;

        // 5. Search keyword
        if (currentFilter.search) {
            const query = currentFilter.search.toLowerCase();
            const dateStr = hasDate ? readingDateObj.toLocaleDateString().toLowerCase() : "";
            const timeStr = hasDate ? readingDateObj.toLocaleTimeString().toLowerCase() : "";
            const detailsStr = (item.details || "").toLowerCase();
            const statusStr = (item.status || "").toLowerCase();
            const severityStr = (item.severity || "").toLowerCase();
            const textMatch =
                dateStr.includes(query) ||
                timeStr.includes(query) ||
                detailsStr.includes(query) ||
                statusStr.includes(query) ||
                severityStr.includes(query);
            if (!textMatch) return false;
        }

        return true;
    });
}

function renderAlertHistory(history) {
    const tableBody = document.getElementById("alert-history-body");
    if (!tableBody) return;

    const filtered = filterAlertHistory(history);

    if (!filtered.length) {
        let msg = "No alert history recorded in the database.";
        if (currentFilter.todayOnly && !currentFilter.customDate) {
            msg = "No alerts recorded today in the database.";
        } else if (
            currentFilter.customDate ||
            currentFilter.type !== "all" ||
            currentFilter.search ||
            currentFilter.status !== "all"
        ) {
            msg = "No alert history matches the selected filters.";
        }
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="table-empty" style="text-align: center; padding: 28px 14px; color: #8a998f;">
                    ${msg}
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = filtered.map((item) => {
        const d = new Date(item.recorded_at);
        const dateStr = !isNaN(d.getTime()) ? d.toLocaleDateString() : item.recorded_at;
        const timeStr = !isNaN(d.getTime()) ? d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "-";

        const severityBadge = item.severity === "Critical"
            ? '<span class="severity-badge severity-critical">Critical</span>'
            : item.severity === "Warning"
            ? '<span class="severity-badge severity-warning">Warning</span>'
            : '<span class="severity-badge severity-none">Optimal</span>';

        const statusPill = item.status === "Active"
            ? '<span class="status-pill status-active">Active</span>'
            : '<span class="status-pill status-resolved">Resolved</span>';

        return `
            <tr>
                <td>${dateStr}</td>
                <td>${timeStr}</td>
                <td><strong>${item.alert_count}</strong></td>
                <td>${severityBadge}</td>
                <td>${statusPill}</td>
                <td>${item.details}</td>
            </tr>
        `;
    }).join("");
}

function updateActiveFilterBadge() {
    let count = 0;
    if (currentFilter.type !== "all") count++;
    if (!currentFilter.todayOnly && currentFilter.customDate) count++;
    if (currentFilter.status !== "all") count++;
    if (currentFilter.search.trim().length > 0) count++;

    const badge = document.getElementById("active-filter-badge");
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.hidden = false;
        } else {
            badge.hidden = true;
        }
    }
}

function initAlertHistoryControls() {
    if (alertControlsInitialized) return;

    const typeSelect = document.getElementById("alert-type-select");
    const todayButton = document.getElementById("alert-today-button");
    const filterToggle = document.getElementById("alert-filter-toggle");
    const filterDrawer = document.getElementById("alert-filter-drawer");
    const customDateInput = document.getElementById("alert-custom-date");
    const statusSelect = document.getElementById("alert-status-select");
    const searchInput = document.getElementById("alert-search-input");
    const resetButton = document.getElementById("alert-reset-filters");

    if (typeSelect) {
        typeSelect.addEventListener("change", (e) => {
            currentFilter.type = e.target.value;
            updateActiveFilterBadge();
            renderAlertHistory(cachedHistory);
        });
    }

    if (todayButton) {
        todayButton.addEventListener("click", () => {
            currentFilter.todayOnly = !currentFilter.todayOnly;
            if (currentFilter.todayOnly) {
                currentFilter.customDate = "";
                if (customDateInput) customDateInput.value = "";
                todayButton.classList.add("active");
                todayButton.setAttribute("aria-pressed", "true");
            } else {
                todayButton.classList.remove("active");
                todayButton.setAttribute("aria-pressed", "false");
            }
            updateActiveFilterBadge();
            renderAlertHistory(cachedHistory);
        });
    }

    if (filterToggle && filterDrawer) {
        filterToggle.addEventListener("click", () => {
            filterDrawerOpen = !filterDrawerOpen;
            filterDrawer.hidden = !filterDrawerOpen;
            filterToggle.setAttribute("aria-expanded", String(filterDrawerOpen));
            if (filterDrawerOpen) {
                filterToggle.classList.add("active");
            } else {
                filterToggle.classList.remove("active");
            }
        });
    }

    if (customDateInput) {
        customDateInput.addEventListener("change", (e) => {
            currentFilter.customDate = e.target.value;
            if (currentFilter.customDate) {
                currentFilter.todayOnly = false;
                if (todayButton) {
                    todayButton.classList.remove("active");
                    todayButton.setAttribute("aria-pressed", "false");
                }
            }
            updateActiveFilterBadge();
            renderAlertHistory(cachedHistory);
        });
    }

    if (statusSelect) {
        statusSelect.addEventListener("change", (e) => {
            currentFilter.status = e.target.value;
            updateActiveFilterBadge();
            renderAlertHistory(cachedHistory);
        });
    }

    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener("input", (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                currentFilter.search = e.target.value;
                updateActiveFilterBadge();
                renderAlertHistory(cachedHistory);
            }, 250);
        });
    }

    if (resetButton) {
        resetButton.addEventListener("click", () => {
            currentFilter = {
                type: "all",
                todayOnly: false,
                customDate: "",
                status: "all",
                search: ""
            };
            if (typeSelect) typeSelect.value = "all";
            if (todayButton) {
                todayButton.classList.remove("active");
                todayButton.setAttribute("aria-pressed", "false");
            }
            if (customDateInput) customDateInput.value = "";
            if (statusSelect) statusSelect.value = "all";
            if (searchInput) searchInput.value = "";
            updateActiveFilterBadge();
            renderAlertHistory(cachedHistory);
        });
    }

    alertControlsInitialized = true;
}

async function loadAlertsData() {
    try {
        const response = await fetch("/api/alerts");
        if (!response.ok) {
            throw new Error(`Alerts API returned ${response.status}`);
        }
        const data = await response.json();
        cachedAlertsData = data;
        cachedHistory = data.history_items || [];

        initAlertHistoryControls();
        updateSummaryCards(data);
        renderRecentNotifications(data.recent_notifications || []);
        renderAlertHistory(cachedHistory);
    } catch (error) {
        console.error("Unable to load sensor data for alerts:", error);
        const activeContainer = document.getElementById("active-alerts");
        const recentContainer = document.getElementById("recent-notifications");
        const historyBody = document.getElementById("alert-history-body");
        const statusContainer = document.getElementById("notification-status");

        if (activeContainer) activeContainer.innerHTML = '<div class="status-box">Unable to load database alerts. Please refresh or retry.</div>';
        if (recentContainer) recentContainer.innerHTML = '<div class="status-box">Unable to load notifications. Please refresh or retry.</div>';
        if (historyBody) historyBody.innerHTML = '<tr><td colspan="6" class="table-empty" style="text-align: center; padding: 24px; color: #8a998f;">Unable to connect to alerts database.</td></tr>';
        if (statusContainer) statusContainer.innerHTML = '<div class="status-box">Sensor database unavailable.</div>';
    }
}

updateDeviceTime();
setInterval(updateDeviceTime, 1000);
loadAlertsData();
setInterval(loadAlertsData, 10000);
