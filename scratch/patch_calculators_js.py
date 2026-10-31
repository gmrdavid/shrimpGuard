with open("static/js/calculators.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. Update openGrowthGraphModal
old_open_modal = """    async function openGrowthGraphModal() {
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
    }"""

new_open_modal = """    async function openGrowthGraphModal() {
        if (!growthGraphModal) return;

        // 1. Immediately prepare trajectory data so points are ready synchronously with zero lag
        if (growthChartMode !== "history") {
            growthChartMode = "trajectory";
            if (btnGraphModeTrajectory) btnGraphModeTrajectory.classList.add("active");
            if (btnGraphModeHistory) btnGraphModeHistory.classList.remove("active");
            currentGrowthChartData = generateGrowthTrajectory();
        }

        const docTotal = Math.max(1, Number(document.getElementById("gm-days-of-culture")?.value || 90));
        const docPill = document.getElementById("graph-doc-pill");
        if (docPill) docPill.textContent = docTotal;

        updateGrowthMiniStats();
        updateGrowthChartLegend();
        growthGraphModal.hidden = false;
        document.body.style.overflow = "hidden";

        // Render immediately and on animation frame
        renderGrowthChart();
        requestAnimationFrame(() => {
            renderGrowthChart();
        });

        // 2. Fetch history in background for Saved Database Batches view
        try {
            const res = await fetch("/api/calculators/history");
            if (res.ok) {
                const data = await res.json();
                growthHistoryRecords = data.latest || [];
                if (growthChartMode === "history" && growthHistoryRecords.length > 0) {
                    currentGrowthChartData = buildHistoryPoints(growthHistoryRecords);
                    renderGrowthChart();
                }
            }
        } catch (err) {
            console.error("Failed to load calculation history:", err);
        }
    }"""

if old_open_modal in js:
    js = js.replace(old_open_modal, new_open_modal)
    print("Replaced openGrowthGraphModal successfully")
else:
    print("WARNING: old_open_modal not found!")

# 2. Update renderGrowthTooltip & handleGrowthPointerMove
old_handler = """    function handleGrowthPointerMove(event) {
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

new_handler = """    function handleGrowthPointerMove(event) {
        if (!growthChartCanvas) return;
        if (!currentGrowthChartData || currentGrowthChartData.length === 0) {
            currentGrowthChartData = generateGrowthTrajectory();
        }
        if (!currentGrowthChartData || currentGrowthChartData.length === 0) return;

        const rect = growthChartCanvas.getBoundingClientRect();
        const clientX = event.clientX !== undefined ? event.clientX : (event.touches && event.touches[0] ? event.touches[0].clientX : 0);
        const clientY = event.clientY !== undefined ? event.clientY : (event.touches && event.touches[0] ? event.touches[0].clientY : 0);
        const mouseX = clientX - rect.left;
        const mouseY = clientY - rect.top;
        const width = growthChartCanvas.clientWidth || 750;
        const height = growthChartCanvas.clientHeight || 340;

        const padding = { top: 28, right: 35, bottom: 38, left: 48 };
        const chartW = width - padding.left - padding.right;
        const dataCount = currentGrowthChartData.length;

        if (
            mouseX < padding.left - 25 ||
            mouseX > width - padding.right + 25 ||
            mouseY < padding.top - 25 ||
            mouseY > height - padding.bottom + 25
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

        // Ensure points exist
        if (!currentGrowthChartPoints || Object.keys(currentGrowthChartPoints).length === 0) {
            renderGrowthChart();
        }

        // Determine closest metric point along vertical crosshair
        const activeKeys = Array.from(selectedGrowthMetrics).filter(
            k => currentGrowthChartPoints[k] && currentGrowthChartPoints[k][nearestIndex]
        );

        let closestParam = null;
        let pointX = dataCount === 1 ? padding.left + chartW / 2 : padding.left + (nearestIndex / (dataCount - 1)) * chartW;
        let targetY = mouseY;

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
                        targetY = pt.y;
                    }
                }
            });

            if (minDistance >= 50) {
                closestParam = null;
                targetY = mouseY;
            }
        }

        growthChartHoverIndex = nearestIndex;
        growthChartHoveredParam = closestParam;
        renderGrowthChart();
        renderGrowthTooltip(nearestIndex, pointX, targetY, closestParam, width, height);
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
        growthChartCanvas.addEventListener("mousemove", handleGrowthPointerMove);
        growthChartCanvas.addEventListener("mouseleave", handleGrowthPointerLeave);
        growthChartCanvas.addEventListener("touchmove", (e) => {
            if (e.touches && e.touches[0]) handleGrowthPointerMove(e.touches[0]);
        }, { passive: true });
        growthChartCanvas.addEventListener("touchend", handleGrowthPointerLeave);
    }"""

if old_handler in js:
    js = js.replace(old_handler, new_handler)
    print("Replaced handleGrowthPointerMove successfully")
else:
    print("WARNING: old_handler not found!")

# 3. Update renderGrowthTooltip positioning calculation
old_tt_render = """        // Calculate dynamic dimensions matching water quality trends
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
        growthTooltip.style.top = `${topPos}px`;"""

new_tt_render = """        // Calculate dynamic dimensions matching water quality trends
        const tooltipWidth = growthTooltip.offsetWidth || 290;
        const tooltipHeight = growthTooltip.offsetHeight || 220;

        let leftPos = pointX + 16;
        if (leftPos + tooltipWidth > containerWidth - 12) {
            leftPos = pointX - tooltipWidth - 16;
        }
        if (leftPos < 12) leftPos = 12;

        let topPos = focusedParam && targetY !== undefined ? targetY - (tooltipHeight / 2) : targetY - (tooltipHeight / 2);
        topPos = Math.max(8, Math.min(containerHeight - 50, topPos));
        if (topPos + tooltipHeight > containerHeight + 80) {
            topPos = Math.max(8, containerHeight + 80 - tooltipHeight);
        }

        growthTooltip.style.left = `${Math.round(leftPos)}px`;
        growthTooltip.style.top = `${Math.round(topPos)}px`;"""

if old_tt_render in js:
    js = js.replace(old_tt_render, new_tt_render)
    print("Replaced tooltip position calculation successfully")
else:
    print("WARNING: old_tt_render not found!")

with open("static/js/calculators.js", "w", encoding="utf-8", newline="\r\n") as f:
    f.write(js)

print("Updated static/js/calculators.js successfully.")
