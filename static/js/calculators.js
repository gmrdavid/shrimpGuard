document.addEventListener("DOMContentLoaded", function () {
    // -------------------------------------------------------------
    // Global State & Sensor Cache
    // -------------------------------------------------------------
    let liveSensor = {
        temperature: 29.5,
        ph: 8.0,
        status: "Optimal",
        recorded_at: null
    };

    const VAN_WYK_TEMPS = [24, 26, 28, 30, 32];
    const VAN_WYK_PHS = [7.0, 7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 10.0];

    // -------------------------------------------------------------
    // Device Clock
    // -------------------------------------------------------------
    function updateClock() {
        const timeEl = document.getElementById("time");
        if (timeEl) {
            timeEl.textContent = new Date().toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit"
            });
        }
    }
    updateClock();
    setInterval(updateClock, 1000);

    // -------------------------------------------------------------
    // Fetch Latest Sensor Telemetry
    // -------------------------------------------------------------
    async function fetchLatestTelemetry() {
        try {
            const response = await fetch("/api/readings/latest");
            if (!response.ok) return;
            const data = await response.json();
            if (data && data.temperature !== undefined && data.ph !== undefined) {
                liveSensor.temperature = Number(data.temperature);
                liveSensor.ph = Number(data.ph);
                liveSensor.status = data.status || "Optimal";
                liveSensor.recorded_at = data.recorded_at || null;
                updateTelemetryUI();
            }
        } catch (err) {
            console.error("Telemetry fetch error:", err);
        }
    }

    function updateTelemetryUI() {
        const tempEl = document.getElementById("telemetry-temp");
        const phEl = document.getElementById("telemetry-ph");
        const statusEl = document.getElementById("telemetry-overall-status");
        const updatedEl = document.getElementById("telemetry-updated");
        const tempStatusEl = document.getElementById("telemetry-temp-status");
        const phStatusEl = document.getElementById("telemetry-ph-status");

        if (tempEl) tempEl.textContent = liveSensor.temperature.toFixed(1);
        if (phEl) phEl.textContent = liveSensor.ph.toFixed(2);

        // ML Status classifications based strictly on model boundaries
        const temp = liveSensor.temperature;
        const ph = liveSensor.ph;

        const isTempCrit = temp <= 25.0 || temp > 33.5;
        const isTempWarn = !isTempCrit && (temp < 28.0 || temp > 32.0);
        const tempStatus = isTempCrit ? "Critical" : (isTempWarn ? "Warning" : "Optimal");

        const isPhCrit = ph < 6.50 || ph > 9.00;
        const isPhWarn = !isPhCrit && (ph < 7.50 || ph > 8.50);
        const phStatus = isPhCrit ? "Critical" : (isPhWarn ? "Warning" : "Optimal");

        if (tempStatusEl) {
            tempStatusEl.textContent = tempStatus;
            tempStatusEl.className = `telemetry-substatus status-${tempStatus.toLowerCase()}`;
        }
        if (phStatusEl) {
            phStatusEl.textContent = phStatus;
            phStatusEl.className = `telemetry-substatus status-${phStatus.toLowerCase()}`;
        }

        const overall = (tempStatus === "Critical" || phStatus === "Critical") ? "Critical" :
                        ((tempStatus === "Warning" || phStatus === "Warning") ? "Warning" : "Optimal");

        if (statusEl) {
            statusEl.textContent = overall;
            statusEl.className = `telemetry-value telemetry-status-${overall.toLowerCase()}`;
        }

        if (updatedEl) {
            updatedEl.textContent = liveSensor.recorded_at
                ? `Updated ${new Date(liveSensor.recorded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
                : "Active sensor sync";
        }

        // Live Ammonia indicators
        const ammLiveTemp = document.getElementById("tools-ammonia-live-temp");
        const ammLivePh = document.getElementById("tools-ammonia-live-ph");
        if (ammLiveTemp) ammLiveTemp.textContent = liveSensor.temperature.toFixed(1);
        if (ammLivePh) ammLivePh.textContent = liveSensor.ph.toFixed(2);
    }

    // -------------------------------------------------------------
    // TOOL 1: Biomass & Feeding Calculator
    // -------------------------------------------------------------
    function calculateBiomassAndFeed() {
        const area = Math.max(1, Number(document.getElementById("feed-pond-area")?.value || 1000));
        const depth = Math.max(0.1, Number(document.getElementById("feed-pond-depth")?.value || 1.2));
        const density = Math.max(1, Number(document.getElementById("feed-stocking-density")?.value || 60));
        const survival = Math.min(100, Math.max(5, Number(document.getElementById("feed-survival-rate")?.value || 85)));
        const abw = Math.max(0.1, Number(document.getElementById("feed-abw")?.value || 15.0));
        const feedRatePct = Math.max(0.5, Number(document.getElementById("feed-rate-percent")?.value || 3.2));
        const meals = Math.max(1, Math.min(8, Number(document.getElementById("feed-meals-day")?.value || 4)));
        const currentTemp = Number(document.getElementById("feed-current-temp")?.value || liveSensor.temperature);

        // Water Volume
        const waterVolume = area * depth;

        // Estimated Population
        const totalStocked = area * density;
        const survivingPopulation = Math.round(totalStocked * (survival / 100.0));

        // Total Biomass (kg)
        const biomassKg = (survivingPopulation * abw) / 1000.0;
        const biomassTons = biomassKg / 1000.0;

        // Base Daily Feed (kg)
        const baseDailyFeed = biomassKg * (feedRatePct / 100.0);

        // Biological Temperature Feeding Adjustment Factor for P. vannamei
        // (Vannamei optimum 28-32°C; enzyme slowdown <28°C; thermal stress >32°C)
        let tempFactor = 1.0;
        let tempBadgeText = "100% (Optimal)";
        let tempBadgeClass = "badge-optimal";
        let guidelineText = "";

        if (currentTemp >= 28.0 && currentTemp <= 32.0) {
            tempFactor = 1.00;
            tempBadgeText = "100% (Optimal)";
            tempBadgeClass = "badge-optimal";
            guidelineText = `At ${currentTemp.toFixed(1)} °C, water temperature is in the ML optimal range (28.0–32.0 °C). Full normal feed ration recommended.`;
        } else if (currentTemp > 32.0 && currentTemp <= 33.5) {
            tempFactor = 0.85;
            tempBadgeText = "85% (-15% Warm Stress)";
            tempBadgeClass = "badge-warning";
            guidelineText = `At ${currentTemp.toFixed(1)} °C (elevated temperature), shrimp metabolism is accelerated and dissolved oxygen drops. Reduce feed by 15% to prevent uneaten decay.`;
        } else if (currentTemp > 33.5) {
            tempFactor = 0.50;
            tempBadgeText = "50% (-50% Critical Heat)";
            tempBadgeClass = "badge-critical";
            guidelineText = `At ${currentTemp.toFixed(1)} °C (critical thermal threshold), shrimp reduce feeding and oxygen demand is extreme. Cut feed in half; monitor check trays closely.`;
        } else if (currentTemp >= 26.0 && currentTemp < 28.0) {
            tempFactor = 0.75;
            tempBadgeText = "75% (-25% Cool Water)";
            tempBadgeClass = "badge-warning";
            guidelineText = `At ${currentTemp.toFixed(1)} °C, shrimp gastric emptying time slows significantly. Reduce daily feed ration by 25% to avoid feed rotting on pond bottom.`;
        } else {
            // < 26.0 °C
            tempFactor = 0.40;
            tempBadgeText = "40% (-60% Cold Stress)";
            tempBadgeClass = "badge-critical";
            guidelineText = `At ${currentTemp.toFixed(1)} °C (cold temperature), digestive protease enzyme activity drops below 40%. Feed minimally (40% ration) or halt until temperature recovers.`;
        }

        const adjustedDailyFeed = baseDailyFeed * tempFactor;
        const feedPerMeal = adjustedDailyFeed / meals;

        // Update DOM
        const bKgEl = document.getElementById("res-biomass-kg");
        const bTonsEl = document.getElementById("res-biomass-tons");
        const sCountEl = document.getElementById("res-shrimp-count");
        const tFactorEl = document.getElementById("res-temp-factor");
        const tBadgeEl = document.getElementById("res-temp-badge");
        const tGuideEl = document.getElementById("res-temp-guideline");
        const adjFeedEl = document.getElementById("res-adjusted-feed");
        const perMealEl = document.getElementById("res-per-meal");
        const baseFeedEl = document.getElementById("res-base-feed");

        if (bKgEl) bKgEl.textContent = biomassKg.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 });
        if (bTonsEl) bTonsEl.textContent = `(${biomassTons.toFixed(2)} metric tons)`;
        if (sCountEl) sCountEl.textContent = `Estimated ${survivingPopulation.toLocaleString()} active shrimp in ${waterVolume.toLocaleString()} m³ water`;
        if (tFactorEl) tFactorEl.textContent = `${tempFactor.toFixed(2)}×`;
        if (tBadgeEl) {
            tBadgeEl.textContent = tempBadgeText;
            tBadgeEl.className = `wqi-metric-badge ${tempBadgeClass}`;
        }
        if (tGuideEl) tGuideEl.textContent = guidelineText;
        if (adjFeedEl) adjFeedEl.textContent = adjustedDailyFeed.toFixed(1);
        if (perMealEl) perMealEl.textContent = `${feedPerMeal.toFixed(1)} kg / meal`;
        if (baseFeedEl) baseFeedEl.textContent = baseDailyFeed.toFixed(1);

        // Also synchronize Pond Volume and Feed into Treatment Calculators
        const limeVolInput = document.getElementById("lime-pond-vol");
        if (limeVolInput && (!limeVolInput.dataset.manualEdited || limeVolInput.dataset.manualEdited === "false")) {
            limeVolInput.value = Math.round(waterVolume);
            calculateLimeDosage();
        }

        const molFeedInput = document.getElementById("molasses-daily-feed");
        if (molFeedInput && (!molFeedInput.dataset.manualEdited || molFeedInput.dataset.manualEdited === "false")) {
            molFeedInput.value = adjustedDailyFeed.toFixed(1);
            calculateMolassesDosage();
        }

        const aeroBiomassInput = document.getElementById("aero-biomass-input");
        if (aeroBiomassInput && (!aeroBiomassInput.dataset.manualEdited || aeroBiomassInput.dataset.manualEdited === "false")) {
            aeroBiomassInput.value = Math.round(biomassKg);
            calculateAeratorPower();
        }
    }

    // -------------------------------------------------------------
    // TOOL 2: Water Treatment & Chemical Dosing
    // -------------------------------------------------------------
    function calculateLimeDosage() {
        const volume = Math.max(1, Number(document.getElementById("lime-pond-vol")?.value || 1200));
        const currentPh = Number(document.getElementById("lime-current-ph")?.value || 7.10);
        const targetPh = Number(document.getElementById("lime-target-ph")?.value || 8.00);
        const chemical = document.getElementById("lime-chemical-type")?.value || "caco3";

        const dosageKgEl = document.getElementById("lime-dosage-kg");
        const dosagePpmEl = document.getElementById("lime-dosage-ppm");
        const instructionEl = document.getElementById("lime-instruction");

        if (currentPh >= targetPh) {
            if (dosageKgEl) dosageKgEl.textContent = "0.0";
            if (dosagePpmEl) dosagePpmEl.textContent = "0.0";
            if (instructionEl) {
                instructionEl.textContent = `Current pH (${currentPh.toFixed(2)}) meets or exceeds target (${targetPh.toFixed(2)}). No liming buffer is required.`;
            }
            return;
        }

        const deltaPh = targetPh - currentPh;
        // Chemical buffer factor (kg per m³ per 1.0 pH unit deficit in typical pond alkalinity)
        let factor = 0.050; // Agricultural limestone CaCO3
        let chemicalName = "Agricultural Limestone (CaCO₃)";

        if (chemical === "dolomite") {
            factor = 0.060;
            chemicalName = "Dolomite [CaMg(CO₃)₂]";
        } else if (chemical === "caoh2") {
            factor = 0.035;
            chemicalName = "Hydrated Lime [Ca(OH)₂]";
        }

        const requiredKg = volume * deltaPh * factor;
        const ppm = (requiredKg * 1000.0) / volume;

        if (dosageKgEl) dosageKgEl.textContent = requiredKg.toFixed(1);
        if (dosagePpmEl) dosagePpmEl.textContent = ppm.toFixed(1);
        if (instructionEl) {
            instructionEl.textContent = `Mix ${requiredKg.toFixed(1)} kg of ${chemicalName} in a 200L drum with pond water into a slurry. Broadcast evenly across the paddlewheel aerator wash in the early morning (07:00–09:00).`;
        }
    }

    function calculateMolassesDosage() {
        const dailyFeed = Math.max(0.1, Number(document.getElementById("molasses-daily-feed")?.value || 25.0));
        const proteinPct = Math.max(15, Number(document.getElementById("molasses-protein-pct")?.value || 35));
        const targetCn = Number(document.getElementById("molasses-target-cn")?.value || 15);
        const carbonSource = document.getElementById("molasses-carbon-source")?.value || "cane_molasses";

        // Nitrogen content in feed = Feed * %CP * 0.16 (crude protein is ~16% Nitrogen)
        const nitrogenInFeed = dailyFeed * (proteinPct / 100.0) * 0.16;
        // Carbon content in typical shrimp pelleted feed is ~50%
        const carbonInFeed = dailyFeed * 0.50;

        // Total Carbon required for target C:N ratio:
        const totalCarbonNeeded = nitrogenInFeed * targetCn;
        // Supplemental Carbon required from external carbon source:
        const carbonDeficit = Math.max(0, totalCarbonNeeded - carbonInFeed);

        // Carbon percentage of chosen source
        let carbonPct = 0.40; // Cane molasses ~40% Carbon
        let sourceName = "Cane Molasses";
        if (carbonSource === "white_sugar") {
            carbonPct = 0.42;
            sourceName = "Refined White Sugar";
        } else if (carbonSource === "cassava_flour") {
            carbonPct = 0.45;
            sourceName = "Cassava / Rice Flour";
        }

        const requiredKg = carbonDeficit / carbonPct;

        const dosageKgEl = document.getElementById("molasses-dosage-kg");
        const instructionEl = document.getElementById("molasses-instruction");

        if (dosageKgEl) dosageKgEl.textContent = requiredKg.toFixed(1);
        if (instructionEl) {
            instructionEl.textContent = `Dilute ${requiredKg.toFixed(1)} kg ${sourceName} in pond water, add 50g commercial biofloc probiotic (Bacillus spp.), aerate/ferment 3–4 hours, and apply during peak daytime aeration (09:00–11:00).`;
        }
    }

    function calculateAeratorPower() {
        const biomass = Math.max(10, Number(document.getElementById("aero-biomass-input")?.value || 765));
        const temp = Number(document.getElementById("aero-temp-input")?.value || liveSensor.temperature);

        // Standard Vannamei Aeration Ratio:
        // ~1.0 HP per 400 kg biomass under normal temperature (<=30°C)
        // ~1.0 HP per 320 kg biomass under elevated temperature (>30°C) due to lower DO saturation
        const kgPerHp = temp > 30.0 ? 320.0 : 400.0;
        const requiredHp = Math.max(1.0, Math.ceil((biomass / kgPerHp) * 2) / 2); // rounded to nearest 0.5 HP

        let unitsDesc = "";
        if (requiredHp <= 1.0) {
            unitsDesc = "1 × 1-HP unit";
        } else if (requiredHp <= 2.0) {
            unitsDesc = "1 × 2-HP or 2 × 1-HP units";
        } else {
            const twoHpUnits = Math.floor(requiredHp / 2.0);
            const remainder = requiredHp % 2.0;
            unitsDesc = remainder > 0 ? `${twoHpUnits} × 2-HP + 1 × 1-HP` : `${twoHpUnits} × 2-HP units`;
        }

        const hpEl = document.getElementById("aero-power-hp");
        const unitsEl = document.getElementById("aero-units");
        const instructionEl = document.getElementById("aero-instruction");

        if (hpEl) hpEl.textContent = requiredHp.toFixed(1);
        if (unitsEl) unitsEl.textContent = unitsDesc;
        if (instructionEl) {
            instructionEl.textContent = `Position paddlewheels to create a circular water vortex concentrating benthic sludge into the central drain. Run continuously from 22:00 to 07:00 and 13:00 to 15:00.`;
        }
    }

    // -------------------------------------------------------------
    // TOOL 3: Unionized Ammonia (NH3) Calculator & Van Wyk Modal
    // -------------------------------------------------------------
    function getVanWykFactor(tempC, phVal) {
        // Emerson / Bower-Bidwell formula used by Van Wyk & Scarpa (1999)
        const pKa = 0.09018 + (2729.92 / (273.15 + tempC));
        const factor = 1.0 / (Math.pow(10, pKa - phVal) + 1.0);
        return Math.min(1.0, Math.max(0.0001, factor));
    }

    function calculateAmmoniaTool() {
        const tanInput = document.getElementById("tools-ammonia-tan");
        const overrideCb = document.getElementById("tools-ammonia-override-cb");
        const customTempInput = document.getElementById("tools-custom-temp");
        const customPhInput = document.getElementById("tools-custom-ph");

        const tan = Math.max(0, Number(tanInput?.value || 0.8));
        const isOverride = overrideCb && overrideCb.checked;

        const temp = isOverride ? Number(customTempInput?.value || 28.0) : liveSensor.temperature;
        const ph = isOverride ? Number(customPhInput?.value || 7.60) : liveSensor.ph;

        const factor = getVanWykFactor(temp, ph);
        const nh3 = factor * tan;

        // Step outputs
        const stepTempEl = document.getElementById("tools-step-temp");
        const stepPhEl = document.getElementById("tools-step-ph");
        const stepFactorEl = document.getElementById("tools-step-factor");
        const stepMathEl = document.getElementById("tools-step-math");
        const stepFinalEl = document.getElementById("tools-step-final");
        const resultValEl = document.getElementById("tools-ammonia-result");
        const badgeEl = document.getElementById("tools-ammonia-badge");
        const assessmentBox = document.getElementById("tools-ammonia-assessment");
        const assessmentText = document.getElementById("tools-ammonia-assessment-text");
        const sensitivityNote = document.getElementById("tools-ammonia-sensitivity");

        if (stepTempEl) stepTempEl.textContent = `${temp.toFixed(1)} °C`;
        if (stepPhEl) stepPhEl.textContent = ph.toFixed(2);
        if (stepFactorEl) stepFactorEl.textContent = factor.toFixed(4);
        if (stepMathEl) stepMathEl.textContent = `${factor.toFixed(4)} × ${tan.toFixed(2)} ppm`;
        if (stepFinalEl) stepFinalEl.textContent = `${nh3.toFixed(4)} ppm`;
        if (resultValEl) resultValEl.textContent = nh3.toFixed(4);

        // Classification against P. vannamei standard (< 0.03 ppm safe)
        let statusBadge = "Safe (< 0.03 ppm)";
        let statusClass = "badge-optimal";
        let assessClass = "is-safe";
        let assessDesc = "";

        if (nh3 < 0.03) {
            statusBadge = "Safe (< 0.03 ppm)";
            statusClass = "badge-optimal";
            assessClass = "is-safe";
            assessDesc = `This level (${nh3.toFixed(4)} ppm) is within the acceptable safety threshold for Penaeus vannamei (<0.03 ppm). Gill permeability and osmoregulation remain healthy.`;
        } else if (nh3 <= 0.05) {
            statusBadge = "Sublethal Stress (0.03–0.05 ppm)";
            statusClass = "badge-warning";
            assessClass = "is-warning";
            assessDesc = `WARNING: This level (${nh3.toFixed(4)} ppm) exceeds the 0.03 ppm safety threshold. Chronic exposure causes gill hyperplasia, reduced feed conversion ratio (FCR), and immune suppression.`;
        } else {
            statusBadge = "Toxic Hazard (> 0.05 ppm)";
            statusClass = "badge-critical";
            assessClass = "is-critical";
            assessDesc = `CRITICAL HAZARD: At ${nh3.toFixed(4)} ppm, unionized ammonia causes cellular gill damage, hemolymph acidification, and elevated shrimp mortality. Execute emergency remediation immediately.`;
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

        // Sensitivity simulation text
        const sensFactor = getVanWykFactor(temp, ph + 0.2);
        const sensNh3 = sensFactor * tan;
        if (sensitivityNote) {
            sensitivityNote.innerHTML = `<strong>Sensitivity Insight:</strong> At ${temp.toFixed(1)} °C, a slight afternoon pH rise of only +0.2 (to ${(ph + 0.2).toFixed(2)}) increases toxic NH₃ to <strong>${sensNh3.toFixed(4)} ppm</strong> (${sensNh3 >= 0.03 ? "Exceeds acceptable limit" : "Safe"}).`;
        }

        highlightVanWykMatrix(temp, ph);
    }

    function highlightVanWykMatrix(temp, ph) {
        // Find closest grid column
        let closestTemp = VAN_WYK_TEMPS[0];
        let minDiffT = Math.abs(temp - closestTemp);
        VAN_WYK_TEMPS.forEach(t => {
            const diff = Math.abs(temp - t);
            if (diff < minDiffT) {
                minDiffT = diff;
                closestTemp = t;
            }
        });

        // Find closest grid row
        let closestPh = VAN_WYK_PHS[0];
        let minDiffP = Math.abs(ph - closestPh);
        VAN_WYK_PHS.forEach(p => {
            const diff = Math.abs(ph - p);
            if (diff < minDiffP) {
                minDiffP = diff;
                closestPh = p;
            }
        });

        const matrix = document.getElementById("tools-van-wyk-matrix");
        if (!matrix) return;

        // Reset highlights
        matrix.querySelectorAll("td, th").forEach(cell => {
            cell.classList.remove("cell-highlight-col", "cell-highlight-row", "cell-highlight-intersect");
        });

        // Highlight header col
        const thCol = matrix.querySelector(`th[data-temp="${closestTemp}"]`);
        if (thCol) thCol.classList.add("cell-highlight-col");

        // Highlight row
        const trRow = matrix.querySelector(`tr[data-ph="${closestPh.toFixed(1)}"]`);
        if (trRow) {
            trRow.querySelectorAll("td").forEach(td => td.classList.add("cell-highlight-row"));
            const targetCell = trRow.querySelector(`td[data-temp="${closestTemp}"]`);
            if (targetCell) {
                targetCell.classList.remove("cell-highlight-row", "cell-highlight-col");
                targetCell.classList.add("cell-highlight-intersect");
            }
        }
    }

    // Modal open/close
    const modal = document.getElementById("tools-van-wyk-modal");
    const openModalBtn = document.getElementById("open-tools-van-wyk");
    const closeModalBtn = document.getElementById("close-tools-van-wyk");
    const closeActionBtn = document.getElementById("tools-modal-close-action");

    function openModal() {
        if (modal) modal.hidden = false;
    }
    function closeModal() {
        if (modal) modal.hidden = true;
    }

    if (openModalBtn) openModalBtn.addEventListener("click", openModal);
    if (closeModalBtn) closeModalBtn.addEventListener("click", closeModal);
    if (closeActionBtn) closeActionBtn.addEventListener("click", closeModal);
    if (modal) {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) closeModal();
        });
    }

    // -------------------------------------------------------------
    // Wire Input Event Listeners
    // -------------------------------------------------------------
    // Biomass & Feed inputs
    [
        "feed-pond-area", "feed-pond-depth", "feed-stocking-density",
        "feed-survival-rate", "feed-abw", "feed-rate-percent",
        "feed-meals-day", "feed-current-temp"
    ].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", calculateBiomassAndFeed);
            el.addEventListener("change", calculateBiomassAndFeed);
        }
    });

    const btnUseLiveTemp = document.getElementById("btn-use-live-temp");
    if (btnUseLiveTemp) {
        btnUseLiveTemp.addEventListener("click", () => {
            const tempInput = document.getElementById("feed-current-temp");
            if (tempInput) {
                tempInput.value = liveSensor.temperature.toFixed(1);
                calculateBiomassAndFeed();
            }
        });
    }

    // Treatment inputs
    [
        "lime-pond-vol", "lime-current-ph", "lime-target-ph", "lime-chemical-type"
    ].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", () => {
                el.dataset.manualEdited = "true";
                calculateLimeDosage();
            });
            el.addEventListener("change", () => {
                el.dataset.manualEdited = "true";
                calculateLimeDosage();
            });
        }
    });

    [
        "molasses-daily-feed", "molasses-protein-pct", "molasses-target-cn", "molasses-carbon-source"
    ].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", () => {
                el.dataset.manualEdited = "true";
                calculateMolassesDosage();
            });
            el.addEventListener("change", () => {
                el.dataset.manualEdited = "true";
                calculateMolassesDosage();
            });
        }
    });

    [
        "aero-biomass-input", "aero-temp-input", "aero-salinity-input", "aero-target-do"
    ].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", () => {
                el.dataset.manualEdited = "true";
                calculateAeratorPower();
            });
            el.addEventListener("change", () => {
                el.dataset.manualEdited = "true";
                calculateAeratorPower();
            });
        }
    });

    // Ammonia Inputs & Presets
    const ammotanInput = document.getElementById("tools-ammonia-tan");
    if (ammotanInput) {
        ammotanInput.addEventListener("input", calculateAmmoniaTool);
        ammotanInput.addEventListener("change", calculateAmmoniaTool);
    }

    const ammoCalcBtn = document.getElementById("tools-ammonia-calc-btn");
    if (ammoCalcBtn) {
        ammoCalcBtn.addEventListener("click", calculateAmmoniaTool);
    }

    const presetChips = document.querySelectorAll("#tools-preset-chips .preset-chip");
    presetChips.forEach(chip => {
        chip.addEventListener("click", () => {
            presetChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            if (ammotanInput) {
                ammotanInput.value = chip.dataset.tan;
                calculateAmmoniaTool();
            }
        });
    });

    const overrideCb = document.getElementById("tools-ammonia-override-cb");
    const overrideFields = document.getElementById("tools-ammonia-override-fields");
    if (overrideCb && overrideFields) {
        overrideCb.addEventListener("change", () => {
            overrideFields.hidden = !overrideCb.checked;
            calculateAmmoniaTool();
        });
    }

    const customTempInput = document.getElementById("tools-custom-temp");
    const customPhInput = document.getElementById("tools-custom-ph");
    if (customTempInput) customTempInput.addEventListener("input", calculateAmmoniaTool);
    if (customPhInput) customPhInput.addEventListener("input", calculateAmmoniaTool);

    // Global Sync Live Button
    const btnSyncLive = document.getElementById("btn-sync-live");
    if (btnSyncLive) {
        btnSyncLive.addEventListener("click", async () => {
            btnSyncLive.disabled = true;
            await fetchLatestTelemetry();

            // Populate all calculators with live readings
            const feedTemp = document.getElementById("feed-current-temp");
            if (feedTemp) feedTemp.value = liveSensor.temperature.toFixed(1);

            const limePh = document.getElementById("lime-current-ph");
            if (limePh) limePh.value = liveSensor.ph.toFixed(2);

            const aeroTemp = document.getElementById("aero-temp-input");
            if (aeroTemp) aeroTemp.value = liveSensor.temperature.toFixed(1);

            calculateBiomassAndFeed();
            calculateLimeDosage();
            calculateMolassesDosage();
            calculateAeratorPower();
            calculateAmmoniaTool();

            btnSyncLive.disabled = false;
        });
    }

    // -------------------------------------------------------------
    // Initial Load & Boot
    // -------------------------------------------------------------
    async function boot() {
        await fetchLatestTelemetry();

        // Seed with live readings
        const feedTemp = document.getElementById("feed-current-temp");
        if (feedTemp) feedTemp.value = liveSensor.temperature.toFixed(1);

        const limePh = document.getElementById("lime-current-ph");
        if (limePh) limePh.value = liveSensor.ph.toFixed(2);

        const aeroTemp = document.getElementById("aero-temp-input");
        if (aeroTemp) aeroTemp.value = liveSensor.temperature.toFixed(1);

        calculateBiomassAndFeed();
        calculateLimeDosage();
        calculateMolassesDosage();
        calculateAeratorPower();
        calculateAmmoniaTool();
    }

    boot();
    setInterval(fetchLatestTelemetry, 15000);
});

