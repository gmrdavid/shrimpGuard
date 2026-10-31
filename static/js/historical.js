let sensorHistory = [];
let historyPage = 1;
let readingsPerPage = "10";
let tableFilterDate = null; // null or 'YYYY-MM-DD'
let tableFilterStatus = "all"; // 'all', 'optimal', 'warning', 'critical'
let calYear = new Date().getFullYear();
let calMonth = new Date().getMonth();
let calInitialized = false;
const parameterLabels = {
    temperature: "Temperature",
    ph: "pH Level"
};
const units = { temperature: "°C", ph: "pH" };
const colors = { temperature: "#2f6fbd", ph: "#2f8a57" };

let currentFilteredHistory = [];
let currentFilteredParameters = [];
let currentHistoricalPoints = {};
let historicalHoverIndex = null;
let historicalHoveredParam = null;
let historicalChartEventsInitialized = false;

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

function statusFor(reading) {
    if (!reading || !reading.status) return "Optimal";
    const status = String(reading.status).trim();
    if (status.toLowerCase().includes("critical")) return "Critical";
    if (status.toLowerCase().includes("warning")) return "Warning";
    if (status.toLowerCase().includes("optimal") || status.toLowerCase().includes("normal") || status.toLowerCase().includes("good")) return "Optimal";
    return status;
}

function getTemperatureStatus(temperature) {
    const temp = Number(temperature);
    // ML model ranges: <= 25 or > 32 is Critical; 25 < temp < 28 is Warning; 28 <= temp <= 32 is Optimal
    if (temp <= 25.0 || temp > 32.0) {
        return { label: "Critical", level: "critical", badgeClass: "status-critical" };
    }
    if (temp < 28.0) {
        return { label: "Warning", level: "warning", badgeClass: "status-warning" };
    }
    return { label: "Optimal", level: "optimal", badgeClass: "status-optimal" };
}

function getPhStatus(phLevel) {
    const ph = Number(phLevel);
    // ML model ranges: <= 6.49 or > 9.0 is Critical; 6.50-7.49 or 8.51-9.0 is Warning; 7.50-8.50 is Optimal
    if (ph <= 6.49 || ph > 9.0) {
        return { label: "Critical", level: "critical", badgeClass: "status-critical" };
    }
    if (ph < 7.5 || ph > 8.5) {
        return { label: "Warning", level: "warning", badgeClass: "status-warning" };
    }
    return { label: "Optimal", level: "optimal", badgeClass: "status-optimal" };
}

