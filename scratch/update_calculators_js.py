with open("static/js/calculators.js", "r", encoding="utf-8") as f:
    js = f.read()

def normalize(text):
    return text.replace("\r\n", "\n")

js_norm = normalize(js)

# 1. updateLiveSensorIndicators
target_live = """        // Live Ammonia indicators
        const ammLiveTemp = document.getElementById("tools-ammonia-live-temp");
        const ammLivePh = document.getElementById("tools-ammonia-live-ph");
        if (ammLiveTemp) ammLiveTemp.textContent = liveSensor.temperature.toFixed(1);
        if (ammLivePh) ammLivePh.textContent = liveSensor.ph.toFixed(2);"""

replacement_live = """        // Live Ammonia indicators
        const ammLiveTemp = document.getElementById("tools-ammonia-live-temp");
        const ammLivePh = document.getElementById("tools-ammonia-live-ph");
        if (ammLiveTemp) ammLiveTemp.textContent = liveSensor.temperature.toFixed(1);
        if (ammLivePh) ammLivePh.textContent = liveSensor.ph.toFixed(2);

        // Live CO2 indicators
        const co2LiveTemp = document.getElementById("tools-co2-live-temp");
        const co2LivePh = document.getElementById("tools-co2-live-ph");
        if (co2LiveTemp) co2LiveTemp.textContent = liveSensor.temperature.toFixed(1);
        if (co2LivePh) co2LivePh.textContent = liveSensor.ph.toFixed(2);

        const co2OverrideCbCheck = document.getElementById("tools-co2-override-cb");
        if (!co2OverrideCbCheck || !co2OverrideCbCheck.checked) {
            calculateCo2Tool();
        }"""

assert normalize(target_live) in js_norm, "target_live not found"
js_norm = js_norm.replace(normalize(target_live), normalize(replacement_live), 1)

# 2. Add CO2 Tool Implementation after Van Wyk modal code
target_after_vanwyk = """    if (modal) {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) closeModal();
        });
    }"""

