# Update static/js/calculators.js and static/css/style.css

with open("static/js/calculators.js", "r", encoding="utf-8") as f:
    js_content = f.read()

# 1. Add growthChartHoveredParam
old_decl = """    let selectedGrowthMetrics = new Set(["sr", "fabw", "adwg", "sgr", "fb", "fcr", "k"]);
    let growthChartMode = "trajectory"; // "trajectory" or "history"
    let currentGrowthChartData = [];
    let currentGrowthChartPoints = {};
    let growthChartHoverIndex = null;
    let growthHistoryRecords = [];

    // DOM Elements for Graph Modal
    const growthGraphModal = document.getElementById("growth-trend-graph-modal");
    const closeGrowthGraphModalBtn = document.getElementById("close-growth-graph-modal");
    const closeGrowthGraphActionBtn = document.getElementById("close-growth-graph-action-btn");
    const btnOpenGrowthChart = document.getElementById("btn-open-growth-chart");
    const btnOpenGrowthChartTop = document.getElementById("btn-open-growth-chart-top");"""

new_decl = """    let selectedGrowthMetrics = new Set(["sr", "fabw", "adwg", "sgr", "fb", "fcr", "k"]);
    let growthChartMode = "trajectory"; // "trajectory" or "history"
    let currentGrowthChartData = [];
    let currentGrowthChartPoints = {};
    let growthChartHoverIndex = null;
    let growthChartHoveredParam = null;
    let growthHistoryRecords = [];

    // DOM Elements for Graph Modal
    const growthGraphModal = document.getElementById("growth-trend-graph-modal");
    const closeGrowthGraphModalBtn = document.getElementById("close-growth-graph-modal");
    const closeGrowthGraphActionBtn = document.getElementById("close-growth-graph-action-btn");
    const btnOpenGrowthChart = document.getElementById("btn-open-growth-chart");"""

if old_decl in js_content:
    js_content = js_content.replace(old_decl, new_decl)
    print("Replaced declaration in calculators.js")
else:
    print("WARNING: old_decl not found!")

# 2. Update dots in renderGrowthChart
old_dots = """            // Circular points with hover halo
            pts.forEach((pt, idx) => {
                const isHovered = growthChartHoverIndex === idx;

                if (isHovered) {
                    context.beginPath();
                    context.arc(pt.x, pt.y, 9.5, 0, Math.PI * 2);
                    context.fillStyle = conf.glow;
                    context.fill();
                }

                context.beginPath();
                context.arc(pt.x, pt.y, isHovered ? 5.5 : 3.5, 0, Math.PI * 2);
                context.fillStyle = isHovered ? "#ffffff" : conf.color;
                context.fill();
                context.strokeStyle = conf.color;
                context.lineWidth = isHovered ? 2.5 : 1.5;
                context.stroke();
            });"""

new_dots = """            // Circular points with hover halo and focused item glow
            pts.forEach((pt, idx) => {
                const isHovered = growthChartHoverIndex === idx;
                const isFocused = isHovered && (growthChartHoveredParam === key || growthChartHoveredParam === null);

                // Halo glow for hovered point
                if (isHovered) {
                    context.beginPath();
                    context.arc(pt.x, pt.y, isFocused ? 11 : 7, 0, Math.PI * 2);
                    context.fillStyle = conf.glow;
                    context.fill();
                }

                // Outer point ring & dot
                context.beginPath();
                context.arc(pt.x, pt.y, isHovered ? (isFocused ? 5.5 : 4.5) : 3.5, 0, Math.PI * 2);
                context.fillStyle = isHovered ? "#ffffff" : conf.color;
                context.fill();
                context.strokeStyle = conf.color;
                context.lineWidth = isHovered ? 2.5 : 1.5;
                context.stroke();
            });"""

if old_dots in js_content:
    js_content = js_content.replace(old_dots, new_dots)
    print("Replaced dots in renderGrowthChart")
else:
    print("WARNING: old_dots not found!")

