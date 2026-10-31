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

function getTemperatureStatus(temperature, reading) {
    if (reading && reading.temperature_status) {
        const lvl = reading.temperature_status.toLowerCase();
        return { label: reading.temperature_status, level: lvl, badgeClass: `status-${lvl}` };
    }
    const temp = Number(temperature);
    // Evaluated strictly based on the trained DecisionTreeClassifier ML model (neutral pH 8.00):
    // Critical: <= 25.01 or > 33.50
    // Warning: (25.01, 28.0) or (32.0, 33.50]
    // Optimal: [28.0, 32.0]
    if (temp <= 25.01 || temp > 33.50) {
        return { label: "Critical", level: "critical", badgeClass: "status-critical" };
    }
    if (temp < 28.0 || temp > 32.0) {
        return { label: "Warning", level: "warning", badgeClass: "status-warning" };
    }
    return { label: "Optimal", level: "optimal", badgeClass: "status-optimal" };
}

function getPhStatus(phLevel, reading) {
    if (reading && reading.ph_status) {
        const lvl = reading.ph_status.toLowerCase();
        return { label: reading.ph_status, level: lvl, badgeClass: `status-${lvl}` };
    }
    const ph = Number(phLevel);
    // Evaluated strictly based on the trained DecisionTreeClassifier ML model (neutral Temp 30.0 °C):
    // Critical: <= 6.49 or > 9.01
    // Warning: (6.49, 7.50) or (8.50, 9.01]
    // Optimal: [7.50, 8.50]
    if (ph <= 6.49 || ph > 9.01) {
        return { label: "Critical", level: "critical", badgeClass: "status-critical" };
    }
    if (ph < 7.50 || ph > 8.50) {
        return { label: "Warning", level: "warning", badgeClass: "status-warning" };
    }
    return { label: "Optimal", level: "optimal", badgeClass: "status-optimal" };
}

function updateSummary(reading) {
    const tempNum = Number(reading.temperature);
    const phNum = Number(reading.ph);
    document.getElementById("monitor-temperature").textContent = !isNaN(tempNum) ? tempNum.toFixed(1) : reading.temperature;
    document.getElementById("monitor-ph").textContent = !isNaN(phNum) ? phNum.toFixed(2) : reading.ph;

    // ML Parameter Statuses
    const tStat = reading.temperature_status || getTemperatureStatus(tempNum, reading).label;
    const pStat = reading.ph_status || getPhStatus(phNum, reading).label;

    const tempStatusEl = document.getElementById("monitor-temp-status");
    if (tempStatusEl) {
        tempStatusEl.textContent = tStat;
        tempStatusEl.className = `metric-status status-${tStat.toLowerCase()}`;
    }
    const phStatusEl = document.getElementById("monitor-ph-status");
    if (phStatusEl) {
        phStatusEl.textContent = pStat;
        phStatusEl.className = `metric-status status-${pStat.toLowerCase()}`;
    }

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
    const dateObj = reading.recorded_at ? new Date(reading.recorded_at) : null;
    document.getElementById("monitoring-updated").textContent = dateObj && !isNaN(dateObj)
        ? "Last updated " + dateObj.toLocaleString([], { dateStyle: "medium", timeStyle: "medium" })
        : "Last updated recently";
    document.getElementById("monitoring-demo-note").hidden = reading.status !== "Demo";
}

