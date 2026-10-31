with open("static/js/calculators.js", "r", encoding="utf-8") as f:
    content = f.read()

target = "    async function boot() {"

js_block = """    // -------------------------------------------------------------
    // TOOL SNAPSHOT PERSISTENCE & CUSTOM EXPORT SYSTEM
    // -------------------------------------------------------------
    function collectCurrentCalculations(customNotes) {
        // 1. Biomass & Feed
        const area = Number(document.getElementById("feed-pond-area")?.value || 1000);
        const depth = Number(document.getElementById("feed-pond-depth")?.value || 1.2);
        const density = Number(document.getElementById("feed-stocking-density")?.value || 60);
        const survival = Number(document.getElementById("feed-survival-rate")?.value || 85);
        const abw = Number(document.getElementById("feed-abw")?.value || 15.0);
        const feedRatePct = Number(document.getElementById("feed-rate-percent")?.value || 3.2);
        const meals = Number(document.getElementById("feed-meals-day")?.value || 4);
        const currentTemp = Number(document.getElementById("feed-current-temp")?.value || liveSensor.temperature);

        const totalStocked = area * density;
        const survivingPopulation = Math.round(totalStocked * (survival / 100.0));
        const biomassKg = (survivingPopulation * abw) / 1000.0;
        const biomassTons = biomassKg / 1000.0;
        const baseDailyFeed = biomassKg * (feedRatePct / 100.0);

        let tempFactor = 1.0;
        if (currentTemp >= 28.0 && currentTemp <= 32.0) tempFactor = 1.00;
        else if (currentTemp > 32.0 && currentTemp <= 33.5) tempFactor = 0.85;
        else if (currentTemp > 33.5) tempFactor = 0.50;
        else if (currentTemp >= 26.0 && currentTemp < 28.0) tempFactor = 0.75;
        else tempFactor = 0.40;

        const adjustedDailyFeed = baseDailyFeed * tempFactor;
        const feedPerMeal = adjustedDailyFeed / meals;

        // 2. Liming
        const limeVol = Number(document.getElementById("lime-pond-vol")?.value || 1200);
        const limeCurrentPh = Number(document.getElementById("lime-current-ph")?.value || 7.10);
        const limeTargetPh = Number(document.getElementById("lime-target-ph")?.value || 8.00);
        const limeChem = document.getElementById("lime-chemical-type")?.value || "caco3";
        let limeFactor = 0.050;
        let limeChemName = "Agricultural Limestone (CaCO3)";
        if (limeChem === "dolomite") { limeFactor = 0.060; limeChemName = "Dolomite [CaMg(CO3)2]"; }
        else if (limeChem === "caoh2") { limeFactor = 0.035; limeChemName = "Hydrated Lime [Ca(OH)2]"; }
        const deltaPh = Math.max(0, limeTargetPh - limeCurrentPh);
        const limeKg = limeVol * deltaPh * limeFactor;
        const limePpm = limeVol > 0 ? (limeKg * 1000.0) / limeVol : 0;

        // 3. Carbon Dosing (Biofloc)
        const molFeed = Number(document.getElementById("molasses-daily-feed")?.value || 25.0);
        const molProtein = Number(document.getElementById("molasses-protein-pct")?.value || 35);
        const molTargetCn = Number(document.getElementById("molasses-target-cn")?.value || 15);
        const molSource = document.getElementById("molasses-carbon-source")?.value || "cane_molasses";
        const nInFeed = molFeed * (molProtein / 100.0) * 0.16;
        const cInFeed = molFeed * 0.50;
        const cDeficit = Math.max(0, (nInFeed * molTargetCn) - cInFeed);
        let cPct = 0.40;
        let cSourceName = "Cane Molasses";
        if (molSource === "white_sugar") { cPct = 0.42; cSourceName = "Refined White Sugar"; }
        else if (molSource === "cassava_flour") { cPct = 0.45; cSourceName = "Cassava / Rice Flour"; }
        const molKg = cDeficit / cPct;

        // 4. Aerator Power
        const aeroBiomass = Number(document.getElementById("aero-biomass-input")?.value || biomassKg);
        const aeroTemp = Number(document.getElementById("aero-temp-input")?.value || liveSensor.temperature);
        const kgPerHp = aeroTemp > 30.0 ? 320.0 : 400.0;
        const aeroHp = Math.max(1.0, Math.ceil((aeroBiomass / kgPerHp) * 2) / 2);
        let aeroUnits = aeroHp <= 1.0 ? "1 × 1-HP unit" : (aeroHp <= 2.0 ? "1 × 2-HP or 2 × 1-HP units" : `${Math.floor(aeroHp / 2.0)} × 2-HP units`);

        // 5. Ammonia
        const tanVal = Number(document.getElementById("tools-ammonia-tan")?.value || 0.8);
        const isOverride = document.getElementById("tools-ammonia-override-cb")?.checked;
        const ammTemp = isOverride ? Number(document.getElementById("tools-custom-temp")?.value || 28.0) : liveSensor.temperature;
        const ammPh = isOverride ? Number(document.getElementById("tools-custom-ph")?.value || 7.60) : liveSensor.ph;
        const ammSal = 18.0;
        const ammFactor = getVanWykFactor(ammTemp, ammPh);
        const nh3Val = ammFactor * tanVal;
        const nh3Status = nh3Val < 0.05 ? "Optimal" : (nh3Val <= 0.10 ? "Warning" : "Critical");

        // 6. Growth Master Equations
        const isVal = Number(document.getElementById("gm-initial-stocking")?.value || 100000);
        const lhcVal = Number(document.getElementById("gm-live-harvest-count")?.value || 85000);
        const docVal = Number(document.getElementById("gm-days-of-culture")?.value || 90);
        const ibw = Number(document.getElementById("gm-initial-weight")?.value || 0.010);
        const bwVal = Number(document.getElementById("gm-bulk-weight")?.value || 1700);
        const bwUnit = document.getElementById("gm-bw-unit")?.value || "kg";
        const tfgVal = Number(document.getElementById("gm-total-feed")?.value || 2125);
        const feedUnit = document.getElementById("gm-feed-unit")?.value || "kg";
        const tlVal = Number(document.getElementById("gm-total-length")?.value || 12.9);

        const bwGrams = bwUnit === "kg" ? bwVal * 1000.0 : bwVal;
        const bwKg = bwGrams / 1000.0;
        const tfgKg = feedUnit === "kg" ? tfgVal : tfgVal / 1000.0;
        const srVal = (lhcVal / isVal) * 100.0;
        const mortCount = Math.max(0, isVal - lhcVal);
        const fabwVal = bwGrams / lhcVal;
        const countPerKg = fabwVal > 0 ? (1000.0 / fabwVal) : 0;
        const adwgVal = (fabwVal - ibw) / docVal;
        const weeklyGain = adwgVal * 7.0;
        const sgrVal = ((Math.log(fabwVal) - Math.log(ibw)) / docVal) * 100.0;
        const ibKg = (isVal * ibw) / 1000.0;
        const fbKg = (lhcVal * fabwVal) / 1000.0;
        const netGainKg = Math.max(0.0001, fbKg - ibKg);
        const fcrVal = tfgKg / netGainKg;
        const feedEff = fcrVal > 0 ? (100.0 / fcrVal) : 0;
        const kFactor = (fabwVal / Math.pow(tlVal, 3)) * 100.0;
        const kProfile = kFactor >= 0.80 && kFactor <= 1.15 ? "Optimal Condition (0.80–1.15)" : (kFactor < 0.80 ? "Slender / Lean (<0.80)" : "Heavy / Plump (>1.15)");

        return {
            notes: (customNotes || `Pond Calculation - DOC ${docVal}`).trim(),
            // 1. Biomass
            pond_area_m2: area,
            pond_depth_m: depth,
            stocking_density_pl_m2: density,
            survival_rate_pct: survival,
            abw_g: abw,
            standing_biomass_kg: biomassKg,
            standing_biomass_tons: biomassTons,
            active_shrimp_count: survivingPopulation,
            // 2. Temp Feeding
            water_temperature_c: currentTemp,
            base_feeding_rate_pct: feedRatePct,
            temp_feeding_factor: tempFactor,
            adjusted_daily_feed_kg: adjustedDailyFeed,
            feed_per_meal_kg: feedPerMeal,
            feedings_per_day: meals,
            // 3. Growth Eqs
            is_count: isVal,
            lhc_count: lhcVal,
            doc_days: docVal,
            ibw_g: ibw,
            bulk_weight_kg: bwKg,
            total_feed_given_kg: tfgKg,
            total_length_cm: tlVal,
            eq1_sr_pct: srVal,
            eq1_mortality_count: mortCount,
            eq2_fabw_g: fabwVal,
            eq2_count_per_kg: countPerKg,
            eq3_adwg_g_day: adwgVal,
            eq3_weekly_gain_g: weeklyGain,
            eq4_sgr_pct_day: sgrVal,
            eq5_ib_kg: ibKg,
            eq6_fb_kg: fbKg,
            eq5_6_net_biomass_kg: netGainKg,
            eq7_fcr: fcrVal,
            eq7_feed_efficiency_pct: feedEff,
            eq8_fulton_k: kFactor,
            eq8_fulton_profile: kProfile,
            // 4. Liming
            lime_pond_vol_m3: limeVol,
            lime_current_ph: limeCurrentPh,
            lime_target_ph: limeTargetPh,
            lime_chemical_type: limeChemName,
            lime_dosage_kg: limeKg,
            lime_dosage_ppm: limePpm,
            // 5. Carbon
            molasses_daily_feed_kg: molFeed,
            molasses_protein_pct: molProtein,
            molasses_target_cn: molTargetCn,
            molasses_carbon_source: cSourceName,
            molasses_dosage_kg: molKg,
            // 6. Aeration
            aero_biomass_kg: aeroBiomass,
            aero_water_temp_c: aeroTemp,
            aero_salinity_ppt: ammSal,
            aero_target_do_ppm: 5.0,
            aero_power_hp: aeroHp,
            aero_units_desc: aeroUnits,
            // 7. Ammonia
            ammonia_tan_ppm: tanVal,
            ammonia_temp_c: ammTemp,
            ammonia_ph: ammPh,
            ammonia_salinity_ppt: ammSal,
            ammonia_factor_f: ammFactor * 100.0,
            ammonia_nh3_ppm: nh3Val,
            ammonia_status: nh3Status
        };
    }

    // Modal helpers
    const saveModalBackdrop = document.getElementById("tools-save-modal");
    const closeSaveModalBtn = document.getElementById("close-save-modal");
    const cancelSaveModalBtn = document.getElementById("cancel-save-modal-btn");
    const confirmSaveModalBtn = document.getElementById("confirm-save-modal-btn");
    const btnOpenSaveModal = document.getElementById("btn-open-save-modal");
    const saveCalcNotes = document.getElementById("save-calc-notes");
    const saveStatusMsg = document.getElementById("save-calc-status-message");

    function openSaveModal() {
        if (!saveModalBackdrop) return;
        const cur = collectCurrentCalculations();
        const setVal = (id, text) => {
            const el = document.getElementById(id);
            if (el) el.textContent = text;
        };
        setVal("save-preview-biomass", `${cur.standing_biomass_kg.toLocaleString(undefined, {maximumFractionDigits: 1})} kg`);
        setVal("save-preview-feed", `${cur.adjusted_daily_feed_kg.toFixed(1)} kg/day`);
        setVal("save-preview-sr", `${cur.eq1_sr_pct.toFixed(2)} %`);
        setVal("save-preview-fabw", `${cur.eq2_fabw_g.toFixed(2)} g`);
        setVal("save-preview-adwg", `${cur.eq3_adwg_g_day.toFixed(3)} g/day`);
        setVal("save-preview-sgr", `${cur.eq4_sgr_pct_day.toFixed(2)} %/day`);
        setVal("save-preview-fcr", cur.eq7_fcr.toFixed(2));
        setVal("save-preview-k", cur.eq8_fulton_k.toFixed(4));
        setVal("save-preview-lime", `${cur.lime_dosage_kg.toFixed(1)} kg`);
        setVal("save-preview-carbon", `${cur.molasses_dosage_kg.toFixed(1)} kg`);
        setVal("save-preview-aeration", `${cur.aero_power_hp.toFixed(1)} HP`);
        setVal("save-preview-nh3", `${cur.ammonia_nh3_ppm.toFixed(3)} ppm`);

        if (saveCalcNotes) {
            saveCalcNotes.value = `Pond 1 - DOC ${cur.doc_days} Run`;
        }
        if (saveStatusMsg) {
            saveStatusMsg.hidden = true;
            saveStatusMsg.textContent = "";
            saveStatusMsg.className = "save-status-msg";
        }
        if (confirmSaveModalBtn) {
            confirmSaveModalBtn.disabled = false;
            confirmSaveModalBtn.innerHTML = `
                <svg class="ui-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <span>Confirm &amp; Save to Database</span>
            `;
        }
        saveModalBackdrop.hidden = false;
        document.body.style.overflow = "hidden";
    }

    function closeSaveModal() {
        if (!saveModalBackdrop) return;
        saveModalBackdrop.hidden = true;
        document.body.style.overflow = "";
    }

    if (btnOpenSaveModal) btnOpenSaveModal.addEventListener("click", openSaveModal);
    if (closeSaveModalBtn) closeSaveModalBtn.addEventListener("click", closeSaveModal);
    if (cancelSaveModalBtn) cancelSaveModalBtn.addEventListener("click", closeSaveModal);
    if (saveModalBackdrop) {
        saveModalBackdrop.addEventListener("click", (e) => {
            if (e.target === saveModalBackdrop) closeSaveModal();
        });
    }

    if (confirmSaveModalBtn) {
        confirmSaveModalBtn.addEventListener("click", async () => {
            confirmSaveModalBtn.disabled = true;
            confirmSaveModalBtn.innerHTML = `<span>Saving to MySQL...</span>`;

            const notesText = saveCalcNotes ? saveCalcNotes.value : "";
            const payload = collectCurrentCalculations(notesText);

            try {
                const res = await fetch("/api/calculators/save", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                if (res.ok && result.success) {
                    if (saveStatusMsg) {
                        saveStatusMsg.hidden = false;
                        saveStatusMsg.className = "save-status-msg status-success";
                        saveStatusMsg.textContent = `✓ ${result.message || 'Snapshot successfully saved!'}`;
                    }
                    setTimeout(() => {
                        closeSaveModal();
                    }, 1400);
                } else {
                    throw new Error(result.error || "Failed to save record.");
                }
            } catch (err) {
                if (saveStatusMsg) {
                    saveStatusMsg.hidden = false;
                    saveStatusMsg.className = "save-status-msg status-error";
                    saveStatusMsg.textContent = `✗ Error: ${err.message}`;
                }
                confirmSaveModalBtn.disabled = false;
                confirmSaveModalBtn.innerHTML = `<span>Retry Save</span>`;
            }
        });
    }

    // Export Modal helpers
    const exportModalBackdrop = document.getElementById("tools-export-modal");
    const closeExportModalBtn = document.getElementById("close-tools-export-modal");
    const cancelExportModalBtn = document.getElementById("cancel-tools-export-btn");
    const confirmExportModalBtn = document.getElementById("confirm-tools-export-btn");
    const btnOpenExportModal = document.getElementById("btn-open-export-modal");
    const btnSelectAllCats = document.getElementById("export-cat-select-all");
    const btnClearAllCats = document.getElementById("export-cat-clear-all");
    const dateRangeSelect = document.getElementById("tools-export-date-range");
    const customDateInput = document.getElementById("tools-export-custom-date");
    const scopeRadios = document.querySelectorAll('input[name="tools-export-scope"]');
    const formatRadios = document.querySelectorAll('input[name="tools-export-format"]');
    const catCheckboxes = document.querySelectorAll('input[name="export-category"]');
    const previewBadge = document.getElementById("tools-export-preview-badge");
    const previewText = document.getElementById("tools-export-preview-text");
    const confirmExportText = document.getElementById("confirm-tools-export-text");
    const dateBoxWrap = document.getElementById("tools-export-date-box");

    let savedRecordsCount = null;

    async function updateExportPreview() {
        const selectedCats = Array.from(catCheckboxes).filter(cb => cb.checked).map(cb => cb.value);
        const scope = document.querySelector('input[name="tools-export-scope"]:checked')?.value || "saved";
        const format = document.querySelector('input[name="tools-export-format"]:checked')?.value || "xlsx";
        const dateRange = dateRangeSelect?.value || "all";

        if (confirmExportText) {
            confirmExportText.textContent = format === "xlsx" ? "Download Excel (.xlsx)" : "Download CSV (.csv)";
        }

        if (dateBoxWrap) {
            dateBoxWrap.style.display = scope === "saved" ? "flex" : "none";
        }

        if (selectedCats.length === 0) {
            if (previewBadge) {
                previewBadge.textContent = "No modules selected";
                previewBadge.className = "preview-badge preview-badge-warning";
            }
            if (previewText) {
                previewText.textContent = "Please select at least one calculation category to export.";
            }
            if (confirmExportModalBtn) confirmExportModalBtn.disabled = true;
            return;
        }

        if (confirmExportModalBtn) confirmExportModalBtn.disabled = false;

        let scopeText = "";
        if (scope === "current") {
            scopeText = "Active screen snapshot (1 record)";
        } else {
            const countStr = savedRecordsCount !== null ? `${savedRecordsCount} records` : "Saved history";
            const dateLabel = dateRange === "today" ? "Today" : (dateRange === "7d" ? "Past 7 days" : (dateRange === "30d" ? "Past 30 days" : "All dates"));
            scopeText = `${countStr} (${dateLabel})`;
        }

        if (previewBadge) {
            previewBadge.textContent = "Ready to Download";
            previewBadge.className = "preview-badge preview-badge-ready";
        }
        if (previewText) {
            previewText.textContent = `Exporting ${selectedCats.length} of 7 modules • ${scopeText} • Format: ${format.toUpperCase()}`;
        }
    }

    async function openExportModal() {
        if (!exportModalBackdrop) return;
        try {
            const res = await fetch("/api/calculators/history");
            if (res.ok) {
                const data = await res.json();
                savedRecordsCount = data.total_count ?? 0;
            }
        } catch (err) {
            console.error("Failed to fetch history count:", err);
        }
        updateExportPreview();
        exportModalBackdrop.hidden = false;
        document.body.style.overflow = "hidden";
    }

    function closeExportModal() {
        if (!exportModalBackdrop) return;
        exportModalBackdrop.hidden = true;
        document.body.style.overflow = "";
    }

    if (btnOpenExportModal) btnOpenExportModal.addEventListener("click", openExportModal);
    if (closeExportModalBtn) closeExportModalBtn.addEventListener("click", closeExportModal);
    if (cancelExportModalBtn) cancelExportModalBtn.addEventListener("click", closeExportModal);
    if (exportModalBackdrop) {
        exportModalBackdrop.addEventListener("click", (e) => {
            if (e.target === exportModalBackdrop) closeExportModal();
        });
    }

    if (btnSelectAllCats) {
        btnSelectAllCats.addEventListener("click", () => {
            catCheckboxes.forEach(cb => cb.checked = true);
            updateExportPreview();
        });
    }
    if (btnClearAllCats) {
        btnClearAllCats.addEventListener("click", () => {
            catCheckboxes.forEach(cb => cb.checked = false);
            updateExportPreview();
        });
    }

    catCheckboxes.forEach(cb => cb.addEventListener("change", updateExportPreview));
    scopeRadios.forEach(r => r.addEventListener("change", updateExportPreview));
    formatRadios.forEach(r => r.addEventListener("change", updateExportPreview));

    if (dateRangeSelect) {
        dateRangeSelect.addEventListener("change", () => {
            if (customDateInput) {
                customDateInput.style.display = dateRangeSelect.value === "custom" ? "inline-block" : "none";
            }
            updateExportPreview();
        });
    }
    if (customDateInput) {
        customDateInput.addEventListener("change", updateExportPreview);
    }

    if (confirmExportModalBtn) {
        confirmExportModalBtn.addEventListener("click", async () => {
            const selectedCats = Array.from(catCheckboxes).filter(cb => cb.checked).map(cb => cb.value);
            if (selectedCats.length === 0) {
                alert("Please select at least one calculation category to export.");
                return;
            }

            const scope = document.querySelector('input[name="tools-export-scope"]:checked')?.value || "saved";
            const format = document.querySelector('input[name="tools-export-format"]:checked')?.value || "xlsx";
            let dateVal = dateRangeSelect?.value || "all";
            if (dateVal === "custom" && customDateInput && customDateInput.value) {
                dateVal = customDateInput.value;
            }

            confirmExportModalBtn.disabled = true;
            confirmExportModalBtn.innerHTML = `<span>Preparing Download...</span>`;

            try {
                if (scope === "current") {
                    const currentData = collectCurrentCalculations();
                    const res = await fetch("/api/calculators/export", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            scope: "current",
                            categories: selectedCats,
                            format: format,
                            current_data: currentData
                        })
                    });

                    if (!res.ok) throw new Error("Export generation failed.");

                    const blob = await res.blob();
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = downloadUrl;
                    const disposition = res.headers.get("Content-Disposition");
                    let filename = `shrimpguard-aquaculture-calculations-snapshot.${format}`;
                    if (disposition && disposition.indexOf("filename=") !== -1) {
                        const matches = /filename[^;=\\n]*=((['"]).*?\\2|[^;\\n]*)/.exec(disposition);
                        if (matches != null && matches[1]) {
                            filename = matches[1].replace(/['"]/g, "");
                        }
                    }
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(downloadUrl);
                } else {
                    const params = new URLSearchParams({
                        scope: "saved",
                        categories: selectedCats.join(","),
                        date: dateVal,
                        format: format
                    });
                    window.location.href = `/api/calculators/export?${params.toString()}`;
                }

                setTimeout(() => {
                    closeExportModal();
                    confirmExportModalBtn.disabled = false;
                    confirmExportModalBtn.innerHTML = `
                        <svg class="ui-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 3v12"></path>
                            <polyline points="7 10 12 15 17 10"></polyline>
                            <path d="M5 17v4h14v-4"></path>
                        </svg>
                        <span>${format === "xlsx" ? "Download Excel (.xlsx)" : "Download CSV (.csv)"}</span>
                    `;
                }, 1000);
            } catch (err) {
                alert(`Export failed: ${err.message}`);
                confirmExportModalBtn.disabled = false;
                confirmExportModalBtn.innerHTML = `<span>Retry Export</span>`;
            }
        });
    }

    // Escape key closes modals
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            if (saveModalBackdrop && !saveModalBackdrop.hidden) closeSaveModal();
            if (exportModalBackdrop && !exportModalBackdrop.hidden) closeExportModal();
        }
    });

"""

norm_content = content.replace("\r\n", "\n")
norm_target = target.replace("\r\n", "\n")

if norm_target in norm_content:
    norm_content = norm_content.replace(norm_target, js_block + "\n" + norm_target)
    print("Inserted JS block successfully")
else:
    print("ERROR: Target not found in calculators.js")

with open("static/js/calculators.js", "w", encoding="utf-8") as f:
    f.write(norm_content)

print("Saved static/js/calculators.js successfully")
