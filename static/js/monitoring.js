const chartColors = ["#2f6fbd", "#2f8a57"];

let currentHistory = [];
let currentPoints = null;
let hoverIndex = null;
let hoveredParam = null;
let chartEventsInitialized = false;

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

function getQualityStatus(reading) {
    if (!reading || !reading.status) return "Waiting for a reading";
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

function updateSummary(reading) {
    document.getElementById("monitor-temperature").textContent = reading.temperature;
    document.getElementById("monitor-ph").textContent = reading.ph;
    const status = getQualityStatus(reading);
    const statusEl = document.getElementById("monitoring-status");
    if (statusEl) {
        statusEl.textContent = status;
        statusEl.className = `status-${status.toLowerCase()}`;
    }
    const statusDot = document.querySelector(".monitoring-status-dot");
    if (statusDot) {
        statusDot.className = `monitoring-status-dot dot-${status.toLowerCase()}`;
    }
    document.getElementById("monitoring-updated").textContent =
        "Last updated " + new Date(reading.recorded_at).toLocaleString();
    document.getElementById("monitoring-demo-note").hidden = reading.status !== "Demo";
}

function drawTrendChart(history) {
    if (!Array.isArray(history) || history.length === 0) return;
    currentHistory = history;

    const canvas = document.getElementById("trend-chart");
    if (!canvas) return;
    const context = canvas.getContext("2d");
    const width = canvas.clientWidth || 600;
    const height = canvas.clientHeight || 300;
    const scale = window.devicePixelRatio || 1;

    const series = ["temperature", "ph"];
    const values = series.map((key) => history.map((reading) => Number(reading[key])));
    const allValues = values.flat();
    const minimum = Math.min(...allValues);
    const maximum = Math.max(...allValues);
    const range = maximum - minimum || 1;
    const padding = { top: 26, right: 30, bottom: 32, left: 42 };

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

    // Compute coordinate points
    const pointsBySeries = series.map((key, seriesIndex) => {
        return values[seriesIndex].map((value, index) => {
            const x = history.length === 1
                ? padding.left + (width - padding.left - padding.right) / 2
                : padding.left + (index / (history.length - 1)) * (width - padding.left - padding.right);
            const y = padding.top + (1 - (value - minimum) / range) * (height - padding.top - padding.bottom);
            return { x, y, value, key, reading: history[index], index };
        });
    });
    currentPoints = pointsBySeries;

    // Subtle vertical dashed guide for hoverIndex
    if (hoverIndex !== null && hoverIndex >= 0 && hoverIndex < history.length) {
        const hoverX = pointsBySeries[0][hoverIndex].x;
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

    // Draw lines and points
    series.forEach((key, seriesIndex) => {
        const pts = pointsBySeries[seriesIndex];
        if (!pts.length) return;

        // Draw connecting line
        context.beginPath();
        pts.forEach((pt, index) => {
            if (index === 0) context.moveTo(pt.x, pt.y);
            else context.lineTo(pt.x, pt.y);
        });
        context.strokeStyle = chartColors[seriesIndex];
        context.lineWidth = 2.5;
        context.lineCap = "round";
        context.lineJoin = "round";
        context.stroke();

        // Draw points with hover glow effects
        pts.forEach((pt, index) => {
            const isHovered = hoverIndex === index;
            const isFocused = isHovered && (hoveredParam === key || hoveredParam === null);

            // Halo glow for hovered point
            if (isHovered) {
                context.beginPath();
                context.arc(pt.x, pt.y, isFocused ? 11 : 7, 0, Math.PI * 2);
                context.fillStyle = seriesIndex === 0
                    ? "rgba(47, 111, 189, 0.22)"
                    : "rgba(47, 138, 87, 0.22)";
                context.fill();
            }

            // Outer point ring & dot
            context.beginPath();
            context.arc(pt.x, pt.y, isHovered ? (isFocused ? 5.5 : 4.5) : 3.5, 0, Math.PI * 2);
            context.fillStyle = isHovered ? "#ffffff" : chartColors[seriesIndex];
            context.fill();
            context.strokeStyle = chartColors[seriesIndex];
            context.lineWidth = isHovered ? 2.5 : 1.5;
            context.stroke();
        });
    });
}

function renderTooltip(reading, index, pointX, mouseY, focusedParam, containerWidth, containerHeight) {
    let tooltip = document.getElementById("chart-tooltip");
    if (!tooltip) {
        const wrap = document.querySelector(".monitoring-chart-wrap");
        if (!wrap) return;
        tooltip = document.createElement("div");
        tooltip.id = "chart-tooltip";
        tooltip.className = "monitoring-chart-tooltip";
        wrap.appendChild(tooltip);
    }

    const tempVal = Number(reading.temperature);
    const phVal = Number(reading.ph);
    const tempStatus = getTemperatureStatus(tempVal);
    const phStatus = getPhStatus(phVal);
    const overallStatus = getQualityStatus(reading);
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
        ? dateObj.toLocaleDateString([], { month: "short", day: "numeric" })
        : "";

    tooltip.innerHTML = `
        <div class="tooltip-header">
            <span class="tooltip-time-badge">${dateDisplay ? dateDisplay + ' • ' : ''}${timeDisplay}</span>
            <span class="tooltip-status-pill ${pillClass}">
                ${statusLabel}
            </span>
        </div>
        <div class="tooltip-content">
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
        </div>
    `;

    tooltip.hidden = false;
    tooltip.classList.add("visible");

    // Compute dynamic width / height
    const tooltipWidth = tooltip.offsetWidth || 250;
    const tooltipHeight = tooltip.offsetHeight || 110;

    // Flip to left if approaching right edge
    let leftPos = pointX + 16;
    if (leftPos + tooltipWidth > containerWidth - 12) {
        leftPos = pointX - tooltipWidth - 16;
    }
    if (leftPos < 12) leftPos = 12;

    // Position vertically centered at mouseY, clamped within bounds
    let topPos = mouseY - (tooltipHeight / 2);
    topPos = Math.max(10, Math.min(containerHeight - tooltipHeight - 10, topPos));

    tooltip.style.left = `${leftPos}px`;
    tooltip.style.top = `${topPos}px`;
}

function handlePointerMove(event) {
    if (!currentHistory || currentHistory.length === 0 || !currentPoints) return;
    const canvas = document.getElementById("trend-chart");
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
        handlePointerLeave();
        return;
    }

    // Find nearest reading along X axis
    let nearestIndex = 0;
    if (currentHistory.length > 1) {
        const plotWidth = width - padding.left - padding.right;
        const ratio = (mouseX - padding.left) / plotWidth;
        nearestIndex = Math.round(ratio * (currentHistory.length - 1));
        nearestIndex = Math.max(0, Math.min(currentHistory.length - 1, nearestIndex));
    }

    const reading = currentHistory[nearestIndex];
    if (!reading) {
        handlePointerLeave();
        return;
    }

    const tempPt = currentPoints[0] ? currentPoints[0][nearestIndex] : null;
    const phPt = currentPoints[1] ? currentPoints[1][nearestIndex] : null;

    let closestParam = null;
    if (tempPt && phPt) {
        const distTemp = Math.hypot(mouseX - tempPt.x, mouseY - tempPt.y);
        const distPh = Math.hypot(mouseX - phPt.x, mouseY - phPt.y);
        if (Math.min(distTemp, distPh) < 32) {
            closestParam = distTemp < distPh ? "temperature" : "ph";
        }
    }

    const pointX = tempPt ? tempPt.x : mouseX;

    hoverIndex = nearestIndex;
    hoveredParam = closestParam;
    drawTrendChart(currentHistory);
    renderTooltip(reading, nearestIndex, pointX, mouseY, closestParam, width, height);
}

function handlePointerLeave() {
    const tooltip = document.getElementById("chart-tooltip");
    if (tooltip) {
        tooltip.classList.remove("visible");
        tooltip.hidden = true;
    }
    if (hoverIndex !== null || hoveredParam !== null) {
        hoverIndex = null;
        hoveredParam = null;
        if (currentHistory && currentHistory.length) {
            drawTrendChart(currentHistory);
        }
    }
}

function initChartEvents() {
    if (chartEventsInitialized) return;
    const canvas = document.getElementById("trend-chart");
    if (!canvas) return;

    canvas.addEventListener("pointermove", handlePointerMove);
    canvas.addEventListener("pointerleave", handlePointerLeave);
    chartEventsInitialized = true;
}

function updateRecommendations(reading, recommendation) {
    const recommendationsList = document.getElementById("monitoring-recommendations");

    if (!reading) {
        recommendationsList.innerHTML =
            "<li>No reading available yet. Submit dashboard readings to receive AI recommendations.</li>";
        return;
    }

    if (!recommendation) {
        recommendationsList.textContent = "";
        const item = document.createElement("li");
        item.textContent = "AI recommendations are temporarily unavailable.";
        recommendationsList.appendChild(item);
        return;
    }

    recommendationsList.textContent = "";
    const item = document.createElement("li");
    item.textContent = `${recommendation.classification}: ${recommendation.recommendation}`;
    recommendationsList.appendChild(item);
}

async function loadRecommendation(reading) {
    const response = await fetch("/api/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ temperature: reading.temperature, ph: reading.ph })
    });
    if (!response.ok) {
        throw new Error(`Recommendation API returned ${response.status}.`);
    }

    const recommendation = await response.json();
    if (
        typeof recommendation.classification !== "string" ||
        typeof recommendation.recommendation !== "string"
    ) {
        throw new Error("Recommendation response has an invalid format.");
    }
    return recommendation;
}

