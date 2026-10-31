with open("static/js/calculators.js", "r", encoding="utf-8") as f:
    content = f.read()

target = "    async function boot() {"

graph_js = """    // =============================================================
    // SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE POPUP GRAPH
    // (Eqs. 1–8 Excl. Eq. 5 Initial Biomass)
    // =============================================================
    const GROWTH_METRICS_CONFIG = {
        sr: {
            id: "sr",
            eq: "Eq. 1",
            label: "Survival Rate",
            unit: "%",
            color: "#e11d48",
            glow: "rgba(225, 29, 72, 0.22)",
            evaluator: (v) => v >= 80 ? { status: "Optimal", badgeClass: "badge-optimal" } : (v >= 65 ? { status: "Acceptable", badgeClass: "badge-warning" } : { status: "Suboptimal", badgeClass: "badge-critical" })
        },
        fabw: {
            id: "fabw",
            eq: "Eq. 2",
            label: "Final Avg Body Weight",
            unit: "g",
            color: "#6366f1",
            glow: "rgba(99, 102, 241, 0.22)",
            evaluator: (v) => v >= 20 ? { status: "Large (>20g)", badgeClass: "badge-optimal" } : (v >= 15 ? { status: "Medium (15-20g)", badgeClass: "badge-optimal" } : { status: "Juvenile (<15g)", badgeClass: "badge-warning" })
        },
        adwg: {
            id: "adwg",
            eq: "Eq. 3",
            label: "Daily Weight Gain",
            unit: "g/d",
            color: "#0284c7",
            glow: "rgba(2, 132, 199, 0.22)",
            evaluator: (v) => v >= 0.20 ? { status: "Fast (≥0.20)", badgeClass: "badge-optimal" } : (v >= 0.15 ? { status: "Moderate (0.15-0.19)", badgeClass: "badge-warning" } : { status: "Slow (<0.15)", badgeClass: "badge-critical" })
        },
        sgr: {
            id: "sgr",
            eq: "Eq. 4",
            label: "Specific Growth Rate",
            unit: "%/d",
            color: "#10b981",
            glow: "rgba(16, 185, 129, 0.22)",
            evaluator: (v) => v >= 5.0 ? { status: "High (≥5%)", badgeClass: "badge-optimal" } : (v >= 2.5 ? { status: "Normal (2.5-5%)", badgeClass: "badge-optimal" } : { status: "Slow (<2.5%)", badgeClass: "badge-warning" })
        },
        fb: {
            id: "fb",
            eq: "Eq. 6",
            label: "Final Biomass",
            unit: "kg",
            color: "#2563eb",
            glow: "rgba(37, 99, 235, 0.22)",
            evaluator: (v) => ({ status: "Pond Yield", badgeClass: "badge-optimal" })
        },
        fcr: {
            id: "fcr",
            eq: "Eq. 7",
            label: "Feed Conversion Ratio",
            unit: "",
            color: "#d97706",
            glow: "rgba(217, 119, 6, 0.22)",
            evaluator: (v) => v <= 1.50 ? { status: "Optimal (≤1.50)", badgeClass: "badge-optimal" } : (v <= 1.80 ? { status: "Acceptable (1.51-1.80)", badgeClass: "badge-warning" } : { status: "Suboptimal (>1.80)", badgeClass: "badge-critical" })
        },
        k: {
            id: "k",
            eq: "Eq. 8",
            label: "Fulton's Condition Factor",
            unit: "",
            color: "#8b5cf6",
            glow: "rgba(139, 92, 246, 0.22)",
            evaluator: (v) => (v >= 0.80 && v <= 1.15) ? { status: "Optimal (0.80-1.15)", badgeClass: "badge-optimal" } : (v < 0.80 ? { status: "Slender (<0.80)", badgeClass: "badge-warning" } : { status: "Plump (>1.15)", badgeClass: "badge-optimal" })
        }
    };

    let selectedGrowthMetrics = new Set(["sr", "fabw", "adwg", "sgr", "fb", "fcr", "k"]);
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
    const btnOpenGrowthChartTop = document.getElementById("btn-open-growth-chart-top");
    const btnGraphModeTrajectory = document.getElementById("btn-graph-mode-trajectory");
    const btnGraphModeHistory = document.getElementById("btn-graph-mode-history");
    const btnToggleAllGrowthMetrics = document.getElementById("btn-toggle-all-growth-metrics");
    const growthMetricChips = document.querySelectorAll("#growth-metric-chips-group .metric-chip");
    const growthChartCanvas = document.getElementById("growth-trend-chart");
    const growthTooltip = document.getElementById("growth-chart-tooltip");
    const growthGraphExportBtn = document.getElementById("growth-graph-open-export");

    function generateGrowthTrajectory() {
        const isCount = Math.max(1, Number(document.getElementById("gm-initial-stocking")?.value || 100000));
        const lhcCount = Math.max(1, Number(document.getElementById("gm-live-harvest-count")?.value || 85000));
        const docTotal = Math.max(1, Number(document.getElementById("gm-days-of-culture")?.value || 90));
        const ibwVal = Math.max(0.0001, Number(document.getElementById("gm-initial-weight")?.value || 0.010));
        const bwInput = Math.max(0.1, Number(document.getElementById("gm-bulk-weight")?.value || 1700));
        const bwUnit = document.getElementById("gm-bw-unit")?.value || "kg";
        const tfgInput = Math.max(0.1, Number(document.getElementById("gm-total-feed")?.value || 2125));
        const feedUnit = document.getElementById("gm-feed-unit")?.value || "kg";
        const tlCm = Math.max(0.1, Number(document.getElementById("gm-total-length")?.value || 12.9));

        const bwGrams = bwUnit === "kg" ? bwInput * 1000.0 : bwInput;
        const fabwVal = bwGrams / lhcCount;
        const tfgKg = feedUnit === "kg" ? tfgInput : tfgInput / 1000.0;
        const sgr = ((Math.log(fabwVal) - Math.log(ibwVal)) / docTotal) * 100.0;
        const adwg = (fabwVal - ibwVal) / docTotal;

        const steps = 7;
        const points = [];

        for (let i = 0; i < steps; i++) {
            const fraction = i / (steps - 1);
            const day = Math.max(1, Math.round(fraction * docTotal));
            const dayFrac = day / docTotal;

            // Exponential weight progression
            const curW = i === 0 ? ibwVal : (i === steps - 1 ? fabwVal : ibwVal * Math.exp((sgr / 100.0) * day));
            // Logistic mortality curve
            const curPop = Math.round(isCount - (isCount - lhcCount) * Math.pow(dayFrac, 0.85));
            const curSR = (curPop / isCount) * 100.0;
            // Final Biomass at day t (Eq. 6)
            const curFB = (curPop * curW) / 1000.0;
            // Daily gain (Eq. 3)
            const curADWG = day > 1 ? (curW - ibwVal) / day : adwg;
            // SGR (Eq. 4)
            const curSGR = day > 1 ? ((Math.log(curW) - Math.log(ibwVal)) / day) * 100.0 : sgr;
            // Cumulative feed & FCR (Eq. 7)
            const curFeed = tfgKg * Math.pow(dayFrac, 1.4);
            const ibKg = (isCount * ibwVal) / 1000.0;
            const curNet = Math.max(0.1, curFB - ibKg);
            const curFCR = day > 10 ? Math.max(0.9, Math.min(2.2, curFeed / curNet)) : 1.18;
            // Length & Fulton's K (Eq. 8)
            const curTL = Math.max(1.0, tlCm * Math.pow(curW / fabwVal, 0.333));
            const curK = (curW / Math.pow(curTL, 3)) * 100.0;

            points.push({
                label: `DOC ${day}`,
                day: day,
                sr: Number(curSR.toFixed(2)),
                fabw: Number(curW.toFixed(2)),
                adwg: Number(curADWG.toFixed(3)),
                sgr: Number(curSGR.toFixed(2)),
                fb: Number(curFB.toFixed(1)),
                fcr: Number(curFCR.toFixed(2)),
                k: Number(curK.toFixed(4)),
            });
        }
        return points;
    }

    function buildHistoryPoints(records) {
        if (!records || !records.length) return [];
        // Sort oldest to newest chronologically
        const sorted = [...records].reverse();
        return sorted.map((r, idx) => ({
            label: r.notes ? (r.notes.length > 15 ? r.notes.substring(0, 13) + '...' : r.notes) : `Run #${r.id}`,
            day: idx + 1,
            sr: Number(r.eq1_sr_pct ?? 0),
            fabw: Number(r.eq2_fabw_g ?? 0),
            adwg: Number(r.eq3_adwg_g_day ?? 0),
            sgr: Number(r.eq4_sgr_pct_day ?? 0),
            fb: Number(r.eq6_fb_kg ?? 0),
            fcr: Number(r.eq7_fcr ?? 0),
            k: Number(r.eq8_fulton_k ?? 0),
        }));
    }

    function renderGrowthChart() {
        if (!growthChartCanvas) return;
        const context = growthChartCanvas.getContext("2d");
        const width = growthChartCanvas.clientWidth || 750;
        const height = growthChartCanvas.clientHeight || 300;
        const scale = window.devicePixelRatio || 1;

        growthChartCanvas.width = Math.round(width * scale);
        growthChartCanvas.height = Math.round(height * scale);
        context.scale(scale, scale);
        context.clearRect(0, 0, width, height);

        const emptyEl = document.getElementById("growth-chart-empty");
        if (!currentGrowthChartData || currentGrowthChartData.length === 0) {
            if (emptyEl) {
                emptyEl.hidden = false;
                emptyEl.textContent = growthChartMode === "history"
                    ? "No saved database records found yet. Click 'Save Snapshot' above to store your first run."
                    : "No calculation data available.";
            }
            return;
        }

        const activeKeys = Array.from(selectedGrowthMetrics);
        if (activeKeys.length === 0) {
            if (emptyEl) {
                emptyEl.hidden = false;
                emptyEl.textContent = "Please select at least one metric chip above to display the curve.";
            }
            return;
        }

        if (emptyEl) emptyEl.hidden = true;

        const padding = { top: 28, right: 35, bottom: 38, left: 48 };
        const chartW = width - padding.left - padding.right;
        const chartH = height - padding.top - padding.bottom;

        // Grid lines matching Water Quality Trend (#e8edea)
        context.strokeStyle = "#e8edea";
        context.fillStyle = "#8a978f";
        context.font = "600 11px Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
        context.lineWidth = 1;

        const gridSteps = 5;
        const isSingleMetric = activeKeys.length === 1;
        let singleMin = 0, singleMax = 100, singleRange = 100;

        if (isSingleMetric) {
            const key = activeKeys[0];
            const vals = currentGrowthChartData.map(d => Number(d[key]) || 0);
            singleMin = Math.min(...vals);
            singleMax = Math.max(...vals);
            if (singleMin === singleMax) {
                singleMin = 0;
                singleMax = singleMax > 0 ? singleMax * 1.5 : 10;
            }
            singleRange = singleMax - singleMin || 1;
        }

        for (let index = 0; index < gridSteps; index += 1) {
            const y = padding.top + (chartH / (gridSteps - 1)) * index;
            context.beginPath();
            context.moveTo(padding.left, y);
            context.lineTo(width - padding.right, y);
            context.stroke();

            let labelVal = "";
            if (isSingleMetric) {
                const rawVal = singleMax - (singleRange / (gridSteps - 1)) * index;
                labelVal = rawVal >= 100 ? Math.round(rawVal).toString() : rawVal.toFixed(1);
            } else {
                const pct = Math.round(100 - (100 / (gridSteps - 1)) * index);
                labelVal = `${pct}%`;
            }
            context.fillText(labelVal, 8, y + 4);
        }

        // X-axis baseline
        context.beginPath();
        context.moveTo(padding.left, height - padding.bottom);
        context.lineTo(width - padding.right, height - padding.bottom);
        context.stroke();

        const dataCount = currentGrowthChartData.length;
        currentGrowthChartPoints = {};

        activeKeys.forEach(key => {
            const vals = currentGrowthChartData.map(d => Number(d[key]) || 0);
            const minVal = Math.min(...vals);
            const maxVal = Math.max(...vals);
            const rVal = maxVal - minVal || (maxVal > 0 ? maxVal : 1);

            currentGrowthChartPoints[key] = currentGrowthChartData.map((d, index) => {
                const val = Number(d[key]) || 0;
                const x = dataCount === 1
                    ? padding.left + chartW / 2
                    : padding.left + (index / (dataCount - 1)) * chartW;

                const norm = isSingleMetric ? (val - singleMin) / singleRange : (val - minVal) / rVal;
                const y = padding.top + (1 - Math.max(0, Math.min(1, norm))) * chartH;

                return { x, y, value: val, key, dataIndex: index, dataItem: d };
            });
        });

        // X-axis point labels
        context.fillStyle = "#64748b";
        context.font = "600 11px Inter, sans-serif";
        context.textAlign = "center";
        currentGrowthChartData.forEach((d, index) => {
            const x = dataCount === 1
                ? padding.left + chartW / 2
                : padding.left + (index / (dataCount - 1)) * chartW;
            context.fillText(d.label || `DOC ${d.day}`, x, height - padding.bottom + 18);
        });
        context.textAlign = "left";

        // Vertical dashed guide line on hover
        if (growthChartHoverIndex !== null && growthChartHoverIndex >= 0 && growthChartHoverIndex < dataCount) {
            const firstKey = activeKeys[0];
            if (currentGrowthChartPoints[firstKey] && currentGrowthChartPoints[firstKey][growthChartHoverIndex]) {
                const hoverX = currentGrowthChartPoints[firstKey][growthChartHoverIndex].x;
                context.save();
                context.beginPath();
                context.setLineDash([4, 4]);
                context.strokeStyle = "rgba(18, 107, 79, 0.45)";
                context.lineWidth = 1.5;
                context.moveTo(hoverX, padding.top - 6);
                context.lineTo(hoverX, height - padding.bottom + 4);
                context.stroke();
                context.restore();
            }
        }

        // Draw smooth lines, area gradients, and dots for each metric
        activeKeys.forEach(key => {
            const conf = GROWTH_METRICS_CONFIG[key];
            const pts = currentGrowthChartPoints[key];
            if (!pts || !pts.length) return;

            // Area Gradient beneath curve
            if (pts.length > 1) {
                const grad = context.createLinearGradient(0, padding.top, 0, height - padding.bottom);
                grad.addColorStop(0, conf.glow);
                grad.addColorStop(1, "rgba(255, 255, 255, 0.0)");

                context.beginPath();
                context.moveTo(pts[0].x, height - padding.bottom);
                pts.forEach(pt => context.lineTo(pt.x, pt.y));
                context.lineTo(pts[pts.length - 1].x, height - padding.bottom);
                context.closePath();
                context.fillStyle = grad;
                context.fill();
            }

            // Line
            context.beginPath();
            pts.forEach((pt, idx) => {
                if (idx === 0) context.moveTo(pt.x, pt.y);
                else context.lineTo(pt.x, pt.y);
            });
            context.strokeStyle = conf.color;
            context.lineWidth = 2.5;
            context.lineCap = "round";
            context.lineJoin = "round";
            context.stroke();

            // Circular points with hover halo
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
            });
        });
    }

    function renderGrowthTooltip(index, pointX, mouseY, containerWidth, containerHeight) {
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
    }

    function updateGrowthChartLegend() {
        const legendEl = document.getElementById("growth-chart-legend");
        if (!legendEl) return;
        const activeKeys = Array.from(selectedGrowthMetrics);
        legendEl.innerHTML = activeKeys.map(key => {
            const conf = GROWTH_METRICS_CONFIG[key];
            return `
                <span>
                    <i style="background:${conf.color};"></i>
                    ${conf.eq}: ${conf.label} ${conf.unit ? '(' + conf.unit + ')' : ''}
                </span>
            `;
        }).join("");
    }

    function updateGrowthMiniStats() {
        const cur = collectCurrentCalculations();
        const setEl = (id, text) => {
            const el = document.getElementById(id);
            if (el) el.textContent = text;
        };

        setEl("mini-stat-sr", `${cur.eq1_sr_pct.toFixed(2)} %`);
        setEl("mini-stat-fabw", `${cur.eq2_fabw_g.toFixed(2)} g`);
        setEl("mini-sub-fabw", `${cur.eq2_count_per_kg.toFixed(1)}/kg`);
        setEl("mini-stat-adwg", `${cur.eq3_adwg_g_day.toFixed(3)} g/d`);
        setEl("mini-stat-sgr", `${cur.eq4_sgr_pct_day.toFixed(2)} %/d`);
        setEl("mini-stat-fb", `${cur.eq6_fb_kg.toLocaleString(undefined, {maximumFractionDigits: 1})} kg`);
        setEl("mini-stat-fcr", cur.eq7_fcr.toFixed(2));
        setEl("mini-stat-k", cur.eq8_fulton_k.toFixed(4));

        const badgeSr = document.getElementById("mini-badge-sr");
        if (badgeSr) {
            const evalSr = GROWTH_METRICS_CONFIG.sr.evaluator(cur.eq1_sr_pct);
            badgeSr.textContent = evalSr.status;
            badgeSr.className = `mini-badge ${evalSr.badgeClass}`;
        }
        const badgeAdwg = document.getElementById("mini-badge-adwg");
        if (badgeAdwg) {
            const evalAdwg = GROWTH_METRICS_CONFIG.adwg.evaluator(cur.eq3_adwg_g_day);
            badgeAdwg.textContent = evalAdwg.status;
            badgeAdwg.className = `mini-badge ${evalAdwg.badgeClass}`;
        }
        const badgeFcr = document.getElementById("mini-badge-fcr");
        if (badgeFcr) {
            const evalFcr = GROWTH_METRICS_CONFIG.fcr.evaluator(cur.eq7_fcr);
            badgeFcr.textContent = evalFcr.status;
            badgeFcr.className = `mini-badge ${evalFcr.badgeClass}`;
        }
        const badgeK = document.getElementById("mini-badge-k");
        if (badgeK) {
            const evalK = GROWTH_METRICS_CONFIG.k.evaluator(cur.eq8_fulton_k);
            badgeK.textContent = evalK.status;
            badgeK.className = `mini-badge ${evalK.badgeClass}`;
        }
    }

    async function openGrowthGraphModal() {
        if (!growthGraphModal) return;

        const docTotal = Math.max(1, Number(document.getElementById("gm-days-of-culture")?.value || 90));
        const docPill = document.getElementById("graph-doc-pill");
        if (docPill) docPill.textContent = docTotal;

        // Fetch history if needed
        try {
            const res = await fetch("/api/calculators/history");
            if (res.ok) {
                const data = await res.json();
                growthHistoryRecords = data.latest || [];
            }
        } catch (err) {
            console.error("Failed to load calculation history:", err);
        }

        if (growthChartMode === "history" && growthHistoryRecords.length > 0) {
            currentGrowthChartData = buildHistoryPoints(growthHistoryRecords);
        } else {
            growthChartMode = "trajectory";
            if (btnGraphModeTrajectory) btnGraphModeTrajectory.classList.add("active");
            if (btnGraphModeHistory) btnGraphModeHistory.classList.remove("active");
            currentGrowthChartData = generateGrowthTrajectory();
        }

        updateGrowthMiniStats();
        updateGrowthChartLegend();
        growthGraphModal.hidden = false;
        document.body.style.overflow = "hidden";

        // Render on next frame after modal is visible
        requestAnimationFrame(() => {
            renderGrowthChart();
        });
    }

    function closeGrowthGraphModal() {
        if (!growthGraphModal) return;
        growthGraphModal.hidden = true;
        document.body.style.overflow = "";
        if (growthTooltip) {
            growthTooltip.classList.remove("visible");
            growthTooltip.hidden = true;
        }
        growthChartHoverIndex = null;
    }

    // Graph Modal Event Listeners
    if (btnOpenGrowthChart) btnOpenGrowthChart.addEventListener("click", openGrowthGraphModal);
    if (btnOpenGrowthChartTop) btnOpenGrowthChartTop.addEventListener("click", openGrowthGraphModal);
    if (closeGrowthGraphModalBtn) closeGrowthGraphModalBtn.addEventListener("click", closeGrowthGraphModal);
    if (closeGrowthGraphActionBtn) closeGrowthGraphActionBtn.addEventListener("click", closeGrowthGraphModal);
    if (growthGraphModal) {
        growthGraphModal.addEventListener("click", (e) => {
            if (e.target === growthGraphModal) closeGrowthGraphModal();
        });
    }

    // Mode Toggle (Trajectory vs Saved History)
    if (btnGraphModeTrajectory) {
        btnGraphModeTrajectory.addEventListener("click", () => {
            growthChartMode = "trajectory";
            btnGraphModeTrajectory.classList.add("active");
            if (btnGraphModeHistory) btnGraphModeHistory.classList.remove("active");
            currentGrowthChartData = generateGrowthTrajectory();
            renderGrowthChart();
        });
    }

    if (btnGraphModeHistory) {
        btnGraphModeHistory.addEventListener("click", async () => {
            growthChartMode = "history";
            btnGraphModeHistory.classList.add("active");
            if (btnGraphModeTrajectory) btnGraphModeTrajectory.classList.remove("active");

            if (!growthHistoryRecords.length) {
                try {
                    const res = await fetch("/api/calculators/history");
                    if (res.ok) {
                        const data = await res.json();
                        growthHistoryRecords = data.latest || [];
                    }
                } catch (e) {
                    console.error("Error loading batches:", e);
                }
            }
            currentGrowthChartData = buildHistoryPoints(growthHistoryRecords);
            renderGrowthChart();
        });
    }

    // Metric Chips (Multi-toggle)
    growthMetricChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const metric = chip.dataset.metric;
            if (selectedGrowthMetrics.has(metric)) {
                if (selectedGrowthMetrics.size > 1) {
                    selectedGrowthMetrics.delete(metric);
                    chip.classList.remove("active");
                }
            } else {
                selectedGrowthMetrics.add(metric);
                chip.classList.add("active");
            }
            updateGrowthChartLegend();
            renderGrowthChart();
        });
    });

    if (btnToggleAllGrowthMetrics) {
        btnToggleAllGrowthMetrics.addEventListener("click", () => {
            selectedGrowthMetrics = new Set(["sr", "fabw", "adwg", "sgr", "fb", "fcr", "k"]);
            growthMetricChips.forEach(chip => chip.classList.add("active"));
            updateGrowthChartLegend();
            renderGrowthChart();
        });
    }

    // Pointer hover interactions on canvas
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
    }

    // Shortcut button to export Growth parameters
    if (growthGraphExportBtn) {
        growthGraphExportBtn.addEventListener("click", () => {
            closeGrowthGraphModal();
            // Pre-select growth checkbox in export modal
            const catCheckboxes = document.querySelectorAll('input[name="export-category"]');
            catCheckboxes.forEach(cb => {
                cb.checked = (cb.value === "growth");
            });
            openExportModal();
        });
    }

    // Window resize redraws chart
    window.addEventListener("resize", () => {
        if (growthGraphModal && !growthGraphModal.hidden) {
            renderGrowthChart();
        }
    });

    // Escape key closes graph modal
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && growthGraphModal && !growthGraphModal.hidden) {
            closeGrowthGraphModal();
        }
    });

"""

norm_content = content.replace("\r\n", "\n")
norm_target = target.replace("\r\n", "\n")

if norm_target in norm_content:
    norm_content = norm_content.replace(norm_target, graph_js + "\n" + norm_target)
    print("Inserted Growth Graph JS logic successfully")
else:
    print("ERROR: Target boot() not found")

with open("static/js/calculators.js", "w", encoding="utf-8") as f:
    f.write(norm_content)

print("Saved static/js/calculators.js successfully")

