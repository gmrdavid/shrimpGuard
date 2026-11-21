const chartColors = ["#2f6fbd", "#2f8a57"];

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

let currentHistory = [];
let allRawHistory = [];
let trendFilterDate = null; // null = all dates, or 'YYYY-MM-DD'
let trendCalYear = new Date().getFullYear();
let trendCalMonth = new Date().getMonth();
let trendCalendarEventsInitialized = false;

let currentPoints = null;
let hoverIndex = null;
let hoveredParam = null;
let chartEventsInitialized = false;

function getLocalDateKey(d) {
    if (!d || !(d instanceof Date) || isNaN(d.getTime())) return "";
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
}

function getReadingDateKey(reading) {
    if (!reading || !reading.recorded_at) return null;
    const d = parseSafeDate(reading.recorded_at);
    if (d && !isNaN(d.getTime())) {
        return getLocalDateKey(d);
    }
    const match = String(reading.recorded_at).match(/^(\d{4}-\d{2}-\d{2})/);
    return match ? match[1] : null;
}

function formatFriendlyDate(dateStr) {
    if (!dateStr) return "";
    const parts = dateStr.split("-");
    if (parts.length === 3) {
        const d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
        if (!isNaN(d.getTime())) {
            return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
        }
    }
    return dateStr;
}

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
    document.getElementById("monitor-temperature").textContent = !isNaN(tempNum) ? tempNum.toFixed(2) : reading.temperature;
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
    const dateObj = parseSafeDate(reading.recorded_at);
    document.getElementById("monitoring-updated").textContent = dateObj && !isNaN(dateObj.getTime())
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
    let tempDetailText = `Current: ${temp.toFixed(2)} °C · Within ML optimal range (28.00–32.00 °C)`;

    if (temp < tempMin) {
        const diff = tempMin - temp;
        tempDiffPercent = (diff / temp) * 100;
        tempBadgeText = `+${tempDiffPercent.toFixed(1)}% Needed`;
        tempBadgeClass = tempStatus === "Critical" ? "badge-critical" : "badge-warning";
        tempDetailText = `Increase by +${diff.toFixed(2)} °C to reach ML optimal range (28.00–32.00 °C)`;
    } else if (temp > tempMax) {
        const diff = temp - tempMax;
        tempDiffPercent = (diff / temp) * 100;
        tempBadgeText = `-${tempDiffPercent.toFixed(1)}% Needed`;
        tempBadgeClass = tempStatus === "Critical" ? "badge-critical" : "badge-warning";
        tempDetailText = `Decrease by -${diff.toFixed(2)} °C to reach ML optimal range (28.00–32.00 °C)`;
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

function drawTrendChart(history) {
    if (!Array.isArray(history) || history.length === 0) {
        const emptyEl = document.getElementById("chart-empty");
        if (emptyEl) emptyEl.hidden = false;
        return;
    }
    currentHistory = history;

    const emptyEl = document.getElementById("chart-empty");
    if (emptyEl) emptyEl.hidden = true;

    const canvas = document.getElementById("trend-chart");
    if (!canvas) return;
    const context = canvas.getContext("2d");
    const width = canvas.clientWidth || 600;
    const height = canvas.clientHeight || 320;
    const scale = window.devicePixelRatio || 1;

    canvas.width = Math.round(width * scale);
    canvas.height = Math.round(height * scale);
    context.scale(scale, scale);
    context.clearRect(0, 0, width, height);

    const isMobile = width < 520;
    const padding = isMobile
        ? { top: 32, right: 38, bottom: 34, left: 42 }
        : { top: 34, right: 52, bottom: 36, left: 52 };
    const plotWidth = width - padding.left - padding.right;
    const plotHeight = height - padding.top - padding.bottom;

    // Independent scales for Temperature and pH
    const tempVals = history.map((r) => Number(r.temperature)).filter((v) => !isNaN(v));
    const phVals = history.map((r) => Number(r.ph)).filter((v) => !isNaN(v));

    const rawTMin = tempVals.length ? Math.min(...tempVals) : 25;
    const rawTMax = tempVals.length ? Math.max(...tempVals) : 33;
    const rawPMin = phVals.length ? Math.min(...phVals) : 7.0;
    const rawPMax = phVals.length ? Math.max(...phVals) : 8.8;

    // Temperature scale (headroom + min span 3.0°C)
    const tSpan = Math.max(rawTMax - rawTMin, 0.4);
    let tempMin = Math.floor((rawTMin - tSpan * 0.16) * 10) / 10;
    let tempMax = Math.ceil((rawTMax + tSpan * 0.16) * 10) / 10;
    if (tempMax - tempMin < 3.0) {
        const mid = (tempMax + tempMin) / 2;
        tempMin = Math.round((mid - 1.5) * 10) / 10;
        tempMax = Math.round((mid + 1.5) * 10) / 10;
    }
    const tempRange = tempMax - tempMin || 1;

    // pH scale (headroom + min span 0.8 pH)
    const pSpan = Math.max(rawPMax - rawPMin, 0.1);
    let phMin = Math.floor((rawPMin - pSpan * 0.18) * 100) / 100;
    let phMax = Math.ceil((rawPMax + pSpan * 0.18) * 100) / 100;
    if (phMax - phMin < 0.8) {
        const mid = (phMax + phMin) / 2;
        phMin = Math.round((mid - 0.4) * 100) / 100;
        phMax = Math.round((mid + 0.4) * 100) / 100;
    }
    const phRange = phMax - phMin || 1;

    // Subtle Safe-Zone Background Band for Penaeus vannamei (28.0°C - 32.0°C)
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

    // Grid lines & Dual Y-Axis Labels
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

        // Left Axis Label: Temperature in #2f6fbd
        const tempLabel = (tempMax - (tempRange / (gridSteps - 1)) * index).toFixed(1);
        context.fillStyle = "#2f6fbd";
        context.font = isMobile ? "600 10px Inter, -apple-system, sans-serif" : "600 11px Inter, -apple-system, sans-serif";
        context.textAlign = "right";
        context.textBaseline = "middle";
        context.fillText(`${tempLabel}°`, padding.left - 8, y);

        // Right Axis Label: pH in #126b4f
        const phLabel = (phMax - (phRange / (gridSteps - 1)) * index).toFixed(2);
        context.fillStyle = "#126b4f";
        context.textAlign = "left";
        context.textBaseline = "middle";
        context.fillText(phLabel, width - padding.right + 8, y);
    }

    // Axis Headers
    context.font = "700 9.5px Inter, -apple-system, sans-serif";
    context.textBaseline = "bottom";
    // Left Axis Header
    context.fillStyle = "#2f6fbd";
    context.textAlign = "right";
    context.fillText("°C (TEMP)", padding.left - 6, padding.top - 8);
    // Right Axis Header
    context.fillStyle = "#126b4f";
    context.textAlign = "left";
    context.fillText("pH LEVEL", width - padding.right + 6, padding.top - 8);

    // Compute coordinate points per series
    const tempPoints = history.map((reading, index) => {
        const val = Number(reading.temperature);
        const x = history.length === 1
            ? padding.left + plotWidth / 2
            : padding.left + (index / (history.length - 1)) * plotWidth;
        const y = padding.top + (1 - (val - tempMin) / tempRange) * plotHeight;
        return { x, y, value: val, key: "temperature", reading, index };
    });

    const phPoints = history.map((reading, index) => {
        const val = Number(reading.ph);
        const x = history.length === 1
            ? padding.left + plotWidth / 2
            : padding.left + (index / (history.length - 1)) * plotWidth;
        const y = padding.top + (1 - (val - phMin) / phRange) * plotHeight;
        return { x, y, value: val, key: "ph", reading, index };
    });

    currentPoints = [tempPoints, phPoints];

    // X-Axis Baseline
    context.beginPath();
    context.strokeStyle = "#d4dfd8";
    context.lineWidth = 1;
    context.moveTo(padding.left, height - padding.bottom);
    context.lineTo(width - padding.right, height - padding.bottom);
    context.stroke();

    // Time Ticks and Labels along X-Axis
    if (history.length > 0) {
        const maxTicks = isMobile ? 3 : (width < 768 ? 4 : 6);
        const numTicks = Math.min(maxTicks, history.length);
        const tickStep = (history.length - 1) / (numTicks - 1 || 1);
        context.fillStyle = "#718277";
        context.font = "600 10.5px Inter, -apple-system, sans-serif";
        context.textAlign = "center";
        context.textBaseline = "top";

        for (let i = 0; i < numTicks; i++) {
            const idx = Math.round(i * tickStep);
            const pt = tempPoints[idx];
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

    // 1. Draw Temperature Spline & Translucent Area Gradient
    if (tempPoints.length > 0) {
        context.save();
        const tempGrad = context.createLinearGradient(0, padding.top, 0, height - padding.bottom);
        tempGrad.addColorStop(0, "rgba(47, 111, 189, 0.18)");
        tempGrad.addColorStop(0.7, "rgba(47, 111, 189, 0.05)");
        tempGrad.addColorStop(1, "rgba(47, 111, 189, 0.00)");

        context.beginPath();
        drawSmoothSpline(context, tempPoints, 0.18);
        context.lineTo(tempPoints[tempPoints.length - 1].x, height - padding.bottom);
        context.lineTo(tempPoints[0].x, height - padding.bottom);
        context.closePath();
        context.fillStyle = tempGrad;
        context.fill();
        context.restore();

        context.save();
        context.beginPath();
        drawSmoothSpline(context, tempPoints, 0.18);
        context.strokeStyle = "#2f6fbd";
        context.lineWidth = 2.75;
        context.lineCap = "round";
        context.lineJoin = "round";
        context.stroke();
        context.restore();
    }

    // 2. Draw pH Spline & Translucent Area Gradient
    if (phPoints.length > 0) {
        context.save();
        const phGrad = context.createLinearGradient(0, padding.top, 0, height - padding.bottom);
        phGrad.addColorStop(0, "rgba(18, 107, 79, 0.16)");
        phGrad.addColorStop(0.7, "rgba(18, 107, 79, 0.04)");
        phGrad.addColorStop(1, "rgba(18, 107, 79, 0.00)");

        context.beginPath();
        drawSmoothSpline(context, phPoints, 0.18);
        context.lineTo(phPoints[phPoints.length - 1].x, height - padding.bottom);
        context.lineTo(phPoints[0].x, height - padding.bottom);
        context.closePath();
        context.fillStyle = phGrad;
        context.fill();
        context.restore();

        context.save();
        context.beginPath();
        drawSmoothSpline(context, phPoints, 0.18);
        context.strokeStyle = "#126b4f";
        context.lineWidth = 2.75;
        context.lineCap = "round";
        context.lineJoin = "round";
        context.stroke();
        context.restore();
    }

    // Interactive Vertical Laser Scrubber & Floating Pill
    if (hoverIndex !== null && hoverIndex >= 0 && hoverIndex < history.length) {
        const hoverX = tempPoints[hoverIndex].x;
        context.save();
        context.beginPath();
        context.setLineDash([3, 3]);
        context.strokeStyle = "rgba(18, 107, 79, 0.55)";
        context.lineWidth = 1.5;
        context.moveTo(hoverX, padding.top - 6);
        context.lineTo(hoverX, height - padding.bottom + 6);
        context.stroke();

        const rDate = parseSafeDate(history[hoverIndex] && history[hoverIndex].recorded_at);
        const pillText = rDate ? rDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : `#${hoverIndex + 1}`;
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

    // Render Dual-Layer High-Definition Data Points
    [
        { pts: tempPoints, color: "#2f6fbd", halo: "rgba(47, 111, 189, 0.22)", key: "temperature" },
        { pts: phPoints, color: "#126b4f", halo: "rgba(18, 107, 79, 0.22)", key: "ph" }
    ].forEach(({ pts, color, halo, key }) => {
        pts.forEach((pt, index) => {
            const isHovered = hoverIndex === index;
            const isFocused = isHovered && (hoveredParam === key || hoveredParam === null);

            if (isHovered) {
                // Ambient glow
                context.beginPath();
                context.arc(pt.x, pt.y, isFocused ? 11 : 8, 0, Math.PI * 2);
                context.fillStyle = halo;
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

    // Update Live Legend Values
    const activeReading = (hoverIndex !== null && history[hoverIndex]) ? history[hoverIndex] : (history.length > 0 ? history[history.length - 1] : null);
    const tempBadge = document.getElementById("monitoring-legend-temp-val");
    const phBadge = document.getElementById("monitoring-legend-ph-val");
    if (tempBadge) {
        tempBadge.textContent = activeReading && activeReading.temperature != null ? `${Number(activeReading.temperature).toFixed(1)} °C` : "-- °C";
    }
    if (phBadge) {
        phBadge.textContent = activeReading && activeReading.ph != null ? `${Number(activeReading.ph).toFixed(2)}` : "--";
    }
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
                    <span class="tooltip-param-value">${tempVal.toFixed(2)} °C</span>
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
    const isMobile = width < 520;
    const padding = isMobile
        ? { top: 32, right: 38, bottom: 34, left: 42 }
        : { top: 34, right: 52, bottom: 36, left: 52 };

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
    const summaryText = recommendation.summary || recommendation.recommendation_summary || recommendation.recommendation || "Maintain standard pond monitoring protocols.";
    const provider = recommendation.source || "Google Gemini API";
    const species = recommendation.species || "Penaeus vannamei (Pacific White Shrimp)";

    let solutionsList = [];
    if (Array.isArray(recommendation.actionable_solutions) && recommendation.actionable_solutions.length > 0) {
        solutionsList = recommendation.actionable_solutions.slice(0, 3);
    } else if (recommendation.actionable_solution || recommendation.actionable_summary) {
        solutionsList = [recommendation.actionable_summary || recommendation.actionable_solution];
    }

    let solutionsHtml = "";
    if (solutionsList.length > 0) {
        solutionsHtml = `
            <div class="rec-action-panel">
                <div class="rec-action-header">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-check-circle"></use></svg>
                    <span>SUMMARY ACTION DIRECTIVES &bull; PENAEUS VANNAMEI</span>
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
                    <span class="rec-summary-tag">Summary View</span>
                </div>
                <div class="rec-provider-tag">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-sparkles"></use></svg>
                    <span>${provider}</span>
                </div>
            </div>

            <div class="rec-content-section">
                <h4 class="rec-content-title">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                    Gemini API Recommendation (Summary)
                </h4>
                <p class="rec-text-body">${summaryText}</p>
            </div>

            ${solutionsHtml}

            <!-- DIRECT LINK TO DETAILED RECOMMENDATIONS WEBPAGE -->
            <div class="monitoring-rec-footer-card">
                <div class="rec-footer-info">
                    <span class="rec-footer-heading">Need In-Depth Field Protocols &amp; 24-Hour Horizon Analysis?</span>
                    <p class="rec-footer-sub">Access complete chemical dosages, step-by-step checklists, and ML trajectory graphs on the dedicated AI Recommendation page.</p>
                </div>
                <a href="/recommendations" class="btn-view-detailed-recs">
                    <span>View Detailed AI Recommendations &rarr;</span>
                </a>
            </div>
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

const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
];

function getTrendDatesWithReadingsSet() {
    const set = new Set();
    if (Array.isArray(allRawHistory)) {
        allRawHistory.forEach((r) => {
            const dateKey = getReadingDateKey(r);
            if (dateKey) set.add(dateKey);
        });
    }
    return set;
}

function renderTrendCalendar() {
    const titleEl = document.getElementById("trend-cal-month-title");
    const gridEl = document.getElementById("trend-calendar-days-grid");
    if (!titleEl || !gridEl) return;

    titleEl.textContent = `${monthNames[trendCalMonth]} ${trendCalYear}`;
    gridEl.innerHTML = "";

    const datesWithReadings = getTrendDatesWithReadingsSet();

    const firstDayIndex = new Date(trendCalYear, trendCalMonth, 1).getDay();
    const totalDays = new Date(trendCalYear, trendCalMonth + 1, 0).getDate();
    const prevMonthDays = new Date(trendCalYear, trendCalMonth, 0).getDate();

    for (let i = firstDayIndex - 1; i >= 0; i--) {
        const filler = document.createElement("div");
        filler.className = "cal-day cal-day-empty";
        filler.textContent = String(prevMonthDays - i);
        gridEl.appendChild(filler);
    }

    for (let day = 1; day <= totalDays; day++) {
        const dayStr = `${trendCalYear}-${String(trendCalMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
        const hasData = datesWithReadings.has(dayStr);
        const isSelected = (trendFilterDate === dayStr);

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
            selectTrendDateFilter(dayStr);
        });

        gridEl.appendChild(dayBtn);
    }
}

function selectTrendDateFilter(dateStr) {
    if (trendFilterDate === dateStr) {
        trendFilterDate = null;
    } else {
        trendFilterDate = dateStr;
    }
    updateTrendDateFilterUI();
    closeTrendCalendarPopup();
    applyTrendDateFilter();
}

function updateTrendDateFilterUI() {
    const textEl = document.getElementById("trend-filter-date-text");
    const clearBtn = document.getElementById("trend-cal-clear-btn");
    if (textEl) {
        if (!trendFilterDate) {
            textEl.textContent = "Filter Date: All";
            if (clearBtn) clearBtn.classList.remove("active");
        } else {
            textEl.textContent = `Date: ${formatFriendlyDate(trendFilterDate)}`;
            if (clearBtn) clearBtn.classList.add("active");
        }
    }
    renderTrendCalendar();
}

function clearTrendDateFilter() {
    trendFilterDate = null;
    updateTrendDateFilterUI();
    closeTrendCalendarPopup();
    applyTrendDateFilter();
}

function prevTrendMonth() {
    trendCalMonth--;
    if (trendCalMonth < 0) {
        trendCalMonth = 11;
        trendCalYear--;
    }
    renderTrendCalendar();
}

function nextTrendMonth() {
    trendCalMonth++;
    if (trendCalMonth > 11) {
        trendCalMonth = 0;
        trendCalYear++;
    }
    renderTrendCalendar();
}

function openTrendCalendarPopup() {
    const popup = document.getElementById("trend-calendar-popup");
    const btn = document.getElementById("trend-filter-date-btn");
    if (!popup) return;
    popup.hidden = false;
    popup.style.display = "block";
    if (btn) btn.setAttribute("aria-expanded", "true");
    renderTrendCalendar();
}

function closeTrendCalendarPopup() {
    const popup = document.getElementById("trend-calendar-popup");
    const btn = document.getElementById("trend-filter-date-btn");
    if (!popup) return;
    popup.hidden = true;
    popup.style.display = "none";
    if (btn) btn.setAttribute("aria-expanded", "false");
}

function toggleTrendCalendarPopup() {
    const popup = document.getElementById("trend-calendar-popup");
    if (popup && (!popup.hidden && popup.style.display !== "none")) {
        closeTrendCalendarPopup();
    } else {
        openTrendCalendarPopup();
    }
}

function initTrendCalendarEvents() {
    if (trendCalendarEventsInitialized) return;

    const filterBtn = document.getElementById("trend-filter-date-btn");
    if (filterBtn) {
        filterBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            toggleTrendCalendarPopup();
        });
    }

    const prevBtn = document.getElementById("trend-cal-prev-month");
    if (prevBtn) {
        prevBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            prevTrendMonth();
        });
    }

    const nextBtn = document.getElementById("trend-cal-next-month");
    if (nextBtn) {
        nextBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            nextTrendMonth();
        });
    }

    const clearBtn = document.getElementById("trend-cal-clear-btn");
    if (clearBtn) {
        clearBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            clearTrendDateFilter();
        });
    }

    // Close on outside click
    document.addEventListener("click", (e) => {
        const popup = document.getElementById("trend-calendar-popup");
        const btn = document.getElementById("trend-filter-date-btn");
        if (!popup || popup.hidden || popup.style.display === "none") return;
        if (!popup.contains(e.target) && !btn?.contains(e.target)) {
            closeTrendCalendarPopup();
        }
    });

    // Close on Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeTrendCalendarPopup();
        }
    });

    trendCalendarEventsInitialized = true;
}