co2_tool_code = """    if (modal) {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) closeModal();
        });
    }

    // -------------------------------------------------------------
    // TOOL 5: Free Carbon Dioxide (CO2) Calculator & Tucker Matrix
    // -------------------------------------------------------------
    const TUCKER_TEMPS = [5, 10, 15, 20, 25, 30, 35];
    const TUCKER_PHS = [6.0, 6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4];
    const TUCKER_TABLE = {
        6.0: [2.915, 2.539, 2.315, 2.112, 1.970, 1.882, 1.839],
        6.2: [1.839, 1.602, 1.460, 1.333, 1.244, 1.187, 1.160],
        6.4: [1.160, 1.010, 0.921, 0.841, 0.784, 0.749, 0.732],
        6.6: [0.732, 0.637, 0.582, 0.531, 0.495, 0.473, 0.462],
        6.8: [0.462, 0.402, 0.367, 0.335, 0.313, 0.298, 0.291],
        7.0: [0.291, 0.254, 0.232, 0.211, 0.197, 0.188, 0.184],
        7.2: [0.184, 0.160, 0.146, 0.133, 0.124, 0.119, 0.116],
        7.4: [0.116, 0.101, 0.092, 0.084, 0.078, 0.075, 0.073],
        7.6: [0.073, 0.064, 0.058, 0.053, 0.050, 0.047, 0.046],
        7.8: [0.046, 0.040, 0.037, 0.034, 0.031, 0.030, 0.030],
        8.0: [0.029, 0.025, 0.023, 0.021, 0.020, 0.019, 0.018],
        8.2: [0.018, 0.016, 0.015, 0.013, 0.012, 0.012, 0.011],
        8.4: [0.012, 0.010, 0.009, 0.008, 0.008, 0.008, 0.007]
    };

    function getTuckerFactor(tempC, phVal) {
        if (phVal > 8.4) {
            return 0.001;
        }

        const tClamped = Math.max(5.0, Math.min(35.0, tempC));
        const pClamped = Math.max(6.0, Math.min(8.4, phVal));

        // Temperature interval
        let tIdx = 0;
        while (tIdx < TUCKER_TEMPS.length - 1 && TUCKER_TEMPS[tIdx + 1] <= tClamped) {
            tIdx++;
        }
        const t1 = TUCKER_TEMPS[tIdx];
        const t2Idx = Math.min(tIdx + 1, TUCKER_TEMPS.length - 1);
        const t2 = TUCKER_TEMPS[t2Idx];
        const u = (t1 === t2) ? 0 : (tClamped - t1) / (t2 - t1);

        // pH interval
        let pIdx = 0;
        while (pIdx < TUCKER_PHS.length - 1 && TUCKER_PHS[pIdx + 1] <= pClamped) {
            pIdx++;
        }
        const p1 = TUCKER_PHS[pIdx];
        const p2Idx = Math.min(pIdx + 1, TUCKER_PHS.length - 1);
        const p2 = TUCKER_PHS[p2Idx];
        const v = (p1 === p2) ? 0 : (pClamped - p1) / (p2 - p1);

        const f11 = TUCKER_TABLE[p1][tIdx];
        const f21 = TUCKER_TABLE[p1][t2Idx];
        const f12 = TUCKER_TABLE[p2][tIdx];
        const f22 = TUCKER_TABLE[p2][t2Idx];

        const factor = (1 - u) * (1 - v) * f11 + u * (1 - v) * f21 + (1 - u) * v * f12 + u * v * f22;
        return Number(factor.toFixed(4));
    }

    function calculateCo2Tool() {
        const alkInput = document.getElementById("tools-co2-alkalinity");
        const overrideCb = document.getElementById("tools-co2-override-cb");
        const customTempInput = document.getElementById("tools-co2-custom-temp");
        const customPhInput = document.getElementById("tools-co2-custom-ph");

        const alk = Math.max(0, Number(alkInput?.value || 140));
        const isOverride = overrideCb && overrideCb.checked;

        const temp = isOverride ? Number(customTempInput?.value || 28.0) : liveSensor.temperature;
        const ph = isOverride ? Number(customPhInput?.value || 7.60) : liveSensor.ph;

        const factor = getTuckerFactor(temp, ph);
        const co2 = factor * alk;

        // Step outputs
        const stepTempEl = document.getElementById("tools-co2-step-temp");
        const stepPhEl = document.getElementById("tools-co2-step-ph");
        const stepFactorEl = document.getElementById("tools-co2-step-factor");
        const stepMathEl = document.getElementById("tools-co2-step-math");
        const stepFinalEl = document.getElementById("tools-co2-step-final");
        const resultValEl = document.getElementById("tools-co2-result");
        const badgeEl = document.getElementById("tools-co2-badge");
        const assessmentBox = document.getElementById("tools-co2-assessment");
        const assessmentText = document.getElementById("tools-co2-assessment-text");
        const sensitivityNote = document.getElementById("tools-co2-sensitivity");

        if (stepTempEl) stepTempEl.textContent = `${temp.toFixed(1)} °C`;
        if (stepPhEl) stepPhEl.textContent = ph.toFixed(2);
        if (stepFactorEl) stepFactorEl.textContent = factor.toFixed(4);
        if (stepMathEl) stepMathEl.textContent = `${factor.toFixed(4)} × ${alk.toFixed(0)} mg/L`;
        if (stepFinalEl) stepFinalEl.textContent = `${co2.toFixed(3)} mg/L`;
        if (resultValEl) resultValEl.textContent = co2.toFixed(3);

        let statusBadge = "Safe (< 10.0 mg/L)";
        let statusClass = "badge-optimal";
        let assessClass = "is-safe";
        let assessDesc = "";

        if (ph > 8.4) {
            statusBadge = "Negligible (< 1.0 mg/L)";
            statusClass = "badge-optimal";
            assessClass = "is-safe";
            assessDesc = `At pH ${ph.toFixed(2)} (> 8.4), free carbon dioxide is negligible (${co2.toFixed(3)} mg/L). Carbonate equilibrium shifts virtually all inorganic carbon into bicarbonate (HCO₃⁻) and carbonate (CO₃²⁻).`;
        } else if (co2 < 10.0) {
            statusBadge = "Safe (< 10.0 mg/L)";
            statusClass = "badge-optimal";
            assessClass = "is-safe";
            assessDesc = `Free CO₂ (${co2.toFixed(3)} mg/L) is within the optimal zootechnical range (< 10.0 mg/L) for Penaeus vannamei. Hemocyanin oxygen affinity and branchial gas exchange operate normally.`;
        } else if (co2 <= 20.0) {
            statusBadge = "Elevated (10.0–20.0 mg/L)";
            statusClass = "badge-warning";
            assessClass = "is-warning";
            assessDesc = `WARNING: Free CO₂ (${co2.toFixed(3)} mg/L) is elevated (10.0–20.0 mg/L). This causes respiratory stress and reduces blood oxygen carrying capacity via the Bohr-Root effect. Increase paddlewheel aeration to degas CO₂.`;
        } else {
            statusBadge = "Critical Stress (> 20.0 mg/L)";
            statusClass = "badge-critical";
            assessClass = "is-critical";
            assessDesc = `CRITICAL HAZARD: Free CO₂ (${co2.toFixed(3)} mg/L) exceeds the critical stress threshold (> 20.0 mg/L). Severe hypercapnic acidosis and asphyxiation risk are present. Operate all surface aerators immediately to strip gas and dose lime.`;
        }

        if (badgeEl) {
            badgeEl.textContent = statusBadge;
            badgeEl.className = `wqi-metric-badge ${statusClass}`;
        }
        if (assessmentBox) {
            assessmentBox.className = `ammonia-assessment ${assessClass}`;
        }
        if (assessmentText) {
            assessmentText.textContent = assessDesc;
        }

        // Sensitivity simulation text: pre-dawn pH drop scenario
        const dawnPh = Math.max(6.0, ph - 0.3);
        const dawnFactor = getTuckerFactor(temp, dawnPh);
        const dawnCo2 = dawnFactor * alk;
        if (sensitivityNote) {
            sensitivityNote.innerHTML = `<strong>Diurnal Dynamics Insight:</strong> Free CO₂ peaks pre-dawn due to continuous overnight shrimp and plankton respiration. If nighttime respiration causes pH to drop by 0.3 (to ${dawnPh.toFixed(2)}), free CO₂ surges to <strong>${dawnCo2.toFixed(3)} mg/L</strong> (${dawnCo2 > 10.0 ? "Requires night aeration" : "Safe"}).`;
        }

        highlightTuckerMatrix(temp, ph);
    }

    function highlightTuckerMatrix(temp, ph) {
        let closestTemp = TUCKER_TEMPS[0];
        let minDiffT = Math.abs(temp - closestTemp);
        TUCKER_TEMPS.forEach(t => {
            const diff = Math.abs(temp - t);
            if (diff < minDiffT) {
                minDiffT = diff;
                closestTemp = t;
            }
        });

        let closestPh = TUCKER_PHS[0];
        let minDiffP = Math.abs(ph - closestPh);
        TUCKER_PHS.forEach(p => {
            const diff = Math.abs(ph - p);
            if (diff < minDiffP) {
                minDiffP = diff;
                closestPh = p;
            }
        });

        const matrix = document.getElementById("tools-tucker-matrix");
        if (!matrix) return;

        // Reset highlights
        matrix.querySelectorAll("td, th").forEach(cell => {
            cell.classList.remove("cell-highlight-col", "cell-highlight-row", "cell-highlight-intersect", "active-col-cell", "active-col-header", "active-intersect-cell");
        });
        matrix.querySelectorAll("tr").forEach(tr => tr.classList.remove("active-row"));

        // Highlight header col
        const thCol = matrix.querySelector(`th[data-temp="${closestTemp}"]`);
        if (thCol) {
            thCol.classList.add("cell-highlight-col", "active-col-header");
        }

        // Highlight col cells in body
        matrix.querySelectorAll(`tbody td[data-temp="${closestTemp}"]`).forEach(td => {
            td.classList.add("cell-highlight-col", "active-col-cell");
        });

        // Highlight row
        const trRow = matrix.querySelector(`tr[data-ph="${closestPh.toFixed(1)}"]`);
        if (trRow) {
            trRow.classList.add("active-row");
            trRow.querySelectorAll("td").forEach(td => td.classList.add("cell-highlight-row"));
            const targetCell = trRow.querySelector(`td[data-temp="${closestTemp}"]`);
            if (targetCell) {
                targetCell.classList.remove("cell-highlight-row", "cell-highlight-col", "active-col-cell");
                targetCell.classList.add("cell-highlight-intersect", "active-intersect-cell");
            }
        }
    }

    // Modal open/close for Tucker matrix
    const tuckerModal = document.getElementById("tools-tucker-modal");
    const openTuckerBtn = document.getElementById("open-tools-tucker");
    const closeTuckerBtn = document.getElementById("close-tools-tucker");
    const closeTuckerActionBtn = document.getElementById("tools-tucker-modal-close-action");

    function openTuckerModal() {
        if (tuckerModal) tuckerModal.hidden = false;
    }
    function closeTuckerModal() {
        if (tuckerModal) tuckerModal.hidden = true;
    }

    if (openTuckerBtn) openTuckerBtn.addEventListener("click", openTuckerModal);
    if (closeTuckerBtn) closeTuckerBtn.addEventListener("click", closeTuckerModal);
    if (closeTuckerActionBtn) closeTuckerActionBtn.addEventListener("click", closeTuckerModal);
    if (tuckerModal) {
        tuckerModal.addEventListener("click", (e) => {
            if (e.target === tuckerModal) closeTuckerModal();
        });
    }"""