async function loadMonitoringData() {
    const emptyMessage = document.getElementById("chart-empty");

    try {
        const [latestResponse, historyResponse] = await Promise.all([
            fetch("/api/readings/latest"),
            fetch("/api/readings/history")
        ]);

        if (latestResponse.ok && historyResponse.ok) {
            const latest = await latestResponse.json();
            const history = await historyResponse.json();
            if (!Array.isArray(history)) {
                throw new Error("Sensor history response has an invalid format.");
            }

            if (!latest || history.length === 0) {
                emptyMessage.hidden = false;
                document.getElementById("trend-count").textContent = "No readings yet";
                updateRecommendations(null);
                document.getElementById("monitor-temperature").textContent = "--";
                document.getElementById("monitor-ph").textContent = "--";
                document.getElementById("monitoring-status").textContent = "Waiting for a reading";
                document.getElementById("monitoring-updated").textContent =
                    "No sensor readings are saved yet.";
                document.getElementById("monitoring-demo-note").hidden = true;
                handlePointerLeave();
                return;
            }

            emptyMessage.hidden = true;
            updateSummary(latest);
            try {
                updateRecommendations(latest, await loadRecommendation(latest));
            } catch (error) {
                console.error("Unable to load AI recommendations:", error);
                updateRecommendations(latest, null);
            }
            document.getElementById("trend-count").textContent = `${history.length} reading${
                history.length === 1 ? "" : "s"
            }`;
            initChartEvents();
            drawTrendChart(history);
            return;
        }
        throw new Error(`Sensor API returned ${latestResponse.status} / ${historyResponse.status}.`);
    } catch (error) {
        console.error("Unable to load sensor data for monitoring:", error);
        emptyMessage.hidden = false;
        emptyMessage.textContent = "Unable to load sensor data. Please refresh or retry.";
        document.getElementById("trend-count").textContent = "Data unavailable";
        document.getElementById("monitoring-status").textContent = "Sensor data unavailable";
        document.getElementById("monitoring-updated").textContent =
            "Could not connect to the sensors database.";
        document.getElementById("monitoring-demo-note").hidden = true;
        updateRecommendations(null);
        handlePointerLeave();
    }
}

updateDeviceTime();
setInterval(updateDeviceTime, 1000);
loadMonitoringData();
window.addEventListener("storage", loadMonitoringData);
window.addEventListener("resize", () => {
    if (currentHistory && currentHistory.length) {
        drawTrendChart(currentHistory);
    }
});
setInterval(loadMonitoringData, 10000);