function calculateWQI(data) {
    if (!data) return;

    // 1. Direct ML Analysis rendering if pre-calculated by backend
    if (data.temp_adjustment && data.ph_adjustment && data.wqi_score !== undefined) {
        const accuracyScore = Number(data.wqi_score);
        const statusLabel = data.wqi_status || (accuracyScore >= 90 ? "OPTIMAL QUALITY" : (accuracyScore >= 70 ? "WARNING CONDITION" : "CRITICAL CONDITION"));
        const statusTheme = data.wqi_theme || (accuracyScore >= 90 ? "optimal" : (accuracyScore >= 70 ? "warning" : "critical"));

        const tempAdj = data.temp_adjustment;
        const tempPercentEl = document.getElementById("temp-norm-percent");
        if (tempPercentEl) tempPercentEl.textContent = tempAdj.percent_text || "0.0%";
        const tempBadgeEl = document.getElementById("temp-norm-badge");
        if (tempBadgeEl) {
            tempBadgeEl.textContent = tempAdj.badge_text || "Normal";
            tempBadgeEl.className = `wqi-metric-badge ${tempAdj.badge_class || "badge-normal"}`;
        }
        const tempDetailEl = document.getElementById("temp-norm-detail");
        if (tempDetailEl) tempDetailEl.textContent = tempAdj.detail_text;

        const phAdj = data.ph_adjustment;
        const phPercentEl = document.getElementById("ph-norm-percent");
        if (phPercentEl) phPercentEl.textContent = phAdj.percent_text || "0.0%";
        const phBadgeEl = document.getElementById("ph-norm-badge");
        if (phBadgeEl) {
            phBadgeEl.textContent = phAdj.badge_text || "Normal";
            phBadgeEl.className = `wqi-metric-badge ${phAdj.badge_class || "badge-normal"}`;
        }
        const phDetailEl = document.getElementById("ph-norm-detail");
        if (phDetailEl) phDetailEl.textContent = phAdj.detail_text;

        const accuracyPercentEl = document.getElementById("wqi-accuracy-percent");
        if (accuracyPercentEl) accuracyPercentEl.textContent = `${accuracyScore}%`;
        const accuracyBadgeEl = document.getElementById("wqi-accuracy-badge");
        if (accuracyBadgeEl) {
            accuracyBadgeEl.textContent = statusLabel;
            accuracyBadgeEl.className = `wqi-metric-badge badge-${statusTheme}`;
        }
        return;
    }

    // 2. Dynamic ML evaluation fallback
    const temp = Number(data.temperature);
    const ph = Number(data.ph);
    if (isNaN(temp) || isNaN(ph)) return;

    const tempMin = 28.0;
    const tempMax = 32.0;
    const phMin = 7.50;
    const phMax = 8.50;

    let tempStatus = "Optimal";
    if (temp <= 25.01 || temp > 33.50) tempStatus = "Critical";
    else if (temp < tempMin || temp > tempMax) tempStatus = "Warning";

    let phStatus = "Optimal";
    if (ph <= 6.49 || ph > 9.01) phStatus = "Critical";
    else if (ph < phMin || ph > phMax) phStatus = "Warning";

    let overallStatus = "Optimal";
    if (tempStatus === "Critical" || phStatus === "Critical") overallStatus = "Critical";
    else if (tempStatus === "Warning" || phStatus === "Warning") overallStatus = "Warning";

    let tempDiffPercent = 0.0;
    let tempBadgeText = "Normal";
    let tempBadgeClass = "badge-normal";
    let tempDetailText = `Current: ${temp.toFixed(1)} °C · Within ML optimal range (28.0–32.0 °C)`;

    if (temp < tempMin) {
        const diff = tempMin - temp;
        tempDiffPercent = (diff / temp) * 100;
        tempBadgeText = `+${tempDiffPercent.toFixed(1)}% Needed`;
        tempBadgeClass = tempStatus === "Critical" ? "badge-critical" : "badge-warning";
        tempDetailText = `Increase by +${diff.toFixed(1)} °C to reach ML optimal range (28.0–32.0 °C)`;
    } else if (temp > tempMax) {
        const diff = temp - tempMax;
        tempDiffPercent = (diff / temp) * 100;
        tempBadgeText = `-${tempDiffPercent.toFixed(1)}% Needed`;
        tempBadgeClass = tempStatus === "Critical" ? "badge-critical" : "badge-warning";
        tempDetailText = `Decrease by -${diff.toFixed(1)} °C to reach ML optimal range (28.0–32.0 °C)`;
    }

    const tempPercentEl = document.getElementById("temp-norm-percent");
    if (tempPercentEl) tempPercentEl.textContent = tempDiffPercent === 0 ? "0.0%" : (temp < tempMin ? `+${tempDiffPercent.toFixed(1)}%` : `-${tempDiffPercent.toFixed(1)}%`);
    const tempBadgeEl = document.getElementById("temp-norm-badge");
    if (tempBadgeEl) {
        tempBadgeEl.textContent = tempBadgeText;
        tempBadgeEl.className = `wqi-metric-badge ${tempBadgeClass}`;
    }
    const tempDetailEl = document.getElementById("temp-norm-detail");
    if (tempDetailEl) tempDetailEl.textContent = tempDetailText;

    let phDiffPercent = 0.0;
    let phBadgeText = "Normal";
    let phBadgeClass = "badge-normal";
    let phDetailText = `Current: ${ph.toFixed(2)} · Within ML optimal range (7.50–8.50)`;

    if (ph < phMin) {
        const diff = phMin - ph;
        phDiffPercent = (diff / ph) * 100;
        phBadgeText = `+${phDiffPercent.toFixed(1)}% Needed`;
        phBadgeClass = phStatus === "Critical" ? "badge-critical" : "badge-warning";
        phDetailText = `Increase by +${diff.toFixed(2)} to reach ML optimal range (7.50–8.50)`;
    } else if (ph > phMax) {
        const diff = ph - phMax;
        phDiffPercent = (diff / ph) * 100;
        phBadgeText = `-${phDiffPercent.toFixed(1)}% Needed`;
        phBadgeClass = phStatus === "Critical" ? "badge-critical" : "badge-warning";
        phDetailText = `Decrease by -${diff.toFixed(2)} to reach ML optimal range (7.50–8.50)`;
    }

    const phPercentEl = document.getElementById("ph-norm-percent");
    if (phPercentEl) phPercentEl.textContent = phDiffPercent === 0 ? "0.0%" : (ph < phMin ? `+${phDiffPercent.toFixed(1)}%` : `-${phDiffPercent.toFixed(1)}%`);
    const phBadgeEl = document.getElementById("ph-norm-badge");
    if (phBadgeEl) {
        phBadgeEl.textContent = phBadgeText;
        phBadgeEl.className = `wqi-metric-badge ${phBadgeClass}`;
    }
    const phDetailEl = document.getElementById("ph-norm-detail");
    if (phDetailEl) phDetailEl.textContent = phDetailText;

    let wqiScore = 100;
    if (overallStatus === "Optimal") {
        const tPen = Math.min(5, (Math.abs(temp - 30.0) / 2.0) * 5);
        const pPen = Math.min(5, (Math.abs(ph - 8.0) / 0.5) * 5);
        wqiScore = Math.max(90, Math.min(100, Math.round(100 - tPen - pPen)));
    } else if (overallStatus === "Warning") {
        const tPen = tempStatus === "Warning" ? 12 : 0;
        const pPen = phStatus === "Warning" ? 12 : 0;
        wqiScore = Math.max(70, Math.min(89, Math.round(100 - tPen - pPen)));
    } else {
        const tPen = tempStatus === "Critical" ? 25 : (tempStatus === "Warning" ? 12 : 0);
        const pPen = phStatus === "Critical" ? 25 : (phStatus === "Warning" ? 12 : 0);
        wqiScore = Math.min(69, Math.max(0, Math.round(100 - tPen - pPen)));
    }

    const statusLabel = overallStatus === "Optimal" ? "OPTIMAL QUALITY" : (overallStatus === "Warning" ? "WARNING CONDITION" : "CRITICAL CONDITION");
    const statusTheme = overallStatus.toLowerCase();

    const accuracyPercentEl = document.getElementById("wqi-accuracy-percent");
    if (accuracyPercentEl) accuracyPercentEl.textContent = `${wqiScore}%`;
    const accuracyBadgeEl = document.getElementById("wqi-accuracy-badge");
    if (accuracyBadgeEl) {
        accuracyBadgeEl.textContent = statusLabel;
        accuracyBadgeEl.className = `wqi-metric-badge badge-${statusTheme}`;
    }
}