function applyTrendDateFilter() {
    const emptyEl = document.getElementById("chart-empty");
    const countEl = document.getElementById("trend-count");

    if (!Array.isArray(allRawHistory) || allRawHistory.length === 0) {
        currentHistory = [];
        const canvas = document.getElementById("trend-chart");
        if (canvas) {
            const ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
        if (emptyEl) {
            emptyEl.hidden = false;
            emptyEl.textContent = "Submit at least one dashboard reading to see the trend graph.";
        }
        if (countEl) countEl.textContent = "No readings yet";
        return;
    }

    let filtered = [];
    if (!trendFilterDate) {
        filtered = [...allRawHistory];
    } else {
        filtered = allRawHistory.filter((r) => getReadingDateKey(r) === trendFilterDate);
    }

    if (countEl) {
        countEl.textContent = `${filtered.length} reading${filtered.length === 1 ? "" : "s"}`;
    }

    // Empty state handling
    if (filtered.length === 0) {
        if (emptyEl) {
            emptyEl.hidden = false;
            emptyEl.textContent = `No telemetry readings recorded on ${formatFriendlyDate(trendFilterDate)}.`;
        }
        const canvas = document.getElementById("trend-chart");
        if (canvas) {
            const ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
        currentHistory = [];
        return;
    }

    if (emptyEl) emptyEl.hidden = true;

    initChartEvents();
    drawTrendChart(filtered);
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
            allRawHistory = history;
            initTrendCalendarEvents();
            const calPopup = document.getElementById("trend-calendar-popup");
            if (calPopup && !calPopup.hidden && calPopup.style.display !== "none") {
                renderTrendCalendar();
            }
            applyTrendDateFilter();
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
let monitoringPollTimer = null;
function restartMonitoringPolling() {
    if (monitoringPollTimer) clearInterval(monitoringPollTimer);
    const adaptive = window.AerisVAdaptive || window.ShrimpGuardAdaptive;
    const interval = adaptive && adaptive.getPollInterval
        ? adaptive.getPollInterval(5000, 25000)
        : 5000;
    monitoringPollTimer = setInterval(loadMonitoringData, interval);
}
restartMonitoringPolling();
window.addEventListener("aeris_v:preferences-changed", restartMonitoringPolling);
window.addEventListener("shrimpguard:preferences-changed", restartMonitoringPolling);