# 3. Update renderGrowthTooltip
old_tooltip = """    function renderGrowthTooltip(index, pointX, mouseY, containerWidth, containerHeight) {
        if (!growthTooltip) return;
        const dataItem = currentGrowthChartData[index];
        if (!dataItem) return;

        const activeKeys = Array.from(selectedGrowthMetrics);
        let itemsHtml = "";

        activeKeys.forEach(key => {
            const conf = GROWTH_METRICS_CONFIG[key];
            const val = dataItem[key];
            const evalInfo = conf.evaluator(val);
            const formattedVal = key === "k" ? Number(val).toFixed(4) : (key === "adwg" ? Number(val).toFixed(3) : Number(val).toLocaleString(undefined, { maximumFractionDigits: 2 }));

            itemsHtml += `
                <div class="tooltip-item">
                    <div class="tooltip-item-left">
                        <span class="tooltip-dot" style="background:${conf.color};"></span>
                        <span class="tooltip-param-label">${conf.eq}: ${conf.label}</span>
                    </div>
                    <div class="tooltip-item-right">
                        <span class="tooltip-param-value">${formattedVal} ${conf.unit}</span>
                        <span class="tooltip-param-status ${evalInfo.badgeClass.replace('badge-', 'status-')}">${evalInfo.status}</span>
                    </div>
                </div>
            `;
        });

        growthTooltip.innerHTML = `
            <div class="tooltip-header">
                <span class="tooltip-time-badge">${dataItem.label || `DOC ${dataItem.day}`}</span>
                <span class="tooltip-status-pill pill-optimal">P. vannamei</span>
            </div>
            <div class="tooltip-content">
                ${itemsHtml}
            </div>
        `;

        growthTooltip.hidden = false;
        growthTooltip.classList.add("visible");

        const tooltipWidth = 285;
        let left = pointX + 16;
        if (left + tooltipWidth > containerWidth - 10) {
            left = pointX - tooltipWidth - 16;
        }
        const top = Math.max(10, Math.min(mouseY - 30, containerHeight - 160));

        growthTooltip.style.left = `${left}px`;
        growthTooltip.style.top = `${top}px`;
    }"""

new_tooltip = """    function renderGrowthTooltip(index, pointX, mouseY, focusedParam, containerWidth, containerHeight) {
        if (!growthTooltip) return;
        const dataItem = currentGrowthChartData[index];
        if (!dataItem) return;

        const activeKeys = Array.from(selectedGrowthMetrics);
        let itemsHtml = "";

        activeKeys.forEach(key => {
            const conf = GROWTH_METRICS_CONFIG[key];
            const val = dataItem[key];
            const evalInfo = conf.evaluator(val);
            const formattedVal = key === "k"
                ? Number(val).toFixed(4)
                : (key === "adwg"
                    ? Number(val).toFixed(3)
                    : (key === "sr" || key === "fabw" || key === "sgr" || key === "fcr"
                        ? Number(val).toFixed(2)
                        : Number(val).toLocaleString(undefined, { maximumFractionDigits: 1 })
                      )
                  );

            const isItemFocused = focusedParam === key;
            const statusClass = evalInfo.badgeClass ? evalInfo.badgeClass.replace("badge-", "status-") : "status-optimal";

            itemsHtml += `
                <div class="tooltip-item ${isItemFocused ? 'tooltip-item-focused' : ''}">
                    <div class="tooltip-item-left">
                        <span class="tooltip-dot" style="background:${conf.color};"></span>
                        <span class="tooltip-param-label">${conf.eq}: ${conf.label}</span>
                    </div>
                    <div class="tooltip-item-right">
                        <span class="tooltip-param-value">${formattedVal} ${conf.unit}</span>
                        <span class="tooltip-param-status ${statusClass}">${evalInfo.status}</span>
                    </div>
                </div>
            `;
        });

        const timeBadge = dataItem.timeStr
            ? `${dataItem.label} • ${dataItem.timeStr}`
            : (dataItem.day ? `DOC ${dataItem.day} • Culture Day ${dataItem.day}` : dataItem.label);

        growthTooltip.innerHTML = `
            <div class="tooltip-header">
                <span class="tooltip-time-badge">${timeBadge}</span>
                <span class="tooltip-status-pill pill-optimal">P. vannamei</span>
            </div>
            <div class="tooltip-content">
                ${itemsHtml}
            </div>
        `;

        growthTooltip.hidden = false;
        growthTooltip.classList.add("visible");

        // Calculate dynamic dimensions matching water quality trends
        const tooltipWidth = growthTooltip.offsetWidth || 285;
        const tooltipHeight = growthTooltip.offsetHeight || 210;

        let leftPos = pointX + 16;
        if (leftPos + tooltipWidth > containerWidth - 12) {
            leftPos = pointX - tooltipWidth - 16;
        }
        if (leftPos < 12) leftPos = 12;

        let topPos = mouseY - (tooltipHeight / 2);
        topPos = Math.max(8, Math.min(containerHeight - tooltipHeight - 8, topPos));

        growthTooltip.style.left = `${leftPos}px`;
        growthTooltip.style.top = `${topPos}px`;
    }"""

