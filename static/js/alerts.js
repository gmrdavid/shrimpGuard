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

function getAlertData(reading) {
    const alerts = [];

    if (!reading) {
        return alerts;
    }

    if (reading.temperature < 26 || reading.temperature > 32) {
        const severity = reading.temperature < 24 || reading.temperature > 34 ? "Critical" : "Warning";
        alerts.push({
            type: "temperature",
            severity,
            title: `${severity} Temperature Alert`,
            message: `Temperature is currently ${reading.temperature} °C, outside the recommended range of 26–32 °C.`,
            notification: `SMS: Pond temperature is ${reading.temperature} °C. Check cooling or heating systems and respond promptly.`
        });
    }

    if (reading.ph < 7.5 || reading.ph > 8.5) {
        const severity = reading.ph < 7.0 || reading.ph > 9.0 ? "Critical" : "Warning";
        alerts.push({
            type: "ph",
            severity,
            title: `${severity} pH Alert`,
            message: `pH is currently ${reading.ph}, outside the recommended range of 7.5–8.5.`,
            notification: `SMS: pH is ${reading.ph}. Adjust water treatment and verify the pH control system.`
        });
    }

    return alerts;
}

function formatDateTime(isoString) {
    if (!isoString) {
        return "-";
    }

    const date = new Date(isoString);
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

function updateSummaryCards(history, latestReading) {
    const alertsFromHistory = history.flatMap((reading) => getAlertData(reading));
    const criticalAlerts = alertsFromHistory.filter((alert) => alert.severity === "Critical").length;
    const warningAlerts = alertsFromHistory.filter((alert) => alert.severity === "Warning").length;
    const resolvedAlerts = history.filter((reading) => getAlertData(reading).length === 0).length;
    const unreadNotifications = alertsFromHistory.length;

    const critEl = document.getElementById("critical-alerts-count");
    const warnEl = document.getElementById("warning-alerts-count");
    const resEl = document.getElementById("resolved-alerts-count");
    const unreadEl = document.getElementById("unread-notifications-count");

    if (critEl) critEl.textContent = criticalAlerts;
    if (warnEl) warnEl.textContent = warningAlerts;
    if (resEl) resEl.textContent = resolvedAlerts;
    if (unreadEl) unreadEl.textContent = unreadNotifications;

    const activeAlerts = latestReading ? getAlertData(latestReading) : [];
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
                    <svg class="ui-icon"><use href="${item.severity === "Critical" ? "#icon-alert" : "#icon-bell"}"></use></svg> ${item.title}
                    <br>
                    ${item.message}
                    <br><br>
                    <strong>Notification:</strong> ${item.notification}
                </div>
            `).join("");
        }
    }

    const statusContainer = document.getElementById("notification-status");
    if (statusContainer) {
        statusContainer.className = "notification-status-panel";
        statusContainer.innerHTML = `
            <div class="notification-status-header">
                <h3>Notification Status</h3>
                <button type="button" class="notification-status-action">View History</button>
            </div>

            <div class="notification-status-subtitle">SMS Notification (SIM800L)</div>

            <div class="notification-status-row">
                <div class="notification-status-main">
                    <div class="notification-status-icon success"><svg class="ui-icon"><use href="#icon-check"></use></svg></div>
                    <div class="notification-status-copy">
                        <div class="notification-status-value">0</div>
                        <div class="notification-status-label">Sent</div>
                    </div>
                </div>
                <div class="notification-status-date">Today</div>
            </div>

            <div class="notification-status-row">
                <div class="notification-status-main">
                    <div class="notification-status-icon success"><svg class="ui-icon"><use href="#icon-check"></use></svg></div>
                    <div class="notification-status-copy">
                        <div class="notification-status-value">0</div>
                        <div class="notification-status-label">Delivered</div>
                    </div>
                </div>
                <div class="notification-status-date">Today</div>
            </div>

            <div class="notification-status-row">
                <div class="notification-status-main">
                    <div class="notification-status-icon danger"><svg class="ui-icon"><use href="#icon-x"></use></svg></div>
                    <div class="notification-status-copy">
                        <div class="notification-status-value">0</div>
                        <div class="notification-status-label">Failed</div>
                    </div>
                </div>
                <div class="notification-status-date">Today</div>
            </div>
        `;
    }
}

function renderRecentNotifications(history) {
    const container = document.getElementById("recent-notifications");
    if (!container) return;

    const allAlerts = history
        .flatMap((reading) => getAlertData(reading).map((alert) => ({ ...alert, recorded_at: reading.recorded_at })))
        .sort((a, b) => new Date(b.recorded_at) - new Date(a.recorded_at))
        .slice(0, 5);

    if (allAlerts.length === 0) {
        container.innerHTML = `
            <div class="status-box">
                No notifications available yet.
            </div>
        `;
        return;
    }

    container.innerHTML = allAlerts.map((item) => `
        <div class="alert">
            <strong>${item.title}</strong>
            <br>
            ${item.message}
            <br>
            <small>${formatDateTime(item.recorded_at)}</small>
        </div>
    `).join("");
}

function filterAlertHistory(history) {
    if (!Array.isArray(history)) return [];

    return history.filter((reading) => {
        const alerts = getAlertData(reading);
        const readingDateObj = new Date(reading.recorded_at);

        // 1. Timeframe filter (Today)
        if (currentFilter.todayOnly && !currentFilter.customDate) {
            const today = new Date();
            const isSameDay =
                readingDateObj.getFullYear() === today.getFullYear() &&
                readingDateObj.getMonth() === today.getMonth() &&
                readingDateObj.getDate() === today.getDate();
            if (!isSameDay) return false;
        }

        // 2. Custom Date filter (YYYY-MM-DD)
        if (currentFilter.customDate) {
            const localReadingDate = `${readingDateObj.getFullYear()}-${String(readingDateObj.getMonth() + 1).padStart(2, "0")}-${String(readingDateObj.getDate()).padStart(2, "0")}`;
            if (localReadingDate !== currentFilter.customDate) return false;
        }

        // 3. Type filter
        if (currentFilter.type === "critical") {
            if (!alerts.some((a) => a.severity === "Critical")) return false;
        } else if (currentFilter.type === "warning") {
            if (!alerts.some((a) => a.severity === "Warning")) return false;
        } else if (currentFilter.type === "temperature") {
            if (!alerts.some((a) => a.type === "temperature")) return false;
        } else if (currentFilter.type === "ph") {
            if (!alerts.some((a) => a.type === "ph")) return false;
        } else if (currentFilter.type === "resolved") {
            if (alerts.length > 0) return false;
        }

        // 4. Status filter
        if (currentFilter.status === "Active" && alerts.length === 0) return false;
        if (currentFilter.status === "Resolved" && alerts.length > 0) return false;

        // 5. Search keyword
        if (currentFilter.search) {
            const query = currentFilter.search.toLowerCase();
            const dateStr = readingDateObj.toLocaleDateString().toLowerCase();
            const timeStr = readingDateObj.toLocaleTimeString().toLowerCase();
            const titlesStr = alerts.map((a) => a.title).join(" ").toLowerCase();
            const statusStr = (alerts.length ? "active" : "resolved").toLowerCase();
            const textMatch =
                dateStr.includes(query) ||
                timeStr.includes(query) ||
                titlesStr.includes(query) ||
                statusStr.includes(query);
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
        let msg = "No alert history available.";
        if (currentFilter.todayOnly && !currentFilter.customDate) {
            msg = "No alerts recorded today.";
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

    tableBody.innerHTML = filtered.slice().reverse().map((reading) => {
        const alerts = getAlertData(reading);
        const highestSeverity = alerts.length ? alerts.reduce((max, alert) => {
            const priority = { Critical: 2, Warning: 1 };
            return priority[alert.severity] > priority[max] ? alert.severity : max;
        }, "Warning") : "Normal";

        const severityBadge = highestSeverity === "Critical"
            ? '<span class="severity-badge severity-critical">Critical</span>'
            : highestSeverity === "Warning"
            ? '<span class="severity-badge severity-warning">Warning</span>'
            : '<span class="severity-badge severity-none">Normal</span>';

        const statusPill = alerts.length
            ? '<span class="status-pill status-active">Active</span>'
            : '<span class="status-pill status-resolved">Resolved</span>';

        const alertDetails = alerts.length
            ? alerts.map((alert) => alert.title).join(", ")
            : "No issues detected";

        return `
            <tr>
                <td>${new Date(reading.recorded_at).toLocaleDateString()}</td>
                <td>${new Date(reading.recorded_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</td>
                <td><strong>${alerts.length}</strong></td>
                <td>${severityBadge}</td>
                <td>${statusPill}</td>
                <td>${alertDetails}</td>
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
        searchInput.addEventListener("input", (e) => {
            currentFilter.search = e.target.value;
            updateActiveFilterBadge();
            renderAlertHistory(cachedHistory);
        });
    }

    if (resetButton) {
        resetButton.addEventListener("click", () => {
            currentFilter = {
                type: "all",
                todayOnly: true,
                customDate: "",
                status: "all",
                search: ""
            };
            if (typeSelect) typeSelect.value = "all";
            if (todayButton) {
                todayButton.classList.add("active");
                todayButton.setAttribute("aria-pressed", "true");
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
        const [latestResponse, historyResponse] = await Promise.all([
            fetch("/api/readings/latest"),
            fetch("/api/readings/history")
        ]);

        if (!latestResponse.ok || !historyResponse.ok) {
            throw new Error(`Sensor API returned ${latestResponse.status} / ${historyResponse.status}.`);
        }
        const reading = await latestResponse.json();
        const history = await historyResponse.json();
        if (!Array.isArray(history)) {
            throw new Error("Sensor history response has an invalid format.");
        }

        cachedHistory = history;
        initAlertHistoryControls();
        updateSummaryCards(history, reading);
        renderRecentNotifications(history);
        renderAlertHistory(history);
        document.getElementById("critical-alerts-count").textContent = history.flatMap((item) => getAlertData(item)).filter((alert) => alert.severity === "Critical").length;
        document.getElementById("warning-alerts-count").textContent = history.flatMap((item) => getAlertData(item)).filter((alert) => alert.severity === "Warning").length;
    } catch (error) {
        console.error("Unable to load sensor data for alerts:", error);
        const activeContainer = document.getElementById("active-alerts");
        const recentContainer = document.getElementById("recent-notifications");
        const historyBody = document.getElementById("alert-history-body");
        const statusContainer = document.getElementById("notification-status");

        if (activeContainer) activeContainer.innerHTML = '<div class="status-box">Unable to load sensor data. Please refresh or retry.</div>';
        if (recentContainer) recentContainer.innerHTML = '<div class="status-box">Unable to load sensor data. Please refresh or retry.</div>';
        if (historyBody) historyBody.innerHTML = '<tr><td colspan="6" class="table-empty" style="text-align: center; padding: 24px; color: #8a998f;">Unable to load sensor data.</td></tr>';
        if (statusContainer) statusContainer.innerHTML = '<div class="status-box">Sensor database unavailable.</div>';
    }
}

updateDeviceTime();
setInterval(updateDeviceTime, 1000);
loadAlertsData();
setInterval(loadAlertsData, 10000);