function localDate(reading) {
    const date = new Date(reading.recorded_at);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function filterHistory(history) {
    const selectedDate = document.getElementById("history-date").value;
    const interval = document.getElementById("history-interval").value;
    const now = Date.now();
    return history.filter((reading) => {
        const recorded = new Date(reading.recorded_at).getTime();
        const dateMatches = !selectedDate || localDate(reading) === selectedDate;
        const intervalMatches = interval === "all" || now - recorded <= Number(interval) * 60 * 60 * 1000;
        return dateMatches && intervalMatches;
    });
}

function selectedParameters() {
    const selected = document.getElementById("history-parameter").value;
    return selected === "all" ? Object.keys(parameterLabels) : [selected];
}

function drawChart(history, parameters) {
    if (!Array.isArray(history) || history.length === 0) return;
    currentFilteredHistory = history;
    currentFilteredParameters = parameters;

    const canvas = document.getElementById("historical-chart");
    if (!canvas) return;
    const context = canvas.getContext("2d");
    const width = canvas.clientWidth || 600;
    const height = canvas.clientHeight || 300;
    const scale = window.devicePixelRatio || 1;

    const allValues = parameters.flatMap((key) => history.map((reading) => Number(reading[key])));
    const minimum = Math.min(...allValues);
    const maximum = Math.max(...allValues);
    const range = maximum - minimum || 1;
    const padding = { top: 26, right: 30, bottom: 32, left: 44 };

    canvas.width = Math.round(width * scale);
    canvas.height = Math.round(height * scale);
    context.scale(scale, scale);
    context.clearRect(0, 0, width, height);

    // Horizontal grid lines and Y-axis scale
    context.strokeStyle = "#e8edea";
    context.fillStyle = "#8a978f";
    context.font = "600 11px Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
    context.lineWidth = 1;

    const gridSteps = 4;
    for (let index = 0; index < gridSteps; index += 1) {
        const y = padding.top + ((height - padding.top - padding.bottom) / (gridSteps - 1)) * index;
        context.beginPath();
        context.moveTo(padding.left, y);
        context.lineTo(width - padding.right, y);
        context.stroke();
        const labelVal = (maximum - (range / (gridSteps - 1)) * index).toFixed(1);
        context.fillText(labelVal, 6, y + 4);
    }

    // Compute coordinate points per parameter
    currentHistoricalPoints = {};
    parameters.forEach((key) => {
        currentHistoricalPoints[key] = history.map((reading, index) => {
            const val = Number(reading[key]);
            const x = history.length === 1
                ? padding.left + (width - padding.left - padding.right) / 2
                : padding.left + (index / (history.length - 1)) * (width - padding.left - padding.right);
            const y = padding.top + (1 - (val - minimum) / range) * (height - padding.top - padding.bottom);
            return { x, y, value: val, key, reading, index };
        });
    });

    // Vertical dashed guide line when hovering
    if (historicalHoverIndex !== null && historicalHoverIndex >= 0 && historicalHoverIndex < history.length) {
        const firstKey = parameters[0];
        if (currentHistoricalPoints[firstKey] && currentHistoricalPoints[firstKey][historicalHoverIndex]) {
            const hoverX = currentHistoricalPoints[firstKey][historicalHoverIndex].x;
            context.save();
            context.beginPath();
            context.setLineDash([4, 4]);
            context.strokeStyle = "rgba(18, 107, 79, 0.45)";
            context.lineWidth = 1.5;
            context.moveTo(hoverX, padding.top - 6);
            context.lineTo(hoverX, height - padding.bottom + 6);
            context.stroke();
            context.restore();
        }
    }

    // Draw lines and points for each selected parameter
    parameters.forEach((key) => {
        const pts = currentHistoricalPoints[key];
        if (!pts || !pts.length) return;

        // Line
        context.beginPath();
        pts.forEach((pt, index) => {
            if (index === 0) context.moveTo(pt.x, pt.y);
            else context.lineTo(pt.x, pt.y);
        });
        context.strokeStyle = colors[key];
        context.lineWidth = 2.5;
        context.lineCap = "round";
        context.lineJoin = "round";
        context.stroke();

        // Points
        pts.forEach((pt, index) => {
            const isHovered = historicalHoverIndex === index;
            const isFocused = isHovered && (historicalHoveredParam === key || historicalHoveredParam === null);

            // Halo glow for hovered point
            if (isHovered) {
                context.beginPath();
                context.arc(pt.x, pt.y, isFocused ? 11 : 7, 0, Math.PI * 2);
                context.fillStyle = key === "temperature"
                    ? "rgba(47, 111, 189, 0.22)"
                    : "rgba(47, 138, 87, 0.22)";
                context.fill();
            }

            // Outer point ring & dot
            context.beginPath();
            context.arc(pt.x, pt.y, isHovered ? (isFocused ? 5.5 : 4.5) : 3.5, 0, Math.PI * 2);
            context.fillStyle = isHovered ? "#ffffff" : colors[key];
            context.fill();
            context.strokeStyle = colors[key];
            context.lineWidth = isHovered ? 2.5 : 1.5;
            context.stroke();
        });
    });
}

function renderHistoricalTooltip(reading, index, pointX, mouseY, focusedParam, containerWidth, containerHeight) {
    let tooltip = document.getElementById("historical-chart-tooltip");
    if (!tooltip) {
        const wrap = document.querySelector(".historical-chart-wrap");
        if (!wrap) return;
        tooltip = document.createElement("div");
        tooltip.id = "historical-chart-tooltip";
        tooltip.className = "historical-chart-tooltip";
        wrap.appendChild(tooltip);
    }

    const tempVal = Number(reading.temperature);
    const phVal = Number(reading.ph);
    const tempStatus = getTemperatureStatus(tempVal);
    const phStatus = getPhStatus(phVal);
    const overallStatus = statusFor(reading);
    const statusLower = overallStatus.toLowerCase();
    const pillClass = statusLower.includes("critical")
        ? "pill-critical"
        : statusLower.includes("warning")
        ? "pill-warning"
        : "pill-optimal";
    const statusLabel = statusLower.includes("critical")
        ? "Critical"
        : statusLower.includes("warning")
        ? "Warning"
        : "Optimal";

    const dateObj = reading.recorded_at ? new Date(reading.recorded_at) : null;
    const timeDisplay = dateObj && !isNaN(dateObj)
        ? dateObj.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
        : `Reading #${index + 1}`;
    const dateDisplay = dateObj && !isNaN(dateObj)
        ? dateObj.toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" })
        : "";

    const showTemp = currentFilteredParameters.length === 0 || currentFilteredParameters.includes("temperature");
    const showPh = currentFilteredParameters.length === 0 || currentFilteredParameters.includes("ph");

    let itemsHtml = "";
    if (showTemp) {
        itemsHtml += `
            <div class="tooltip-item ${focusedParam === 'temperature' ? 'tooltip-item-focused' : ''}">
                <div class="tooltip-item-left">
                    <span class="tooltip-dot" style="background:#2f6fbd;"></span>
                    <span class="tooltip-param-label">Temperature:</span>
                </div>
                <div class="tooltip-item-right">
                    <span class="tooltip-param-value">${tempVal.toFixed(1)} °C</span>
                    <span class="tooltip-param-status ${tempStatus.badgeClass}">${tempStatus.label}</span>
                </div>
            </div>
        `;
    }
    if (showPh) {
        itemsHtml += `
            <div class="tooltip-item ${focusedParam === 'ph' ? 'tooltip-item-focused' : ''}">
                <div class="tooltip-item-left">
                    <span class="tooltip-dot" style="background:#2f8a57;"></span>
                    <span class="tooltip-param-label">pH Level:</span>
                </div>
                <div class="tooltip-item-right">
                    <span class="tooltip-param-value">${phVal.toFixed(2)}</span>
                    <span class="tooltip-param-status ${phStatus.badgeClass}">${phStatus.label}</span>
                </div>
            </div>
        `;
    }

    tooltip.innerHTML = `
        <div class="tooltip-header">
            <span class="tooltip-time-badge">${dateDisplay ? dateDisplay + ' • ' : ''}${timeDisplay}</span>
            <span class="tooltip-status-pill ${pillClass}">
                ${statusLabel}
            </span>
        </div>
        <div class="tooltip-content">
            ${itemsHtml}
        </div>
    `;

    tooltip.hidden = false;
    tooltip.classList.add("visible");

    const tooltipWidth = tooltip.offsetWidth || 250;
    const tooltipHeight = tooltip.offsetHeight || 110;

    let leftPos = pointX + 16;
    if (leftPos + tooltipWidth > containerWidth - 12) {
        leftPos = pointX - tooltipWidth - 16;
    }
    if (leftPos < 12) leftPos = 12;

    let topPos = mouseY - (tooltipHeight / 2);
    topPos = Math.max(10, Math.min(containerHeight - tooltipHeight - 10, topPos));

    tooltip.style.left = `${leftPos}px`;
    tooltip.style.top = `${topPos}px`;
}

function handleHistoricalPointerMove(event) {
    if (!currentFilteredHistory || currentFilteredHistory.length === 0 || !currentHistoricalPoints) return;
    const canvas = document.getElementById("historical-chart");
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const padding = { top: 26, right: 30, bottom: 32, left: 42 };

    if (
        mouseX < padding.left - 15 ||
        mouseX > width - padding.right + 15 ||
        mouseY < padding.top - 15 ||
        mouseY > height - padding.bottom + 15
    ) {
        handleHistoricalPointerLeave();
        return;
    }

    let nearestIndex = 0;
    if (currentFilteredHistory.length > 1) {
        const plotWidth = width - padding.left - padding.right;
        const ratio = (mouseX - padding.left) / plotWidth;
        nearestIndex = Math.round(ratio * (currentFilteredHistory.length - 1));
        nearestIndex = Math.max(0, Math.min(currentFilteredHistory.length - 1, nearestIndex));
    }

    const reading = currentFilteredHistory[nearestIndex];
    if (!reading) {
        handleHistoricalPointerLeave();
        return;
    }

    let closestParam = null;
    let pointX = mouseX;

    const availableKeys = currentFilteredParameters.filter((k) => currentHistoricalPoints[k] && currentHistoricalPoints[k][nearestIndex]);
    if (availableKeys.length > 0) {
        pointX = currentHistoricalPoints[availableKeys[0]][nearestIndex].x;

        let minDistance = Infinity;
        availableKeys.forEach((key) => {
            const pt = currentHistoricalPoints[key][nearestIndex];
            if (pt) {
                const dist = Math.hypot(mouseX - pt.x, mouseY - pt.y);
                if (dist < minDistance) {
                    minDistance = dist;
                    closestParam = key;
                }
            }
        });

        if (minDistance >= 36) {
            closestParam = null;
        }
    }

    historicalHoverIndex = nearestIndex;
    historicalHoveredParam = closestParam;
    drawChart(currentFilteredHistory, currentFilteredParameters);
    renderHistoricalTooltip(reading, nearestIndex, pointX, mouseY, closestParam, width, height);
}

function handleHistoricalPointerLeave() {
    const tooltip = document.getElementById("historical-chart-tooltip");
    if (tooltip) {
        tooltip.classList.remove("visible");
        tooltip.hidden = true;
    }
    if (historicalHoverIndex !== null || historicalHoveredParam !== null) {
        historicalHoverIndex = null;
        historicalHoveredParam = null;
        if (currentFilteredHistory && currentFilteredHistory.length) {
            drawChart(currentFilteredHistory, currentFilteredParameters);
        }
    }
}

function initHistoricalChartEvents() {
    if (historicalChartEventsInitialized) return;
    const canvas = document.getElementById("historical-chart");
    if (!canvas) return;

    canvas.addEventListener("pointermove", handleHistoricalPointerMove);
    canvas.addEventListener("pointerleave", handleHistoricalPointerLeave);
    historicalChartEventsInitialized = true;
}

function updateLegend(parameters) {
    document.getElementById("historical-legend").innerHTML = parameters.map((key) =>
        `<span><i style="background:${colors[key]}"></i>${parameterLabels[key]}</span>`).join("");
}

function updateSummary(history, parameters) {
    const values = parameters.flatMap((key) => history.map((reading) => reading[key]));
    const average = parameters.length === 1 && values.length
        ? values.reduce((total, value) => total + value, 0) / values.length
        : null;
    const summaryMinimum = parameters.length === 1 && values.length ? Math.min(...values).toFixed(2) : "--";
    const summaryMaximum = parameters.length === 1 && values.length ? Math.max(...values).toFixed(2) : "--";
    document.getElementById("summary-title").textContent = parameters.length === 1 ? parameterLabels[parameters[0]] : "All parameters";
    document.getElementById("summary-count").textContent = history.length;
    document.getElementById("summary-average").textContent = average === null ? "--" : average.toFixed(2);
    document.getElementById("summary-minimum").textContent = summaryMinimum;
    document.getElementById("summary-maximum").textContent = summaryMaximum;
    document.getElementById("data-review").textContent = history.length
        ? `Showing ${history.length} saved reading${history.length === 1 ? "" : "s"} for the selected filters.`
        : "No saved readings match the selected filters.";
    const attentionCount = history.filter((reading) => statusFor(reading) !== "Optimal").length;
    const reviewStatus = document.getElementById("review-status");
    reviewStatus.textContent = attentionCount ? `${attentionCount} reading${attentionCount === 1 ? "" : "s"} need attention` : "All readings look good";
    reviewStatus.className = attentionCount ? "review-status review-warning" : "review-status";
}

const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
];

