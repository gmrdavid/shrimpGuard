let cachedAlertsData = null;
let cachedHistory = [];
let cachedRecentNotifications = [];
let recentCurrentPage = 1;
const recentPerPage = 3;

let historyPage = 1;
let alertsPerPage = "10";
let tableFilterDate = null; // null or 'YYYY-MM-DD'
let tableFilterStatus = "all"; // 'all', 'optimal', 'warning', 'critical'
let calYear = new Date().getFullYear();
let calMonth = new Date().getMonth();
let calInitialized = false;
let alertControlsInitialized = false;

const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
];

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

function localDate(reading) {
    if (!reading || !reading.recorded_at) return "";
    const date = new Date(reading.recorded_at);
    if (isNaN(date.getTime())) return "";
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function getDatesWithReadingsSet() {
    const set = new Set();
    cachedHistory.forEach((r) => {
        const d = localDate(r);
        if (d) set.add(d);
    });
    return set;
}

function statusForAlert(item) {
    if (!item) return "Optimal";
    const sev = String(item.severity || "").trim().toLowerCase();
    const ml = String(item.ml_status || "").trim().toLowerCase();
    if (sev === "critical" || ml === "critical") return "Critical";
    if (sev === "warning" || ml === "warning") return "Warning";
    return "Optimal";
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
    cachedRecentNotifications = Array.isArray(notifications) ? notifications : [];
    const container = document.getElementById("recent-notifications");
    const paginationEl = document.getElementById("recent-notifications-pagination");
    const pageInfo = document.getElementById("recent-page-info");
    const prevBtn = document.getElementById("recent-prev-btn");
    const nextBtn = document.getElementById("recent-next-btn");

    if (!container) return;

    if (!cachedRecentNotifications.length) {
        container.innerHTML = `
            <div class="status-box">
                No recent notifications recorded. All parameters are optimal.
            </div>
        `;
        if (paginationEl) paginationEl.hidden = true;
        return;
    }

    if (paginationEl) paginationEl.hidden = false;

    const totalPages = Math.max(1, Math.ceil(cachedRecentNotifications.length / recentPerPage));
    if (recentCurrentPage > totalPages) recentCurrentPage = totalPages;
    if (recentCurrentPage < 1) recentCurrentPage = 1;

    const startIdx = (recentCurrentPage - 1) * recentPerPage;
    const endIdx = Math.min(startIdx + recentPerPage, cachedRecentNotifications.length);
    const pageItems = cachedRecentNotifications.slice(startIdx, endIdx);

    if (pageInfo) {
        pageInfo.textContent = `Showing ${startIdx + 1}–${endIdx} of ${cachedRecentNotifications.length}`;
    }
    if (prevBtn) prevBtn.disabled = (recentCurrentPage <= 1);
    if (nextBtn) nextBtn.disabled = (recentCurrentPage >= totalPages);

    container.innerHTML = pageItems.map((item) => {
        const sev = (item.severity || "optimal").toLowerCase();
        const iconHref = sev === "critical" ? "#icon-alert" : sev === "warning" ? "#icon-bell" : "#icon-check-circle";
        const isUnread = !item.is_read;
        return `
            <div class="alert" style="${isUnread ? 'border-left: 3px solid #16a34a; background: #fafdfb;' : 'border-left: 3px solid #d1d5db; opacity: 0.9;'}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="display: flex; align-items: center; gap: 6px;">
                        <svg class="ui-icon"><use href="${iconHref}"></use></svg>
                        <strong>${item.title}</strong>
                    </span>
                    ${isUnread ? '<span style="background: #e8f5e9; color: #16a34a; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px;">NEW</span>' : ''}
                </div>
                <div>${item.message}</div>
                <small style="color: #6d8477; display: block; margin-top: 4px;">${formatDateTime(item.recorded_at)}</small>
            </div>
        `;
    }).join("");
}

// =========================================
// CALENDAR & DATE FILTER LOGIC
// =========================================

function renderCalendar() {
    const titleEl = document.getElementById("cal-month-title");
    const gridEl = document.getElementById("calendar-days-grid");
    if (!titleEl || !gridEl) return;

    titleEl.textContent = `${monthNames[calMonth]} ${calYear}`;
    gridEl.innerHTML = "";

    const datesWithReadings = getDatesWithReadingsSet();

    const firstDayIndex = new Date(calYear, calMonth, 1).getDay();
    const totalDays = new Date(calYear, calMonth + 1, 0).getDate();
    const prevMonthDays = new Date(calYear, calMonth, 0).getDate();

    for (let i = firstDayIndex - 1; i >= 0; i--) {
        const filler = document.createElement("div");
        filler.className = "cal-day cal-day-empty";
        filler.textContent = String(prevMonthDays - i);
        gridEl.appendChild(filler);
    }

    for (let day = 1; day <= totalDays; day++) {
        const dayStr = `${calYear}-${String(calMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
        const hasData = datesWithReadings.has(dayStr);
        const isSelected = tableFilterDate === dayStr;

        const dayBtn = document.createElement("button");
        dayBtn.type = "button";
        dayBtn.className = `cal-day-btn ${hasData ? "has-data" : "no-data"}${isSelected ? " selected" : ""}`;
        dayBtn.setAttribute("data-date", dayStr);
        dayBtn.setAttribute("title", `${dayStr}: ${hasData ? "Readings available" : "No readings"}`);

        const dayNum = document.createElement("span");
        dayNum.className = "cal-day-num";
        dayNum.textContent = String(day);

        const dot = document.createElement("span");
        dot.className = `cal-dot ${hasData ? "cal-dot-green" : "cal-dot-red"}`;

        dayBtn.appendChild(dayNum);
        dayBtn.appendChild(dot);

        dayBtn.addEventListener("click", () => {
            selectDateFilter(dayStr);
        });

        gridEl.appendChild(dayBtn);
    }
}

function selectDateFilter(dateStr) {
    if (tableFilterDate === dateStr) {
        tableFilterDate = null;
    } else {
        tableFilterDate = dateStr;
    }
    updateDateFilterUI();
    closeCalendarPopup();
    historyPage = 1;
    renderAlertHistory(cachedHistory);
}

function clearDateFilter() {
    tableFilterDate = null;
    updateDateFilterUI();
    closeCalendarPopup();
    historyPage = 1;
    renderAlertHistory(cachedHistory);
}

function updateDateFilterUI() {
    const textEl = document.getElementById("filter-date-text");
    const clearBtn = document.getElementById("cal-clear-btn");
    if (!textEl) return;

    if (!tableFilterDate) {
        textEl.textContent = "Filter Date: All";
        if (clearBtn) clearBtn.classList.remove("active");
    } else {
        const parts = tableFilterDate.split("-");
        const y = parseInt(parts[0], 10);
        const m = parseInt(parts[1], 10) - 1;
        const d = parseInt(parts[2], 10);
        const dateObj = new Date(y, m, d);
        const formatted = isNaN(dateObj.getTime())
            ? tableFilterDate
            : dateObj.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
        textEl.textContent = `Date: ${formatted}`;
        if (clearBtn) clearBtn.classList.add("active");
    }
    renderCalendar();
}

function prevMonth() {
    calMonth--;
    if (calMonth < 0) {
        calMonth = 11;
        calYear--;
    }
    renderCalendar();
}

function nextMonth() {
    calMonth++;
    if (calMonth > 11) {
        calMonth = 0;
        calYear++;
    }
    renderCalendar();
}

function openCalendarPopup() {
    const popup = document.getElementById("calendar-popup");
    const btn = document.getElementById("filter-date-btn");
    if (!popup) return;
    closeStatusDropdown();
    popup.hidden = false;
    popup.style.display = "block";
    if (btn) btn.setAttribute("aria-expanded", "true");
    renderCalendar();
}

function closeCalendarPopup() {
    const popup = document.getElementById("calendar-popup");
    const btn = document.getElementById("filter-date-btn");
    if (!popup) return;
    popup.hidden = true;
    popup.style.display = "none";
    if (btn) btn.setAttribute("aria-expanded", "false");
}

function toggleCalendarPopup() {
    const popup = document.getElementById("calendar-popup");
    if (popup && (!popup.hidden && popup.style.display !== "none")) {
        closeCalendarPopup();
    } else {
        openCalendarPopup();
    }
}

// =========================================
// STATUS DROPDOWN FILTER LOGIC
// =========================================

function selectStatusFilter(status) {
    tableFilterStatus = String(status).toLowerCase();
    const textEl = document.getElementById("filter-status-text");
    if (textEl) {
        const labels = {
            all: "Status: All",
            optimal: "Status: Optimal",
            warning: "Status: Warning",
            critical: "Status: Critical",
        };
        textEl.textContent = labels[tableFilterStatus] || "Status: All";
    }

    const items = document.querySelectorAll(".status-menu-item");
    items.forEach((btn) => {
        if (btn.getAttribute("data-status") === tableFilterStatus) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    closeStatusDropdown();
    historyPage = 1;
    renderAlertHistory(cachedHistory);
}

function openStatusDropdown() {
    const menu = document.getElementById("status-dropdown-menu");
    const btn = document.getElementById("filter-status-btn");
    if (!menu) return;
    closeCalendarPopup();
    menu.hidden = false;
    menu.style.display = "flex";
    if (btn) btn.setAttribute("aria-expanded", "true");
}

function closeStatusDropdown() {
    const menu = document.getElementById("status-dropdown-menu");
    const btn = document.getElementById("filter-status-btn");
    if (!menu) return;
    menu.hidden = true;
    menu.style.display = "none";
    if (btn) btn.setAttribute("aria-expanded", "false");
}

function toggleStatusDropdown() {
    const menu = document.getElementById("status-dropdown-menu");
    if (menu && (!menu.hidden && menu.style.display !== "none")) {
        closeStatusDropdown();
    } else {
        openStatusDropdown();
    }
}

// =========================================
// ALERT HISTORY TABLE & PAGINATION
// =========================================

function renderAlertHistory(history) {
    const tableBody = document.getElementById("alert-history-body");
    const pagination = document.getElementById("alert-history-pagination");
    const pageInfoEl = document.getElementById("table-page-info");
    if (!tableBody) return;

    let filteredItems = Array.isArray(history) ? history.slice() : [];

    // Table-level date filter
    if (tableFilterDate) {
        filteredItems = filteredItems.filter((r) => localDate(r) === tableFilterDate);
    }

    // Table-level status filter
    if (tableFilterStatus && tableFilterStatus !== "all") {
        filteredItems = filteredItems.filter((r) => statusForAlert(r).toLowerCase() === tableFilterStatus);
    }

    // Sort by recorded_at descending (newest first)
    filteredItems.sort((a, b) => new Date(b.recorded_at).getTime() - new Date(a.recorded_at).getTime());

    // Limit and Pagination calculation
    const total = filteredItems.length;
    const limit = alertsPerPage === "all" ? Math.max(total, 1) : parseInt(alertsPerPage, 10);
    const pageCount = Math.ceil(total / limit) || 1;
    historyPage = Math.min(historyPage, Math.max(pageCount, 1));
    const startIndex = (historyPage - 1) * limit;
    const endIndex = Math.min(startIndex + limit, total);
    const pagedItems = filteredItems.slice(startIndex, endIndex);

    // Update table page info text (matching historical format)
    if (pageInfoEl) {
        if (total === 0) {
            pageInfoEl.textContent = "Showing 0 readings";
        } else if (alertsPerPage === "all") {
            pageInfoEl.textContent = `Showing all ${total} reading${total === 1 ? "" : "s"}`;
        } else {
            pageInfoEl.textContent = `Showing ${startIndex + 1}–${endIndex} of ${total} reading${total === 1 ? "" : "s"}`;
        }
    }

    // Update Toolbar indicators
    const filterDateText = document.getElementById("filter-date-text");
    if (filterDateText) {
        if (!tableFilterDate) {
            filterDateText.textContent = "Filter Date: All";
        } else {
            const parts = tableFilterDate.split("-");
            const y = parseInt(parts[0], 10);
            const m = parseInt(parts[1], 10) - 1;
            const d = parseInt(parts[2], 10);
            const dateObj = new Date(y, m, d);
            const formatted = isNaN(dateObj.getTime())
                ? tableFilterDate
                : dateObj.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
            filterDateText.textContent = `Date: ${formatted}`;
        }
    }

    const filterStatusText = document.getElementById("filter-status-text");
    if (filterStatusText) {
        const labels = {
            all: "Status: All",
            optimal: "Status: Optimal",
            warning: "Status: Warning",
            critical: "Status: Critical",
        };
        filterStatusText.textContent = labels[tableFilterStatus] || "Status: All";
    }

    if (total === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="table-empty" style="text-align: center; padding: 28px 14px; color: #8a998f;">
                    No saved alert records match these filters.
                </td>
            </tr>
        `;
    } else {
        tableBody.innerHTML = pagedItems.map((item) => {
            const d = new Date(item.recorded_at);
            const dateStr = !isNaN(d.getTime()) ? d.toLocaleDateString() : item.recorded_at;
            const timeStr = !isNaN(d.getTime()) ? d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "-";

            const overall = statusForAlert(item);
            const severityBadge = overall === "Critical"
                ? '<span class="severity-badge severity-critical">Critical</span>'
                : overall === "Warning"
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
                    <td>${item.details || "-"}</td>
                </tr>
            `;
        }).join("");
    }

    // Render Pagination controls (exact match with historical.js)
    if (pagination) {
        pagination.replaceChildren();
        pagination.hidden = pageCount <= 1;
        if (pageCount <= 1) return;

        const addPageButton = (label, page, options = {}) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "readings-page-button";
            button.textContent = label;
            if (options.label) button.setAttribute("aria-label", options.label);
            if (options.current) button.setAttribute("aria-current", "page");
            if (options.disabled) button.disabled = true;
            button.addEventListener("click", () => {
                historyPage = page;
                renderAlertHistory(history);
            });
            pagination.appendChild(button);
        };

        addPageButton("‹", historyPage - 1, {
            label: "Previous page",
            disabled: historyPage === 1
        });

        let visiblePages;
        if (pageCount <= 7) {
            visiblePages = Array.from({ length: pageCount }, (_, index) => index + 1);
        } else if (historyPage <= 4) {
            visiblePages = [1, 2, 3, 4, 5, "…", pageCount];
        } else if (historyPage >= pageCount - 3) {
            visiblePages = [1, "…", pageCount - 4, pageCount - 3, pageCount - 2, pageCount - 1, pageCount];
        } else {
            visiblePages = [1, "…", historyPage - 1, historyPage, historyPage + 1, "…", pageCount];
        }

        visiblePages.forEach((page) => {
            if (typeof page !== "number") {
                const ellipsis = document.createElement("span");
                ellipsis.className = "readings-page-ellipsis";
                ellipsis.textContent = page;
                ellipsis.setAttribute("aria-hidden", "true");
                pagination.appendChild(ellipsis);
                return;
            }
            addPageButton(String(page), page, { current: page === historyPage });
        });

        addPageButton("›", historyPage + 1, {
            label: "Next page",
            disabled: historyPage === pageCount
        });
    }
}

function initAlertHistoryControls() {
    if (alertControlsInitialized) return;

    // Limit selector
    const tableLimitSelect = document.getElementById("table-limit-select");
    if (tableLimitSelect) {
        tableLimitSelect.addEventListener("change", (e) => {
            alertsPerPage = e.target.value;
            historyPage = 1;
            renderAlertHistory(cachedHistory);
        });
    }

    // Filter date button & Calendar nav
    const filterDateBtn = document.getElementById("filter-date-btn");
    if (filterDateBtn) {
        filterDateBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            toggleCalendarPopup();
        });
    }

    const calPrevBtn = document.getElementById("cal-prev-month");
    if (calPrevBtn) {
        calPrevBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            prevMonth();
        });
    }

    const calNextBtn = document.getElementById("cal-next-month");
    if (calNextBtn) {
        calNextBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            nextMonth();
        });
    }

    const calClearBtn = document.getElementById("cal-clear-btn");
    if (calClearBtn) {
        calClearBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            clearDateFilter();
        });
    }

    // Status Filter button & Dropdown
    const filterStatusBtn = document.getElementById("filter-status-btn");
    if (filterStatusBtn) {
        filterStatusBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            toggleStatusDropdown();
        });
    }

    const statusMenuItems = document.querySelectorAll(".status-menu-item");
    statusMenuItems.forEach((btn) => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const status = btn.getAttribute("data-status");
            selectStatusFilter(status);
        });
    });

    // Close popup/dropdown when clicking outside
    document.addEventListener("click", (e) => {
        const calAnchor = document.querySelector(".calendar-picker-anchor");
        if (calAnchor && !calAnchor.contains(e.target)) {
            closeCalendarPopup();
        }
        const statusAnchor = document.querySelector(".status-picker-anchor");
        if (statusAnchor && !statusAnchor.contains(e.target)) {
            closeStatusDropdown();
        }
    });

    // Close on Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeCalendarPopup();
            closeStatusDropdown();
        }
    });

    // Recent Notifications Pagination controls
    const recentPrevBtn = document.getElementById("recent-prev-btn");
    const recentNextBtn = document.getElementById("recent-next-btn");

    if (recentPrevBtn) {
        recentPrevBtn.addEventListener("click", () => {
            if (recentCurrentPage > 1) {
                recentCurrentPage--;
                renderRecentNotifications(cachedRecentNotifications);
            }
        });
    }
    if (recentNextBtn) {
        recentNextBtn.addEventListener("click", () => {
            recentCurrentPage++;
            renderRecentNotifications(cachedRecentNotifications);
        });
    }

    // Mark all as read button
    const markReadBtn = document.getElementById("mark-all-read-btn");
    if (markReadBtn) {
        markReadBtn.addEventListener("click", async () => {
            try {
                const res = await fetch("/api/alerts/mark-read", { method: "POST" });
                if (res.ok) {
                    const unreadEl = document.getElementById("unread-notifications-count");
                    if (unreadEl) unreadEl.textContent = "0";
                    if (cachedAlertsData && cachedAlertsData.summary) {
                        cachedAlertsData.summary.unread_notifications = 0;
                    }
                    if (Array.isArray(cachedRecentNotifications)) {
                        cachedRecentNotifications.forEach(n => n.is_read = true);
                        renderRecentNotifications(cachedRecentNotifications);
                    }
                    window.dispatchEvent(new Event("shrimpguard:notification-update"));
                }
            } catch (err) {
                console.error("Failed to mark all as read:", err);
            }
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

        if (!calInitialized && cachedHistory.length > 0) {
            const latestDate = new Date(cachedHistory[0].recorded_at);
            if (!isNaN(latestDate.getTime())) {
                calYear = latestDate.getFullYear();
                calMonth = latestDate.getMonth();
                calInitialized = true;
            }
        }

        initAlertHistoryControls();
        updateSummaryCards(data);
        renderRecentNotifications(data.recent_notifications || []);
        renderCalendar();
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

closeCalendarPopup();
closeStatusDropdown();
updateDeviceTime();
setInterval(updateDeviceTime, 1000);
loadAlertsData();
setInterval(loadAlertsData, 10000);
