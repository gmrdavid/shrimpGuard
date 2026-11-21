let sensorHistory = [];
let historyPage = 1;
let readingsPerPage = "10";
let tableFilterDate = null; // null or 'YYYY-MM-DD'
let tableFilterStatus = "all"; // 'all', 'optimal', 'warning', 'critical'
let calYear = new Date().getFullYear();
let calMonth = new Date().getMonth();
let calInitialized = false;
let historyFilterDate = null; // null or 'YYYY-MM-DD'
let historyCalYear = new Date().getFullYear();
let historyCalMonth = new Date().getMonth();
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

function parseSafeDate(val) {
    if (!val) return null;
    if (val instanceof Date) return isNaN(val.getTime()) ? null : val;
    const s = String(val).trim();
    let d = new Date(s);
    if (!isNaN(d.getTime())) return d;
    d = new Date(s.replace(" ", "T"));
    if (!isNaN(d.getTime())) return d;
    return null;
}

function localDate(reading) {
    if (!reading || !reading.recorded_at) return "";
    const date = parseSafeDate(reading.recorded_at);
    if (!date || isNaN(date.getTime())) return "";
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function filterHistory(history) {
    const selectedDate = historyFilterDate || document.getElementById("history-date")?.value;
    const intervalEl = document.getElementById("history-interval");
    const interval = intervalEl ? intervalEl.value : "all";
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

function drawSmoothSpline(ctx, points, tension = 0.18) {
    if (!points || points.length === 0) return;
    if (points.length === 1) {
        ctx.moveTo(points[0].x, points[0].y);
        return;
    }
    if (points.length === 2) {
        ctx.moveTo(points[0].x, points[0].y);
        ctx.lineTo(points[1].x, points[1].y);
        return;
    }

    ctx.moveTo(points[0].x, points[0].y);

    for (let i = 0; i < points.length - 1; i++) {
        const p0 = i > 0 ? points[i - 1] : points[i];
        const p1 = points[i];
        const p2 = points[i + 1];
        const p3 = i < points.length - 2 ? points[i + 2] : p2;

        const cp1x = p1.x + (p2.x - p0.x) * tension;
        const cp1y = p1.y + (p2.y - p0.y) * tension;

        const cp2x = p2.x - (p3.x - p1.x) * tension;
        const cp2y = p2.y - (p3.y - p1.y) * tension;

        ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, p2.x, p2.y);
    }
}

function drawChart(history, parameters) {
    if (!Array.isArray(history) || history.length === 0) {
        const emptyEl = document.getElementById("history-empty");
        if (emptyEl) emptyEl.hidden = false;
        return;
    }
    currentFilteredHistory = history;
    currentFilteredParameters = parameters;

    const emptyEl = document.getElementById("history-empty");
    if (emptyEl) emptyEl.hidden = true;

    const canvas = document.getElementById("historical-chart");
    if (!canvas) return;
    const context = canvas.getContext("2d");
    const width = canvas.clientWidth || 600;
    const height = canvas.clientHeight || 320;
    const scale = window.devicePixelRatio || 1;

    canvas.width = Math.round(width * scale);
    canvas.height = Math.round(height * scale);
    context.scale(scale, scale);
    context.clearRect(0, 0, width, height);

    const isBoth = parameters.includes("temperature") && parameters.includes("ph");
    const isTempOnly = parameters.length === 1 && parameters[0] === "temperature";
    const isPhOnly = parameters.length === 1 && parameters[0] === "ph";
    const isMobile = width < 520;

    const padding = isMobile
        ? { top: 32, right: isBoth ? 38 : 24, bottom: 34, left: 42 }
        : { top: 34, right: isBoth ? 52 : 28, bottom: 36, left: 52 };
    const plotWidth = width - padding.left - padding.right;
    const plotHeight = height - padding.top - padding.bottom;

    // Calculate parameter scales
    let tempMin, tempMax, tempRange;
    if (parameters.includes("temperature")) {
        const tempVals = history.map((r) => Number(r.temperature)).filter((v) => !isNaN(v));
        const rawTMin = tempVals.length ? Math.min(...tempVals) : 25;
        const rawTMax = tempVals.length ? Math.max(...tempVals) : 33;
        const tSpan = Math.max(rawTMax - rawTMin, 0.4);
        tempMin = Math.floor((rawTMin - tSpan * 0.16) * 10) / 10;
        tempMax = Math.ceil((rawTMax + tSpan * 0.16) * 10) / 10;
        if (tempMax - tempMin < 3.0) {
            const mid = (tempMax + tempMin) / 2;
            tempMin = Math.round((mid - 1.5) * 10) / 10;
            tempMax = Math.round((mid + 1.5) * 10) / 10;
        }
        tempRange = tempMax - tempMin || 1;
    }

    let phMin, phMax, phRange;
    if (parameters.includes("ph")) {
        const phVals = history.map((r) => Number(r.ph)).filter((v) => !isNaN(v));
        const rawPMin = phVals.length ? Math.min(...phVals) : 7.0;
        const rawPMax = phVals.length ? Math.max(...phVals) : 8.8;
        const pSpan = Math.max(rawPMax - rawPMin, 0.1);
        phMin = Math.floor((rawPMin - pSpan * 0.18) * 100) / 100;
        phMax = Math.ceil((rawPMax + pSpan * 0.18) * 100) / 100;
        if (phMax - phMin < 0.8) {
            const mid = (phMax + phMin) / 2;
            phMin = Math.round((mid - 0.4) * 100) / 100;
            phMax = Math.round((mid + 0.4) * 100) / 100;
        }
        phRange = phMax - phMin || 1;
    }

    // Subtle Safe-Zone Background Band for Penaeus vannamei (28.0°C - 32.0°C) if temperature is active
    if (parameters.includes("temperature") && tempMin !== undefined) {
        const tOptTopY = Math.max(padding.top, Math.min(height - padding.bottom, padding.top + (1 - (32.0 - tempMin) / tempRange) * plotHeight));
        const tOptBottomY = Math.max(padding.top, Math.min(height - padding.bottom, padding.top + (1 - (28.0 - tempMin) / tempRange) * plotHeight));
        if (tOptBottomY > tOptTopY) {
            context.save();
            context.fillStyle = "rgba(47, 111, 189, 0.035)";
            context.fillRect(padding.left, tOptTopY, plotWidth, tOptBottomY - tOptTopY);
            context.setLineDash([2, 4]);
            context.strokeStyle = "rgba(47, 111, 189, 0.18)";
            context.lineWidth = 1;
            context.beginPath();
            context.moveTo(padding.left, tOptTopY);
            context.lineTo(width - padding.right, tOptTopY);
            context.moveTo(padding.left, tOptBottomY);
            context.lineTo(width - padding.right, tOptBottomY);
            context.stroke();
            context.restore();
        }
    }

    // Horizontal grid lines & Y-axis scale
    const gridSteps = isMobile ? 4 : 5;
    for (let index = 0; index < gridSteps; index += 1) {
        const y = padding.top + (plotHeight / (gridSteps - 1)) * index;

        // Horizontal grid line
        context.beginPath();
        context.strokeStyle = index === gridSteps - 1 ? "#d3ded7" : "#edf2ee";
        context.lineWidth = 1;
        context.setLineDash([]);
        context.moveTo(padding.left, y);
        context.lineTo(width - padding.right, y);
        context.stroke();

        context.font = isMobile ? "600 10px Inter, -apple-system, sans-serif" : "600 11px Inter, -apple-system, sans-serif";
        context.textBaseline = "middle";

        if (isBoth) {
            // Left Axis Label: Temperature in #2f6fbd
            const tempLabel = (tempMax - (tempRange / (gridSteps - 1)) * index).toFixed(1);
            context.fillStyle = "#2f6fbd";
            context.textAlign = "right";
            context.fillText(`${tempLabel}°`, padding.left - 8, y);

            // Right Axis Label: pH in #126b4f
            const phLabel = (phMax - (phRange / (gridSteps - 1)) * index).toFixed(2);
            context.fillStyle = "#126b4f";
            context.textAlign = "left";
            context.fillText(phLabel, width - padding.right + 8, y);
        } else if (isTempOnly) {
            const tempLabel = (tempMax - (tempRange / (gridSteps - 1)) * index).toFixed(1);
            context.fillStyle = "#2f6fbd";
            context.textAlign = "right";
            context.fillText(`${tempLabel}°C`, padding.left - 8, y);
        } else if (isPhOnly) {
            const phLabel = (phMax - (phRange / (gridSteps - 1)) * index).toFixed(2);
            context.fillStyle = "#126b4f";
            context.textAlign = "right";
            context.fillText(phLabel, padding.left - 8, y);
        }
    }

    // Axis Headers
    context.font = "700 9.5px Inter, -apple-system, sans-serif";
    context.textBaseline = "bottom";
    if (isBoth) {
        context.fillStyle = "#2f6fbd";
        context.textAlign = "right";
        context.fillText("°C (TEMP)", padding.left - 6, padding.top - 8);

        context.fillStyle = "#126b4f";
        context.textAlign = "left";
        context.fillText("pH LEVEL", width - padding.right + 6, padding.top - 8);
    } else if (isTempOnly) {
        context.fillStyle = "#2f6fbd";
        context.textAlign = "right";
        context.fillText("TEMP (°C)", padding.left - 6, padding.top - 8);
    } else if (isPhOnly) {
        context.fillStyle = "#126b4f";
        context.textAlign = "right";
        context.fillText("pH LEVEL", padding.left - 6, padding.top - 8);
    }

    // Compute coordinate points per parameter
    currentHistoricalPoints = {};
    parameters.forEach((key) => {
        const isTemp = key === "temperature";
        const minVal = isTemp ? tempMin : phMin;
        const rangeVal = isTemp ? tempRange : phRange;

        currentHistoricalPoints[key] = history.map((reading, index) => {
            const val = Number(reading[key]);
            const x = history.length === 1
                ? padding.left + plotWidth / 2
                : padding.left + (index / (history.length - 1)) * plotWidth;
            const y = padding.top + (1 - (val - minVal) / rangeVal) * plotHeight;
            return { x, y, value: val, key, reading, index };
        });
    });

    // X-Axis Baseline
    context.beginPath();
    context.strokeStyle = "#d4dfd8";
    context.lineWidth = 1;
    context.moveTo(padding.left, height - padding.bottom);
    context.lineTo(width - padding.right, height - padding.bottom);
    context.stroke();

    // Time Ticks and Labels along X-Axis
    if (history.length > 0) {
        const firstKey = parameters[0];
        const refPoints = currentHistoricalPoints[firstKey] || [];
        const maxTicks = isMobile ? 3 : (width < 768 ? 4 : 6);
        const numTicks = Math.min(maxTicks, history.length);
        const tickStep = (history.length - 1) / (numTicks - 1 || 1);
        context.fillStyle = "#718277";
        context.font = "600 10.5px Inter, -apple-system, sans-serif";
        context.textAlign = "center";
        context.textBaseline = "top";

        for (let i = 0; i < numTicks; i++) {
            const idx = Math.round(i * tickStep);
            const pt = refPoints[idx];
            if (!pt) continue;

            const rDate = parseSafeDate(pt.reading && pt.reading.recorded_at);
            let timeStr = "";
            if (rDate && !isNaN(rDate.getTime())) {
                timeStr = rDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
            } else {
                timeStr = `#${idx + 1}`;
            }

            // Small tick
            context.beginPath();
            context.strokeStyle = "#ccd7d0";
            context.lineWidth = 1;
            context.moveTo(pt.x, height - padding.bottom);
            context.lineTo(pt.x, height - padding.bottom + 5);
            context.stroke();

            // Label
            context.fillText(timeStr, pt.x, height - padding.bottom + 8);
        }
        context.textAlign = "left";
    }

    // Draw Smooth Splines and Translucent Area Gradients per Parameter
    parameters.forEach((key) => {
        const pts = currentHistoricalPoints[key];
        if (!pts || !pts.length) return;
        const color = key === "temperature" ? "#2f6fbd" : "#126b4f";
        const gradRgb = key === "temperature" ? "47, 111, 189" : "18, 107, 79";

        // Area Gradient
        context.save();
        const grad = context.createLinearGradient(0, padding.top, 0, height - padding.bottom);
        grad.addColorStop(0, `rgba(${gradRgb}, 0.17)`);
        grad.addColorStop(0.7, `rgba(${gradRgb}, 0.04)`);
        grad.addColorStop(1, `rgba(${gradRgb}, 0.00)`);

        context.beginPath();
        drawSmoothSpline(context, pts, 0.18);
        context.lineTo(pts[pts.length - 1].x, height - padding.bottom);
        context.lineTo(pts[0].x, height - padding.bottom);
        context.closePath();
        context.fillStyle = grad;
        context.fill();
        context.restore();

        // Spline Curve Stroke
        context.save();
        context.beginPath();
        drawSmoothSpline(context, pts, 0.18);
        context.strokeStyle = color;
        context.lineWidth = 2.75;
        context.lineCap = "round";
        context.lineJoin = "round";
        context.stroke();
        context.restore();
    });

    // Vertical dashed guide line & floating timestamp pill when hovering
    if (historicalHoverIndex !== null && historicalHoverIndex >= 0 && historicalHoverIndex < history.length) {
        const firstKey = parameters[0];
        if (currentHistoricalPoints[firstKey] && currentHistoricalPoints[firstKey][historicalHoverIndex]) {
            const hoverX = currentHistoricalPoints[firstKey][historicalHoverIndex].x;
            context.save();
            context.beginPath();
            context.setLineDash([3, 3]);
            context.strokeStyle = "rgba(18, 107, 79, 0.55)";
            context.lineWidth = 1.5;
            context.moveTo(hoverX, padding.top - 6);
            context.lineTo(hoverX, height - padding.bottom + 6);
            context.stroke();

            // Top Scrubber Pill
            const rDate = parseSafeDate(history[historicalHoverIndex] && history[historicalHoverIndex].recorded_at);
            const pillText = rDate ? rDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : `#${historicalHoverIndex + 1}`;
            context.font = "600 10px Inter, -apple-system, sans-serif";
            const pillTextW = context.measureText(pillText).width;
            const pillW = pillTextW + 14;
            const pillH = 19;
            let pillX = hoverX - pillW / 2;
            if (pillX < padding.left) pillX = padding.left;
            if (pillX + pillW > width - padding.right) pillX = width - padding.right - pillW;
            const pillY = padding.top - 23;

            context.fillStyle = "#1e293b";
            context.beginPath();
            if (context.roundRect) {
                context.roundRect(pillX, pillY, pillW, pillH, 4);
            } else {
                context.rect(pillX, pillY, pillW, pillH);
            }
            context.fill();

            context.fillStyle = "#ffffff";
            context.textAlign = "center";
            context.textBaseline = "middle";
            context.fillText(pillText, pillX + pillW / 2, pillY + pillH / 2);
            context.restore();
        }
    }

    // Draw Points with Hover Glow Effects
    parameters.forEach((key) => {
        const pts = currentHistoricalPoints[key];
        if (!pts || !pts.length) return;
        const color = key === "temperature" ? "#2f6fbd" : "#126b4f";
        const haloColor = key === "temperature" ? "rgba(47, 111, 189, 0.22)" : "rgba(18, 107, 79, 0.22)";

        pts.forEach((pt, index) => {
            const isHovered = historicalHoverIndex === index;
            const isFocused = isHovered && (historicalHoveredParam === key || historicalHoveredParam === null);

            if (isHovered) {
                // Ambient glow
                context.beginPath();
                context.arc(pt.x, pt.y, isFocused ? 11 : 8, 0, Math.PI * 2);
                context.fillStyle = haloColor;
                context.fill();

                // Outer Ring
                context.beginPath();
                context.arc(pt.x, pt.y, isFocused ? 5.5 : 4.5, 0, Math.PI * 2);
                context.fillStyle = "#ffffff";
                context.fill();
                context.strokeStyle = color;
                context.lineWidth = 2.5;
                context.stroke();

                // Core Dot
                context.beginPath();
                context.arc(pt.x, pt.y, 2.2, 0, Math.PI * 2);
                context.fillStyle = color;
                context.fill();
            } else {
                // Crisp standard point
                context.beginPath();
                context.arc(pt.x, pt.y, 3, 0, Math.PI * 2);
                context.fillStyle = "#ffffff";
                context.fill();
                context.strokeStyle = color;
                context.lineWidth = 1.75;
                context.stroke();
            }
        });
    });

    // Update legend with active values
    const activeReading = (historicalHoverIndex !== null && history[historicalHoverIndex])
        ? history[historicalHoverIndex]
        : (history.length > 0 ? history[history.length - 1] : null);
    updateLegend(parameters, activeReading);
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
                    <span class="tooltip-param-value">${tempVal.toFixed(2)} °C</span>
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
    const isBoth = currentFilteredParameters.includes("temperature") && currentFilteredParameters.includes("ph");
    const isMobile = width < 520;
    const padding = isMobile
        ? { top: 32, right: isBoth ? 38 : 24, bottom: 34, left: 42 }
        : { top: 34, right: isBoth ? 52 : 28, bottom: 36, left: 52 };

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

function updateLegend(parameters, activeReading = null) {
    const legendEl = document.getElementById("historical-legend");
    if (!legendEl) return;

    const reading = activeReading || (currentFilteredHistory && currentFilteredHistory.length > 0 ? currentFilteredHistory[currentFilteredHistory.length - 1] : null);
    const isBoth = parameters.includes("temperature") && parameters.includes("ph");

    let itemsHtml = "";
    parameters.forEach((key) => {
        const val = reading ? Number(reading[key]) : null;
        let valFormatted = "--";
        if (val !== null && !isNaN(val)) {
            valFormatted = key === "temperature" ? `${val.toFixed(1)} °C` : `${val.toFixed(2)}`;
        }
        const color = key === "temperature" ? "#2f6fbd" : "#126b4f";
        const label = parameterLabels[key] || key;

        itemsHtml += `
            <span class="legend-pill-item legend-pill-${key}">
                <i class="legend-indicator" style="background:${color};"></i>
                <span class="legend-label">${label}</span>
                <span class="legend-val-badge" id="historical-legend-${key}-val">${valFormatted}</span>
            </span>
        `;
    });

    const modeTag = isBoth
        ? `<span class="legend-axis-mode-tag" title="Calibrated independent Y-axes: Left = Temp, Right = pH">
               <svg class="ui-icon" style="width:12px;height:12px;" aria-hidden="true"><use href="#icon-chart"></use></svg>
               Dual-Axis Telemetry
           </span>`
        : `<span class="legend-axis-mode-tag" title="Single scale axis">
               <svg class="ui-icon" style="width:12px;height:12px;" aria-hidden="true"><use href="#icon-chart"></use></svg>
               Single Axis Mode
           </span>`;

    const safeZoneTag = `
        <span class="legend-safezone-tag" title="Penaeus vannamei standards: 28-32°C & pH 7.5-8.5">
            <span class="cal-dot cal-dot-green" style="width:7px;height:7px;"></span>
            <i>P. vannamei</i> Safe Zones
        </span>
    `;

    legendEl.innerHTML = `
        <div class="legend-items-group">${itemsHtml}</div>
        <div class="legend-meta-group">${modeTag}${safeZoneTag}</div>
    `;
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
    if (!status) return;
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

    const items = document.querySelectorAll("#status-dropdown-menu .status-menu-item");
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

function selectLimitFilter(limit) {
    if (!limit) return;
    readingsPerPage = String(limit);
    const textEl = document.getElementById("table-limit-text");
    if (textEl) {
        textEl.textContent = limit === "all" ? "Show: All rows" : `Show: ${limit} rows`;
    }

    const items = document.querySelectorAll("#limit-dropdown-menu .limit-menu-item");
    items.forEach((btn) => {
        if (btn.getAttribute("data-limit") === String(limit)) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    const selectEl = document.getElementById("table-limit-select");
    if (selectEl) {
        selectEl.value = limit;
    }

    closeLimitDropdown();
    historyPage = 1;
    updateTable();
}

function renderHistoryCalendar() {
    const titleEl = document.getElementById("history-cal-month-title");
    const gridEl = document.getElementById("history-calendar-days-grid");
    if (!titleEl || !gridEl) return;

    titleEl.textContent = `${monthNames[historyCalMonth]} ${historyCalYear}`;
    gridEl.innerHTML = "";

    const datesWithReadings = getDatesWithReadingsSet();

    const firstDayIndex = new Date(historyCalYear, historyCalMonth, 1).getDay();
    const totalDays = new Date(historyCalYear, historyCalMonth + 1, 0).getDate();
    const prevMonthDays = new Date(historyCalYear, historyCalMonth, 0).getDate();

    for (let i = firstDayIndex - 1; i >= 0; i--) {
        const filler = document.createElement("div");
        filler.className = "cal-day cal-day-empty";
        filler.textContent = String(prevMonthDays - i);
        gridEl.appendChild(filler);
    }

    for (let day = 1; day <= totalDays; day++) {
        const dayStr = `${historyCalYear}-${String(historyCalMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
        const hasData = datesWithReadings.has(dayStr);
        const isSelected = historyFilterDate === dayStr;

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
            selectHistoryDateFilter(dayStr);
        });

        gridEl.appendChild(dayBtn);
    }
}

function selectHistoryDateFilter(dateStr) {
    if (historyFilterDate === dateStr) {
        historyFilterDate = null;
    } else {
        historyFilterDate = dateStr;
    }
    const histDateInput = document.getElementById("history-date");
    if (histDateInput) histDateInput.value = historyFilterDate || "";
    updateHistoryDateFilterUI();
    closeHistoryCalendarPopup();
    applyFilters();
}

function updateHistoryDateFilterUI() {
    const textEl = document.getElementById("history-filter-date-text");
    const clearBtn = document.getElementById("history-cal-clear-btn");
    if (textEl) {
        if (!historyFilterDate) {
            textEl.textContent = "Filter Date: All";
            if (clearBtn) clearBtn.classList.remove("active");
        } else {
            const parts = historyFilterDate.split("-");
            const y = parseInt(parts[0], 10);
            const m = parseInt(parts[1], 10) - 1;
            const d = parseInt(parts[2], 10);
            const dateObj = new Date(y, m, d);
            const formatted = isNaN(dateObj.getTime())
                ? historyFilterDate
                : dateObj.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
            textEl.textContent = `Date: ${formatted}`;
            if (clearBtn) clearBtn.classList.add("active");
        }
    }
    renderHistoryCalendar();
}

function clearHistoryDateFilter() {
    historyFilterDate = null;
    const histDateInput = document.getElementById("history-date");
    if (histDateInput) histDateInput.value = "";
    updateHistoryDateFilterUI();
    closeHistoryCalendarPopup();
    applyFilters();
}

function prevHistoryMonth() {
    historyCalMonth--;
    if (historyCalMonth < 0) {
        historyCalMonth = 11;
        historyCalYear--;
    }
    renderHistoryCalendar();
}

function nextHistoryMonth() {
    historyCalMonth++;
    if (historyCalMonth > 11) {
        historyCalMonth = 0;
        historyCalYear++;
    }
    renderHistoryCalendar();
}

function openHistoryCalendarPopup() {
    const popup = document.getElementById("history-calendar-popup");
    const btn = document.getElementById("history-filter-date-btn");
    if (!popup) return;
    closeCalendarPopup();
    closeStatusDropdown();
    closeLimitDropdown();
    popup.hidden = false;
    popup.style.display = "block";
    if (btn) btn.setAttribute("aria-expanded", "true");
    renderHistoryCalendar();
}

function closeHistoryCalendarPopup() {
    const popup = document.getElementById("history-calendar-popup");
    const btn = document.getElementById("history-filter-date-btn");
    if (!popup) return;
    popup.hidden = true;
    popup.style.display = "none";
    if (btn) btn.setAttribute("aria-expanded", "false");
}

function toggleHistoryCalendarPopup() {
    const popup = document.getElementById("history-calendar-popup");
    if (popup && (!popup.hidden && popup.style.display !== "none")) {
        closeHistoryCalendarPopup();
    } else {
        openHistoryCalendarPopup();
    }
}

function openCalendarPopup() {
    const popup = document.getElementById("calendar-popup");
    const btn = document.getElementById("filter-date-btn");
    if (!popup) return;
    closeHistoryCalendarPopup();
    closeStatusDropdown();
    closeLimitDropdown();
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
    closeHistoryCalendarPopup();
    closeCalendarPopup();
    closeLimitDropdown();
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

function openLimitDropdown() {
    const menu = document.getElementById("limit-dropdown-menu");
    const btn = document.getElementById("table-limit-btn");
    if (!menu) return;
    closeHistoryCalendarPopup();
    closeCalendarPopup();
    closeStatusDropdown();
    menu.hidden = false;
    menu.style.display = "flex";
    if (btn) btn.setAttribute("aria-expanded", "true");
}

function closeLimitDropdown() {
    const menu = document.getElementById("limit-dropdown-menu");
    const btn = document.getElementById("table-limit-btn");
    if (!menu) return;
    menu.hidden = true;
    menu.style.display = "none";
    if (btn) btn.setAttribute("aria-expanded", "false");
}

function toggleLimitDropdown() {
    const menu = document.getElementById("limit-dropdown-menu");
    if (menu && (!menu.hidden && menu.style.display !== "none")) {
        closeLimitDropdown();
    } else {
        openLimitDropdown();
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
        const formattedTemp = !isNaN(Number(reading.temperature)) ? Number(reading.temperature).toFixed(2) : reading.temperature;
        const formattedPh = !isNaN(Number(reading.ph)) ? Number(reading.ph).toFixed(2) : reading.ph;
        return `<tr><td>${date.toLocaleDateString()}</td><td>${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</td><td>${formattedTemp} °C</td><td>${formattedPh}</td><td><span class="table-status ${statusClass}">${statusLabel}</span></td></tr>`;
    }).join("");
    document.getElementById("table-empty").hidden = total > 0;

    // 5. Render Pagination controls
    pagination.replaceChildren();
    pagination.hidden = pageCount <= 1;
    if (pageCount <= 1) return;

    const addPageButton = (label, page, options = {}) => {
        const button = document.createElement("button");
        button.type = "button";
        const isNav = Boolean(options.label);
        button.className = "readings-page-button pagination-btn" + (isNav ? " pagination-btn-nav" : " pagination-page-num") + (options.current ? " active" : "");
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

    addPageButton("‹ Prev", historyPage - 1, {
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
            ellipsis.className = "readings-page-ellipsis pagination-ellipsis";
            ellipsis.textContent = page;
            ellipsis.setAttribute("aria-hidden", "true");
            pagination.appendChild(ellipsis);
            return;
        }
        addPageButton(String(page), page, { current: page === historyPage });
    });

    addPageButton("Next ›", historyPage + 1, {
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
        let filename = `aeris_v-historical-${filters.targetDate === 'all' ? 'all-dates' : filters.targetDate}-${filters.status}.${filters.format}`;
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

// Bind Limit selector & custom dropdown
const tableLimitBtn = document.getElementById("table-limit-btn");
if (tableLimitBtn) {
    tableLimitBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleLimitDropdown();
    });
}

const limitMenuItems = document.querySelectorAll("#limit-dropdown-menu .limit-menu-item");
limitMenuItems.forEach((btn) => {
    btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const limit = btn.getAttribute("data-limit");
        selectLimitFilter(limit);
    });
});

const tableLimitSelect = document.getElementById("table-limit-select");
if (tableLimitSelect) {
    tableLimitSelect.addEventListener("change", (e) => {
        selectLimitFilter(e.target.value);
    });
}

// Bind History Filter Date button & Calendar nav
const historyFilterDateBtn = document.getElementById("history-filter-date-btn");
if (historyFilterDateBtn) {
    historyFilterDateBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleHistoryCalendarPopup();
    });
}

const historyCalPrevBtn = document.getElementById("history-cal-prev-month");
if (historyCalPrevBtn) {
    historyCalPrevBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        prevHistoryMonth();
    });
}

const historyCalNextBtn = document.getElementById("history-cal-next-month");
if (historyCalNextBtn) {
    historyCalNextBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        nextHistoryMonth();
    });
}

const historyCalClearBtn = document.getElementById("history-cal-clear-btn");
if (historyCalClearBtn) {
    historyCalClearBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        clearHistoryDateFilter();
    });
}

// Bind Table Date Filter button & Calendar nav
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

const statusMenuItems = document.querySelectorAll("#status-dropdown-menu .status-menu-item");
statusMenuItems.forEach((btn) => {
    btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const status = btn.getAttribute("data-status");
        selectStatusFilter(status);
    });
});

// Close popups/dropdown when clicking outside
document.addEventListener("click", (e) => {
    const histPopup = document.getElementById("history-calendar-popup");
    const histBtn = document.getElementById("history-filter-date-btn");
    if (histPopup && !histPopup.hidden && histPopup.style.display !== "none") {
        if (!histPopup.contains(e.target) && !histBtn?.contains(e.target)) {
            closeHistoryCalendarPopup();
        }
    }

    const tablePopup = document.getElementById("calendar-popup");
    const tableBtn = document.getElementById("filter-date-btn");
    if (tablePopup && !tablePopup.hidden && tablePopup.style.display !== "none") {
        if (!tablePopup.contains(e.target) && !tableBtn?.contains(e.target)) {
            closeCalendarPopup();
        }
    }

    const limitAnchor = document.querySelector(".limit-picker-anchor");
    if (limitAnchor && !limitAnchor.contains(e.target)) {
        closeLimitDropdown();
    }

    const statusAnchor = document.querySelector(".status-picker-anchor");
    if (statusAnchor && !statusAnchor.contains(e.target)) {
        closeStatusDropdown();
    }
});

// Close on Escape key
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        closeHistoryCalendarPopup();
        closeCalendarPopup();
        closeStatusDropdown();
        closeLimitDropdown();
    }
});

// Filter form submit listener (updates Historical Review & Visual Trend)
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
                historyCalYear = latestDate.getFullYear();
                historyCalMonth = latestDate.getMonth();
                calInitialized = true;
            }
        }
        renderCalendar();
        renderHistoryCalendar();
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

closeHistoryCalendarPopup();
closeCalendarPopup();
closeStatusDropdown();
closeLimitDropdown();
updateDeviceTime();
setInterval(updateDeviceTime, 1000);
loadHistory();
setInterval(loadHistory, 10000);
window.addEventListener("resize", () => {
    if (currentFilteredHistory && currentFilteredHistory.length) {
        drawChart(currentFilteredHistory, currentFilteredParameters);
    }
});