function getDatesWithReadingsSet() {
    const set = new Set();
    sensorHistory.forEach((r) => {
        if (r && r.recorded_at) {
            set.add(localDate(r));
        }
    });
    return set;
}

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
    updateTable();
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

function clearDateFilter() {
    tableFilterDate = null;
    updateDateFilterUI();
    closeCalendarPopup();
    historyPage = 1;
    updateTable();
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
    updateTable();
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

function updateTable() {
    const body = document.getElementById("readings-body");
    const pagination = document.getElementById("readings-pagination");
    const hasDemoData = sensorHistory.some((reading) => reading.status === "Demo");

    let filteredItems = Array.isArray(sensorHistory) ? sensorHistory.slice() : [];

    // Table-level date filter
    if (tableFilterDate) {
        filteredItems = filteredItems.filter((r) => localDate(r) === tableFilterDate);
    }

    // Table-level status filter
    if (tableFilterStatus && tableFilterStatus !== "all") {
        filteredItems = filteredItems.filter((r) => statusFor(r).toLowerCase() === tableFilterStatus);
    }

    // Sort by recorded_at descending (newest first)
    filteredItems.sort((a, b) => new Date(b.recorded_at).getTime() - new Date(a.recorded_at).getTime());

    // 2. Limit and Pagination calculation
    const total = filteredItems.length;
    const limit = readingsPerPage === "all" ? Math.max(total, 1) : parseInt(readingsPerPage, 10);
    const pageCount = Math.ceil(total / limit) || 1;
    historyPage = Math.min(historyPage, Math.max(pageCount, 1));
    const startIndex = (historyPage - 1) * limit;
    const endIndex = Math.min(startIndex + limit, total);
    const pagedItems = filteredItems.slice(startIndex, endIndex);

    // 3. Update table page info text
    const pageInfoEl = document.getElementById("table-page-info");
    if (pageInfoEl) {
        if (total === 0) {
            pageInfoEl.textContent = "Showing 0 readings";
        } else if (readingsPerPage === "all") {
            pageInfoEl.textContent = `Showing all ${total} reading${total === 1 ? "" : "s"}`;
        } else {
            pageInfoEl.textContent = `Showing ${startIndex + 1}–${endIndex} of ${total} reading${total === 1 ? "" : "s"}`;
        }
    }

    // 4. Update Toolbar indicators
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

    document.getElementById("demo-data-note").hidden = !hasDemoData;
    body.innerHTML = pagedItems.map((reading) => {
        const date = new Date(reading.recorded_at);
        const qualityStatus = statusFor(reading);
        const isDemo = reading.status && reading.status.toLowerCase().includes("demo");
        const statusLabel = isDemo ? `Demo · ${qualityStatus}` : qualityStatus;
        const statusClass = isDemo ? "demo" : qualityStatus.toLowerCase();
        return `<tr><td>${date.toLocaleDateString()}</td><td>${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</td><td>${reading.temperature} °C</td><td>${reading.ph}</td><td><span class="table-status ${statusClass}">${statusLabel}</span></td></tr>`;
    }).join("");
    document.getElementById("table-empty").hidden = total > 0;

    // 5. Render Pagination controls
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
            updateTable();
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

function applyFilters() {
    const history = filterHistory(sensorHistory);
    const parameters = selectedParameters();
    currentFilteredHistory = history;
    currentFilteredParameters = parameters;
    const hasData = history.length > 0;
    document.getElementById("history-count").textContent = `${history.length} reading${history.length === 1 ? "" : "s"}`;
    const chartExportBtn = document.getElementById("history-export-button");
    if (chartExportBtn) chartExportBtn.disabled = sensorHistory.length === 0;
    const tableExportBtn = document.getElementById("table-export-button");
    if (tableExportBtn) tableExportBtn.disabled = sensorHistory.length === 0;
    document.getElementById("history-empty").hidden = hasData;
    if (hasData) {
        initHistoricalChartEvents();
        drawChart(history, parameters);
    } else {
        handleHistoricalPointerLeave();
    }
    updateLegend(parameters);
    updateSummary(history, parameters);
}

// ==========================================
// HISTORICAL EXPORT MODAL & FILTER LOGIC
// ==========================================

const exportModal = document.getElementById("historical-export-modal");
const closeExportBtn = document.getElementById("close-export-modal");
const cancelExportBtn = document.getElementById("cancel-export-btn");
const confirmExportBtn = document.getElementById("confirm-export-btn");
const confirmExportText = document.getElementById("confirm-export-text");
const exportDateScopeRadios = document.querySelectorAll('input[name="export-date-scope"]');
const exportSingleDateWrap = document.getElementById("export-single-date-wrap");
const exportTargetDateInput = document.getElementById("export-target-date");
const exportDateSyncBtn = document.getElementById("export-date-sync-active");
const exportStatusRadios = document.querySelectorAll('input[name="export-status-filter"]');
const exportFormatRadios = document.querySelectorAll('input[name="export-file-format"]');

function openExportModal() {
    if (!exportModal) return;

    // 1. Sync Date selection: if user has a tableFilterDate active, default to that single date
    if (tableFilterDate) {
        const singleRadio = document.getElementById("export-date-single");
        if (singleRadio) singleRadio.checked = true;
        if (exportSingleDateWrap) exportSingleDateWrap.hidden = false;
        if (exportTargetDateInput) exportTargetDateInput.value = tableFilterDate;
    } else {
        const allRadio = document.getElementById("export-date-all");
        if (allRadio) allRadio.checked = true;
        if (exportSingleDateWrap) exportSingleDateWrap.hidden = true;
        if (exportTargetDateInput && !exportTargetDateInput.value) {
            if (sensorHistory.length > 0) {
                exportTargetDateInput.value = localDate(sensorHistory[0]);
            } else {
                exportTargetDateInput.value = new Date().toISOString().split("T")[0];
            }
        }
    }

    // 2. Sync Status selection: if user has a tableFilterStatus active ('optimal', 'warning', 'critical'), select it
    if (tableFilterStatus && ["optimal", "warning", "critical"].includes(tableFilterStatus.toLowerCase())) {
        const targetRadio = document.querySelector(`input[name="export-status-filter"][value="${tableFilterStatus.toLowerCase()}"]`);
        if (targetRadio) targetRadio.checked = true;
    } else {
        const allStatusRadio = document.querySelector('input[name="export-status-filter"][value="all"]');
        if (allStatusRadio) allStatusRadio.checked = true;
    }

    // 3. Reset format to xlsx default if not set
    const xlsxRadio = document.querySelector('input[name="export-file-format"][value="xlsx"]');
    if (xlsxRadio && !document.querySelector('input[name="export-file-format"]:checked')) {
        xlsxRadio.checked = true;
    }

    // 4. Update preview count & button label
    updateExportPreview();

    // 5. Open dialog
    exportModal.hidden = false;
    document.body.style.overflow = "hidden";
}

function closeExportModal() {
    if (!exportModal) return;
    exportModal.hidden = true;
    document.body.style.overflow = "";
}

function getSelectedExportFilters() {
    const dateScopeRadio = document.querySelector('input[name="export-date-scope"]:checked');
    const dateScope = dateScopeRadio ? dateScopeRadio.value : "all";
    const targetDate = exportTargetDateInput ? exportTargetDateInput.value.trim() : "";

    const statusRadio = document.querySelector('input[name="export-status-filter"]:checked');
    const status = statusRadio ? statusRadio.value.toLowerCase() : "all";

    const formatRadio = document.querySelector('input[name="export-file-format"]:checked');
    const format = formatRadio ? formatRadio.value.toLowerCase() : "xlsx";

    return {
        dateScope,
        targetDate: dateScope === "single" ? targetDate : "all",
        status,
        format
    };
}

function calculateMatchingReadings(targetDate, targetStatus) {
    if (!Array.isArray(sensorHistory) || sensorHistory.length === 0) return 0;
    let count = 0;
    sensorHistory.forEach((reading) => {
        // Date match check
        if (targetDate && targetDate !== "all") {
            if (localDate(reading) !== targetDate) return;
        }

        // Status match check
        if (targetStatus && targetStatus !== "all") {
            const st = statusFor(reading).toLowerCase();
            if (st !== targetStatus) return;
        }

        count++;
    });
    return count;
}

function updateExportPreview() {
    const filters = getSelectedExportFilters();
    const matchCount = calculateMatchingReadings(filters.targetDate, filters.status);

    const previewCard = document.getElementById("export-preview-card");
    const previewBadge = document.getElementById("export-preview-badge");
    const previewText = document.getElementById("export-preview-text");

    const formatLabel = filters.format === "csv" ? "CSV (.csv)" : "Excel (.xlsx)";
    if (confirmExportText) {
        confirmExportText.textContent = `Download ${formatLabel}`;
    }

    let dateDesc = "across all logged dates";
    if (filters.dateScope === "single" && filters.targetDate && filters.targetDate !== "all") {
        const parts = filters.targetDate.split("-");
        if (parts.length === 3) {
            const dObj = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
            dateDesc = `for ${isNaN(dObj.getTime()) ? filters.targetDate : dObj.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}`;
        } else {
            dateDesc = `for ${filters.targetDate}`;
        }
    }

    let statusDesc = "all statuses";
    if (filters.status === "optimal") statusDesc = "Optimal water quality records";
    else if (filters.status === "warning") statusDesc = "Warning alert records";
    else if (filters.status === "critical") statusDesc = "Critical condition records";

    if (matchCount > 0) {
        if (previewCard) previewCard.classList.remove("no-matches");
        if (previewBadge) {
            previewBadge.textContent = `${matchCount} reading${matchCount === 1 ? "" : "s"} ready`;
            previewBadge.className = "preview-badge preview-badge-ready";
        }
        if (previewText) {
            previewText.textContent = `Ready to export ${matchCount} reading${matchCount === 1 ? "" : "s"} (${statusDesc}, ${dateDesc}) in ${formatLabel} format.`;
        }
        if (confirmExportBtn) confirmExportBtn.disabled = false;
    } else {
        if (previewCard) previewCard.classList.add("no-matches");
        if (previewBadge) {
            previewBadge.textContent = "0 readings found";
            previewBadge.className = "preview-badge preview-badge-empty";
        }
        if (previewText) {
            previewText.textContent = `No saved pond readings match ${statusDesc} ${dateDesc}. Please choose a different date or status.`;
        }
        if (confirmExportBtn) confirmExportBtn.disabled = true;
    }
}

async function executeHistoricalExport() {
    if (!confirmExportBtn || confirmExportBtn.disabled) return;
    const filters = getSelectedExportFilters();

    const originalText = confirmExportText ? confirmExportText.textContent : "Download Export";
    confirmExportBtn.disabled = true;
    confirmExportBtn.setAttribute("aria-busy", "true");
    if (confirmExportText) confirmExportText.textContent = "Generating Export...";

    try {
        const url = `/historical/export?date=${encodeURIComponent(filters.targetDate)}&status=${encodeURIComponent(filters.status)}&format=${encodeURIComponent(filters.format)}`;
        const response = await fetch(url);
        if (response.redirected) {
            throw new Error("Your session has expired. Sign in again to download historical data.");
        }
        if (!response.ok) {
            let message = "The historical readings could not be exported.";
            try {
                const result = await response.json();
                message = result.error || message;
            } catch (err) {
                console.error("Export error parsing:", err);
            }
            throw new Error(message);
        }

        // Determine filename from Content-Disposition header if available
        let filename = `shrimpguard-historical-${filters.targetDate === 'all' ? 'all-dates' : filters.targetDate}-${filters.status}.${filters.format}`;
        const disposition = response.headers.get("Content-Disposition");
        if (disposition && disposition.includes("filename=")) {
            const nameParts = disposition.split("filename=");
            if (nameParts.length > 1) {
                filename = nameParts[1].split(";")[0].replace(/['"]/g, "").trim();
            }
        }

        const blob = await response.blob();
        const downloadUrl = URL.createObjectURL(blob);
        const downloadLink = document.createElement("a");
        downloadLink.href = downloadUrl;
        downloadLink.download = filename;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        downloadLink.remove();
        setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);

        closeExportModal();
    } catch (error) {
        console.error("Unable to export historical readings:", error);
        window.alert(`Unable to download historical data: ${error.message}`);
    } finally {
        confirmExportBtn.removeAttribute("aria-busy");
        if (confirmExportText) confirmExportText.textContent = originalText;
        updateExportPreview();
    }
}

// Bind Chart and Table export buttons
const chartExportBtn = document.getElementById("history-export-button");
if (chartExportBtn) {
    chartExportBtn.addEventListener("click", () => openExportModal());
}

const tableExportBtn = document.getElementById("table-export-button");
if (tableExportBtn) {
    tableExportBtn.addEventListener("click", () => openExportModal());
}

// Event Listeners for Export Modal
if (closeExportBtn) closeExportBtn.addEventListener("click", closeExportModal);
if (cancelExportBtn) cancelExportBtn.addEventListener("click", closeExportModal);
if (confirmExportBtn) confirmExportBtn.addEventListener("click", executeHistoricalExport);

if (exportModal) {
    exportModal.addEventListener("click", (e) => {
        if (e.target === exportModal) closeExportModal();
    });
}

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && exportModal && !exportModal.hidden) {
        closeExportModal();
    }
});

