let sensorHistory = [];
let historyPage = 1;
const readingsPerPage = 10;
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
    if (temp < 24) {
        return { label: "Critically Low", level: "critical", badgeClass: "status-critical" };
    }
    if (temp < 26) {
        return { label: "Too Cold", level: "warning", badgeClass: "status-warning" };
    }
    if (temp > 34) {
        return { label: "Critically High", level: "critical", badgeClass: "status-critical" };
    }
    if (temp > 32) {
        return { label: "Too Hot", level: "warning", badgeClass: "status-warning" };
    }
    return { label: "Optimal", level: "optimal", badgeClass: "status-optimal" };
}

function getPhStatus(phLevel) {
    const ph = Number(phLevel);
    if (ph < 7.0) {
        return { label: "Critically Acidic", level: "critical", badgeClass: "status-critical" };
    }
    if (ph < 7.5) {
        return { label: "Too Acidic", level: "warning", badgeClass: "status-warning" };
    }
    if (ph > 9.0) {
        return { label: "Critically Alkaline", level: "critical", badgeClass: "status-critical" };
    }
    if (ph > 8.5) {
        return { label: "Too Alkaline", level: "warning", badgeClass: "status-warning" };
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
    const isGood = overallStatus === "Optimal";

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
            <span class="tooltip-status-pill ${isGood ? 'pill-good' : 'pill-warn'}">
                ${isGood ? '✓ Optimal Quality' : '! Needs Attention'}
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

function updateTable(history) {
    const body = document.getElementById("readings-body");
    const pagination = document.getElementById("readings-pagination");
    const hasDemoData = history.some((reading) => reading.status === "Demo");
    const sortedHistory = history.slice().reverse();
    const pageCount = Math.ceil(sortedHistory.length / readingsPerPage);
    historyPage = Math.min(historyPage, Math.max(pageCount, 1));
    document.getElementById("demo-data-note").hidden = !hasDemoData;
    body.innerHTML = sortedHistory.slice(
        (historyPage - 1) * readingsPerPage,
        historyPage * readingsPerPage
    ).map((reading) => {
        const date = new Date(reading.recorded_at);
        const qualityStatus = statusFor(reading);
        const isDemo = reading.status === "Demo";
        const statusLabel = isDemo ? `Demo · ${qualityStatus}` : qualityStatus;
        const statusClass = isDemo ? "demo" : qualityStatus.toLowerCase();
        return `<tr><td>${date.toLocaleDateString()}</td><td>${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</td><td>${reading.temperature} °C</td><td>${reading.ph}</td><td><span class="table-status ${statusClass}">${statusLabel}</span></td></tr>`;
    }).join("");
    document.getElementById("table-empty").hidden = history.length > 0;
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
            updateTable(history);
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
    document.getElementById("history-export-button").disabled = sensorHistory.length === 0;
    document.getElementById("history-empty").hidden = hasData;
    if (hasData) {
        initHistoricalChartEvents();
        drawChart(history, parameters);
    } else {
        handleHistoricalPointerLeave();
    }
    updateLegend(parameters);
    updateSummary(history, parameters);
    updateTable(history);
}

document.getElementById("history-export-button").addEventListener("click", async (event) => {
    const button = event.currentTarget;
    button.disabled = true;
    button.setAttribute("aria-busy", "true");

    try {
        const response = await fetch("/historical/export");
        if (response.redirected) {
            throw new Error("Your session has expired. Sign in again to download historical data.");
        }
        if (!response.ok || !(response.headers.get("Content-Type") || "").includes("spreadsheetml")) {
            let message = "The historical data could not be exported.";
            try {
                const result = await response.json();
                message = result.error || message;
            } catch (error) {
                console.error("The export server returned an unexpected response:", error);
            }
            throw new Error(message);
        }

        const downloadUrl = URL.createObjectURL(await response.blob());
        const downloadLink = document.createElement("a");
        downloadLink.href = downloadUrl;
        downloadLink.download = "shrimpguard-historical-data.xlsx";
        document.body.appendChild(downloadLink);
        downloadLink.click();
        downloadLink.remove();
        setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);
    } catch (error) {
        console.error("Unable to export historical readings:", error);
        window.alert(`Unable to download historical data: ${error.message}`);
    } finally {
        button.disabled = sensorHistory.length === 0;
        button.removeAttribute("aria-busy");
    }
});

document.getElementById("history-filter").addEventListener("submit", (event) => {
    event.preventDefault();
    historyPage = 1;
    applyFilters();
});

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
    } catch (error) {
        console.error("Unable to load saved sensor history:", error);
        sensorHistory = [];
        document.getElementById("history-count").textContent = "Data unavailable";
        document.getElementById("history-empty").textContent = "Unable to load sensor data. Please refresh or retry.";
        document.getElementById("history-empty").hidden = false;
        document.getElementById("table-empty").textContent = "Unable to load sensor data from the database.";
        document.getElementById("table-empty").hidden = false;
        document.getElementById("readings-body").replaceChildren();
        document.getElementById("readings-pagination").hidden = true;
        handleHistoricalPointerLeave();
        return;
    }

    applyFilters();
}

updateDeviceTime();
setInterval(updateDeviceTime, 1000);
loadHistory();
setInterval(loadHistory, 10000);
window.addEventListener("resize", () => {
    if (currentFilteredHistory && currentFilteredHistory.length) {
        drawChart(currentFilteredHistory, currentFilteredParameters);
    }
});