if old_tooltip in js_content:
    js_content = js_content.replace(old_tooltip, new_tooltip)
    print("Replaced renderGrowthTooltip")
else:
    print("WARNING: old_tooltip not found!")

# 4. Update closeGrowthGraphModal
old_close = """    function closeGrowthGraphModal() {
        if (!growthGraphModal) return;
        growthGraphModal.hidden = true;
        document.body.style.overflow = "";
        if (growthTooltip) {
            growthTooltip.classList.remove("visible");
            growthTooltip.hidden = true;
        }
        growthChartHoverIndex = null;
    }"""

new_close = """    function closeGrowthGraphModal() {
        if (!growthGraphModal) return;
        growthGraphModal.hidden = true;
        document.body.style.overflow = "";
        if (growthTooltip) {
            growthTooltip.classList.remove("visible");
            growthTooltip.hidden = true;
        }
        growthChartHoverIndex = null;
        growthChartHoveredParam = null;
    }"""

if old_close in js_content:
    js_content = js_content.replace(old_close, new_close)
    print("Replaced closeGrowthGraphModal")
else:
    print("WARNING: old_close not found!")

# 5. Remove btnOpenGrowthChartTop listener
old_listener = """    if (btnOpenGrowthChart) btnOpenGrowthChart.addEventListener("click", openGrowthGraphModal);
    if (btnOpenGrowthChartTop) btnOpenGrowthChartTop.addEventListener("click", openGrowthGraphModal);"""

new_listener = """    if (btnOpenGrowthChart) btnOpenGrowthChart.addEventListener("click", openGrowthGraphModal);"""

if old_listener in js_content:
    js_content = js_content.replace(old_listener, new_listener)
    print("Removed btnOpenGrowthChartTop listener")
else:
    print("WARNING: old_listener not found!")

# 6. Update canvas pointer interaction
old_events = """    // Pointer hover interactions on canvas
    if (growthChartCanvas) {
        growthChartCanvas.addEventListener("pointermove", (e) => {
            if (!currentGrowthChartData || currentGrowthChartData.length === 0) return;
            const rect = growthChartCanvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            const padding = { top: 28, right: 35, bottom: 38, left: 48 };
            const chartW = (growthChartCanvas.clientWidth || 750) - padding.left - padding.right;
            const dataCount = currentGrowthChartData.length;

            if (mouseX < padding.left - 10 || mouseX > padding.left + chartW + 10) {
                if (growthTooltip) {
                    growthTooltip.classList.remove("visible");
                    growthTooltip.hidden = true;
                }
                growthChartHoverIndex = null;
                renderGrowthChart();
                return;
            }

            let closestIndex = 0;
            let closestDist = Infinity;

            for (let i = 0; i < dataCount; i++) {
                const ptX = dataCount === 1
                    ? padding.left + chartW / 2
                    : padding.left + (i / (dataCount - 1)) * chartW;
                const dist = Math.abs(mouseX - ptX);
                if (dist < closestDist) {
                    closestDist = dist;
                    closestIndex = i;
                }
            }

            growthChartHoverIndex = closestIndex;
            renderGrowthChart();

            const pointX = dataCount === 1
                ? padding.left + chartW / 2
                : padding.left + (closestIndex / (dataCount - 1)) * chartW;

            renderGrowthTooltip(closestIndex, pointX, mouseY, growthChartCanvas.clientWidth || 750, growthChartCanvas.clientHeight || 300);
        });

        growthChartCanvas.addEventListener("pointerleave", () => {
            if (growthTooltip) {
                growthTooltip.classList.remove("visible");
                growthTooltip.hidden = true;
            }
            growthChartHoverIndex = null;
            renderGrowthChart();
        });
    }"""