exportDateScopeRadios.forEach((radio) => {
    radio.addEventListener("change", () => {
        if (exportSingleDateWrap) {
            exportSingleDateWrap.hidden = radio.value !== "single";
        }
        updateExportPreview();
    });
});

if (exportTargetDateInput) {
    exportTargetDateInput.addEventListener("input", updateExportPreview);
    exportTargetDateInput.addEventListener("change", updateExportPreview);
}

if (exportDateSyncBtn) {
    exportDateSyncBtn.addEventListener("click", () => {
        if (tableFilterDate && exportTargetDateInput) {
            exportTargetDateInput.value = tableFilterDate;
            updateExportPreview();
        } else if (sensorHistory.length > 0 && exportTargetDateInput) {
            exportTargetDateInput.value = localDate(sensorHistory[0]);
            updateExportPreview();
        }
    });
}

exportStatusRadios.forEach((radio) => {
    radio.addEventListener("change", updateExportPreview);
});

exportFormatRadios.forEach((radio) => {
    radio.addEventListener("change", updateExportPreview);
});

// Bind Limit selector
const tableLimitSelect = document.getElementById("table-limit-select");
if (tableLimitSelect) {
    tableLimitSelect.addEventListener("change", (e) => {
        readingsPerPage = e.target.value;
        historyPage = 1;
        updateTable();
    });
}