function resetWQI() {
    const tempPercentEl = document.getElementById("temp-norm-percent");
    if (tempPercentEl) tempPercentEl.textContent = "0.0%";
    const tempBadgeEl = document.getElementById("temp-norm-badge");
    if (tempBadgeEl) {
        tempBadgeEl.textContent = "Normal";
        tempBadgeEl.className = "wqi-metric-badge badge-normal";
    }
    const tempDetailEl = document.getElementById("temp-norm-detail");
    if (tempDetailEl) tempDetailEl.textContent = "Optimal range: 28.0–32.0 °C";

    const phPercentEl = document.getElementById("ph-norm-percent");
    if (phPercentEl) phPercentEl.textContent = "0.0%";
    const phBadgeEl = document.getElementById("ph-norm-badge");
    if (phBadgeEl) {
        phBadgeEl.textContent = "Normal";
        phBadgeEl.className = "wqi-metric-badge badge-normal";
    }
    const phDetailEl = document.getElementById("ph-norm-detail");
    if (phDetailEl) phDetailEl.textContent = "Optimal range: 7.50–8.50 pH";

    const accuracyPercentEl = document.getElementById("wqi-accuracy-percent");
    if (accuracyPercentEl) accuracyPercentEl.textContent = "--";
    const accuracyBadgeEl = document.getElementById("wqi-accuracy-badge");
    if (accuracyBadgeEl) {
        accuracyBadgeEl.textContent = "Assessment";
        accuracyBadgeEl.className = "wqi-metric-badge badge-normal";
    }
    const accuracyDetailEl = document.getElementById("wqi-accuracy-detail");
    if (accuracyDetailEl) accuracyDetailEl.textContent = "Water quality assessment accuracy";
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
    const container = document.getElementById("monitoring-recommendations");
    if (!container) return;

    if (!reading) {
        container.innerHTML = `
            <div class="rec-empty-box">
                <p>No reading available yet. Submit dashboard readings to receive AI recommendations for <em>Penaeus vannamei</em>.</p>
            </div>
        `;
        return;
    }

    if (!recommendation) {
        container.innerHTML = `
            <div class="rec-error-box">
                <p>AI recommendations are temporarily unavailable. Please verify your connection.</p>
            </div>
        `;
        return;
    }

    const classification = recommendation.classification || "Assessment";
    const badgeClass = classification.toLowerCase();
    const recommendationText = recommendation.recommendation || "Maintain standard pond monitoring protocols.";
    const provider = recommendation.source || "OpenAI API";
    const species = recommendation.species || "Penaeus vannamei (Pacific White Shrimp)";

    let solutionsList = [];
    if (Array.isArray(recommendation.actionable_solutions) && recommendation.actionable_solutions.length > 0) {
        solutionsList = recommendation.actionable_solutions;
    } else if (recommendation.actionable_solution) {
        solutionsList = [recommendation.actionable_solution];
    }

    let solutionsHtml = "";
    if (solutionsList.length > 0) {
        solutionsHtml = `
            <div class="rec-action-panel">
                <div class="rec-action-header">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-check-circle"></use></svg>
                    <span>ACTIONABLE SOLUTIONS FOR PENAEUS VANNAMEI</span>
                </div>
                <ul class="rec-action-items">
                    ${solutionsList.map((step) => `
                        <li class="rec-action-item">
                            <span class="action-check-badge">✓</span>
                            <span class="action-step-text">${step}</span>
                        </li>
                    `).join("")}
                </ul>
            </div>
        `;
    }

    container.innerHTML = `
        <div class="rec-card-container">
            <div class="rec-header-row">
                <div class="rec-badge-wrap">
                    <span class="table-status ${badgeClass}">${classification} Status</span>
                    <span class="rec-species-chip">Target: <em>${species}</em></span>
                </div>
                <span class="rec-source-badge">${provider}</span>
            </div>

            <div class="rec-content-section">
                <h4 class="rec-content-title">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                    Biological Assessment &amp; Recommendation
                </h4>
                <p class="rec-text-body">${recommendationText}</p>
            </div>

            ${solutionsHtml}
        </div>
    `;
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

            // Ensure history is chronologically ordered (oldest to newest for trajectory chart)
            history.sort((a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime());

            // Determine the true latest reading between /api/readings/latest and the newest history point
            const newestFromHistory = history.length > 0 ? history[history.length - 1] : null;
            let trueLatest = latest;
            if (!trueLatest && newestFromHistory) {
                trueLatest = newestFromHistory;
            } else if (trueLatest && newestFromHistory) {
                const latestTime = new Date(trueLatest.recorded_at).getTime();
                const historyTime = new Date(newestFromHistory.recorded_at).getTime();
                if (historyTime > latestTime) {
                    trueLatest = newestFromHistory;
                }
            }

            if (!trueLatest || history.length === 0) {
                emptyMessage.hidden = false;
                document.getElementById("trend-count").textContent = "No readings yet";
                updateRecommendations(null);
                document.getElementById("monitor-temperature").textContent = "--";
                document.getElementById("monitor-ph").textContent = "--";
                document.getElementById("monitoring-status").textContent = "Waiting for a reading";
                document.getElementById("monitoring-updated").textContent =
                    "No sensor readings are saved yet.";
                document.getElementById("monitoring-demo-note").hidden = true;
                resetWQI();
                handlePointerLeave();
                return;
            }

            emptyMessage.hidden = true;
            updateSummary(trueLatest);
            calculateWQI(trueLatest);
            loadRecommendation(trueLatest).then(rec => {
                updateRecommendations(trueLatest, rec);
            }).catch(err => {
                console.error("Unable to load AI recommendations:", err);
                updateRecommendations(trueLatest, null);
            });
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
        resetWQI();
        handlePointerLeave();
    }
}

// Entrypoint initialization
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