assert normalize(target_after_vanwyk) in js_norm, "target_after_vanwyk not found"
js_norm = js_norm.replace(normalize(target_after_vanwyk), normalize(co2_tool_code), 1)

# 3. Input event listeners for CO2
target_custom_inputs = """    const customTempInput = document.getElementById("tools-custom-temp");
    const customPhInput = document.getElementById("tools-custom-ph");
    if (customTempInput) customTempInput.addEventListener("input", calculateAmmoniaTool);
    if (customPhInput) customPhInput.addEventListener("input", calculateAmmoniaTool);"""

replacement_custom_inputs = """    const customTempInput = document.getElementById("tools-custom-temp");
    const customPhInput = document.getElementById("tools-custom-ph");
    if (customTempInput) customTempInput.addEventListener("input", calculateAmmoniaTool);
    if (customPhInput) customPhInput.addEventListener("input", calculateAmmoniaTool);

    // CO2 Inputs & Presets
    const co2AlkInput = document.getElementById("tools-co2-alkalinity");
    if (co2AlkInput) {
        co2AlkInput.addEventListener("input", calculateCo2Tool);
        co2AlkInput.addEventListener("change", calculateCo2Tool);
    }

    const co2CalcBtn = document.getElementById("tools-co2-calc-btn");
    if (co2CalcBtn) {
        co2CalcBtn.addEventListener("click", calculateCo2Tool);
    }

    const co2PresetChips = document.querySelectorAll("#tools-co2-preset-chips .preset-chip");
    co2PresetChips.forEach(chip => {
        chip.addEventListener("click", () => {
            co2PresetChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            if (co2AlkInput) {
                co2AlkInput.value = chip.dataset.alk;
                calculateCo2Tool();
            }
        });
    });

    const co2OverrideCb = document.getElementById("tools-co2-override-cb");
    const co2OverrideFields = document.getElementById("tools-co2-override-fields");
    if (co2OverrideCb && co2OverrideFields) {
        co2OverrideCb.addEventListener("change", () => {
            co2OverrideFields.hidden = !co2OverrideCb.checked;
            calculateCo2Tool();
        });
    }

    const co2CustomTempInput = document.getElementById("tools-co2-custom-temp");
    const co2CustomPhInput = document.getElementById("tools-co2-custom-ph");
    if (co2CustomTempInput) co2CustomTempInput.addEventListener("input", calculateCo2Tool);
    if (co2CustomPhInput) co2CustomPhInput.addEventListener("input", calculateCo2Tool);"""