new_events = """    function handleGrowthPointerMove(event) {
        if (!currentGrowthChartData || currentGrowthChartData.length === 0) return;
        const rect = growthChartCanvas.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;
        const width = growthChartCanvas.clientWidth || 750;
        const height = growthChartCanvas.clientHeight || 320;

        const padding = { top: 28, right: 35, bottom: 38, left: 48 };
        const chartW = width - padding.left - padding.right;
        const dataCount = currentGrowthChartData.length;

        if (
            mouseX < padding.left - 15 ||
            mouseX > width - padding.right + 15 ||
            mouseY < padding.top - 15 ||
            mouseY > height - padding.bottom + 15
        ) {
            handleGrowthPointerLeave();
            return;
        }

        let nearestIndex = 0;
        if (dataCount > 1) {
            const ratio = (mouseX - padding.left) / chartW;
            nearestIndex = Math.round(ratio * (dataCount - 1));
            nearestIndex = Math.max(0, Math.min(dataCount - 1, nearestIndex));
        }

        const dataItem = currentGrowthChartData[nearestIndex];
        if (!dataItem) {
            handleGrowthPointerLeave();
            return;
        }

        // Determine closest metric point along vertical crosshair
        const activeKeys = Array.from(selectedGrowthMetrics).filter(
            k => currentGrowthChartPoints[k] && currentGrowthChartPoints[k][nearestIndex]
        );

        let closestParam = null;
        let pointX = dataCount === 1 ? padding.left + chartW / 2 : padding.left + (nearestIndex / (dataCount - 1)) * chartW;

        if (activeKeys.length > 0) {
            pointX = currentGrowthChartPoints[activeKeys[0]][nearestIndex].x;
            let minDistance = Infinity;
            activeKeys.forEach(k => {
                const pt = currentGrowthChartPoints[k][nearestIndex];
                if (pt) {
                    const dist = Math.hypot(mouseX - pt.x, mouseY - pt.y);
                    if (dist < minDistance) {
                        minDistance = dist;
                        closestParam = k;
                    }
                }
            });

            if (minDistance >= 40) {
                closestParam = null;
            }
        }

        growthChartHoverIndex = nearestIndex;
        growthChartHoveredParam = closestParam;
        renderGrowthChart();
        renderGrowthTooltip(nearestIndex, pointX, mouseY, closestParam, width, height);
    }

    function handleGrowthPointerLeave() {
        if (growthTooltip) {
            growthTooltip.classList.remove("visible");
            growthTooltip.hidden = true;
        }
        if (growthChartHoverIndex !== null || growthChartHoveredParam !== null) {
            growthChartHoverIndex = null;
            growthChartHoveredParam = null;
            renderGrowthChart();
        }
    }

    // Pointer hover interactions on canvas matching Water Quality Trends
    if (growthChartCanvas) {
        growthChartCanvas.addEventListener("pointermove", handleGrowthPointerMove);
        growthChartCanvas.addEventListener("pointerleave", handleGrowthPointerLeave);
    }"""

if old_events in js_content:
    js_content = js_content.replace(old_events, new_events)
    print("Replaced canvas pointer interaction in calculators.js")
else:
    print("WARNING: old_events not found!")

with open("static/js/calculators.js", "w", encoding="utf-8", newline="\r\n") as f:
    f.write(js_content)

print("Updated static/js/calculators.js successfully.")

# Update CSS for .growth-chart-wrap
with open("static/css/style.css", "r", encoding="utf-8") as f:
    css_content = f.read()

old_css = """.growth-chart-wrap {
    position: relative;
    width: 100%;
    height: 310px;
    min-height: 240px;
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    box-sizing: border-box;
    overflow: hidden;
}"""

new_css = """.growth-chart-wrap {
    position: relative;
    width: 100%;
    height: 320px;
    min-height: 240px;
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    box-sizing: border-box;
    overflow: visible;
    cursor: crosshair;
}"""

if old_css in css_content:
    css_content = css_content.replace(old_css, new_css)
    print("Updated .growth-chart-wrap in style.css")
    with open("static/css/style.css", "w", encoding="utf-8", newline="\r\n") as f:
        f.write(css_content)
else:
    print("WARNING: old_css not found in style.css!")