// Bind Date Filter button & Calendar nav
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

// Bind Status Filter button & Dropdown
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

// Filter form submit listener (only updates Historical Review & Visual Trend)
const historyFilterForm = document.getElementById("history-filter");
if (historyFilterForm) {
    historyFilterForm.addEventListener("submit", (event) => {
        event.preventDefault();
        applyFilters();
    });
}

// Fetch historical readings from API
async function loadHistory() {
    try {
        const response = await fetch("/api/readings/history");
        if (!response.ok) {
            throw new Error(`History request failed with status ${response.status}.`);
        }

        const history = await response.json();
        if (!Array.isArray(history)) {
            throw new Error("The history response has an invalid format.");
        }

        sensorHistory = history;
        if (!calInitialized && sensorHistory.length > 0) {
            const latestDate = new Date(sensorHistory[0].recorded_at);
            if (!isNaN(latestDate.getTime())) {
                calYear = latestDate.getFullYear();
                calMonth = latestDate.getMonth();
                calInitialized = true;
            }
        }
        renderCalendar();
    } catch (error) {
        console.error("Unable to load saved sensor history:", error);
        sensorHistory = [];
        const countBadge = document.getElementById("history-count");
        if (countBadge) countBadge.textContent = "Data unavailable";
        const historyEmpty = document.getElementById("history-empty");
        if (historyEmpty) {
            historyEmpty.textContent = "Unable to load sensor data. Please refresh or retry.";
            historyEmpty.hidden = false;
        }
        const tableEmpty = document.getElementById("table-empty");
        if (tableEmpty) {
            tableEmpty.textContent = "Unable to load sensor data from the database.";
            tableEmpty.hidden = false;
        }
        const readingsBody = document.getElementById("readings-body");
        if (readingsBody) readingsBody.replaceChildren();
        const paginationNav = document.getElementById("readings-pagination");
        if (paginationNav) paginationNav.hidden = true;
        const pageInfo = document.getElementById("table-page-info");
        if (pageInfo) pageInfo.textContent = "Showing 0 readings";
        return;
    }

    applyFilters();
    updateTable();
}

closeCalendarPopup();
closeStatusDropdown();
updateDeviceTime();
setInterval(updateDeviceTime, 1000);
loadHistory();
setInterval(loadHistory, 10000);
window.addEventListener("resize", () => {
    if (currentFilteredHistory && currentFilteredHistory.length) {
        drawChart(currentFilteredHistory, currentFilteredParameters);
    }
});