assert normalize(target_custom_inputs) in js_norm, "target_custom_inputs not found"
js_norm = js_norm.replace(normalize(target_custom_inputs), normalize(replacement_custom_inputs), 1)

# 4. collectCurrentCalculations: add CO2
target_collect_nh3 = """            // 7. Ammonia
            ammonia_tan_ppm: tanVal,
            ammonia_temp_c: ammTemp,
            ammonia_ph: ammPh,
            ammonia_salinity_ppt: ammSal,
            ammonia_factor_f: ammFactor * 100.0,
            ammonia_nh3_ppm: nh3Val,
            ammonia_status: nh3Status
        };"""

replacement_collect_nh3 = """            // 7. Ammonia
            ammonia_tan_ppm: tanVal,
            ammonia_temp_c: ammTemp,
            ammonia_ph: ammPh,
            ammonia_salinity_ppt: ammSal,
            ammonia_factor_f: ammFactor * 100.0,
            ammonia_nh3_ppm: nh3Val,
            ammonia_status: nh3Status,
            // 8. Free Carbon Dioxide
            co2_alkalinity_mg_l: co2AlkVal,
            co2_temp_c: co2Temp,
            co2_ph: co2Ph,
            co2_factor: co2Factor,
            co2_concentration_mg_l: co2Val,
            co2_status: co2Status
        };"""

target_collect_pre = """        // 5. Ammonia
        const tanVal = Number(document.getElementById("tools-ammonia-tan")?.value || 0.8);
        const isOverride = document.getElementById("tools-ammonia-override-cb")?.checked;
        const ammTemp = isOverride ? Number(document.getElementById("tools-custom-temp")?.value || 28.0) : liveSensor.temperature;
        const ammPh = isOverride ? Number(document.getElementById("tools-custom-ph")?.value || 7.60) : liveSensor.ph;
        const ammSal = 18.0;
        const ammFactor = getVanWykFactor(ammTemp, ammPh);
        const nh3Val = ammFactor * tanVal;
        const nh3Status = nh3Val < 0.05 ? "Optimal" : (nh3Val <= 0.10 ? "Warning" : "Critical");"""

replacement_collect_pre = """        // 5. Ammonia
        const tanVal = Number(document.getElementById("tools-ammonia-tan")?.value || 0.8);
        const isOverride = document.getElementById("tools-ammonia-override-cb")?.checked;
        const ammTemp = isOverride ? Number(document.getElementById("tools-custom-temp")?.value || 28.0) : liveSensor.temperature;
        const ammPh = isOverride ? Number(document.getElementById("tools-custom-ph")?.value || 7.60) : liveSensor.ph;
        const ammSal = 18.0;
        const ammFactor = getVanWykFactor(ammTemp, ammPh);
        const nh3Val = ammFactor * tanVal;
        const nh3Status = nh3Val < 0.05 ? "Optimal" : (nh3Val <= 0.10 ? "Warning" : "Critical");

        // 6. Carbon Dioxide
        const co2AlkVal = Number(document.getElementById("tools-co2-alkalinity")?.value || 140);
        const isCo2Override = document.getElementById("tools-co2-override-cb")?.checked;
        const co2Temp = isCo2Override ? Number(document.getElementById("tools-co2-custom-temp")?.value || 28.0) : liveSensor.temperature;
        const co2Ph = isCo2Override ? Number(document.getElementById("tools-co2-custom-ph")?.value || 7.60) : liveSensor.ph;
        const co2Factor = getTuckerFactor(co2Temp, co2Ph);
        const co2Val = co2Factor * co2AlkVal;
        const co2Status = co2Ph > 8.4 ? "Negligible" : (co2Val < 10.0 ? "Safe" : (co2Val <= 20.0 ? "Elevated" : "Critical"));"""

assert normalize(target_collect_pre) in js_norm, "target_collect_pre not found"
js_norm = js_norm.replace(normalize(target_collect_pre), normalize(replacement_collect_pre), 1)

assert normalize(target_collect_nh3) in js_norm, "target_collect_nh3 not found"
js_norm = js_norm.replace(normalize(target_collect_nh3), normalize(replacement_collect_nh3), 1)

# 5. openSaveModal preview item
target_save_nh3 = """        setVal("save-preview-nh3", `${cur.ammonia_nh3_ppm.toFixed(3)} ppm`);"""
replacement_save_nh3 = """        setVal("save-preview-nh3", `${cur.ammonia_nh3_ppm.toFixed(3)} ppm`);
        setVal("save-preview-co2", `${cur.co2_concentration_mg_l.toFixed(2)} mg/L`);"""

assert normalize(target_save_nh3) in js_norm, "target_save_nh3 not found"
js_norm = js_norm.replace(normalize(target_save_nh3), normalize(replacement_save_nh3), 1)

# 6. boot() calling calculateCo2Tool()
target_boot = """        calculateAmmoniaTool();
        calculateMasterGrowth();"""

replacement_boot = """        calculateAmmoniaTool();
        calculateCo2Tool();
        calculateMasterGrowth();"""

assert normalize(target_boot) in js_norm, "target_boot not found"
js_norm = js_norm.replace(normalize(target_boot), normalize(replacement_boot), 1)

# 7. updateExportPreview module count: update 7 to catCheckboxes.length
target_export_preview_len = """            previewText.textContent = `Exporting ${selectedCats.length} of 7 modules • ${scopeText} • Format: ${format.toUpperCase()}`;"""
replacement_export_preview_len = """            previewText.textContent = `Exporting ${selectedCats.length} of ${catCheckboxes.length} modules • ${scopeText} • Format: ${format.toUpperCase()}`;"""

assert normalize(target_export_preview_len) in js_norm, "target_export_preview_len not found"
js_norm = js_norm.replace(normalize(target_export_preview_len), normalize(replacement_export_preview_len), 1)

# 8. Add ESC key support for Tucker modal
target_esc = """    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && growthGraphModal && !growthGraphModal.hidden) {
            closeGrowthGraphModal();
        }
    });"""

replacement_esc = """    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && growthGraphModal && !growthGraphModal.hidden) {
            closeGrowthGraphModal();
        }
        if (e.key === "Escape" && tuckerModal && !tuckerModal.hidden) {
            closeTuckerModal();
        }
    });"""

assert normalize(target_esc) in js_norm, "target_esc not found"
js_norm = js_norm.replace(normalize(target_esc), normalize(replacement_esc), 1)

with open("static/js/calculators.js", "w", encoding="utf-8") as f:
    f.write(js_norm)

print("Successfully updated static/js/calculators.js!")
