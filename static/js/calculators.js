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
        calculateMasterGrowth();
            }
        });
    });

    const overrideCb = document.getElementById("tools-ammonia-override-cb");
    const overrideFields = document.getElementById("tools-ammonia-override-fields");
    if (overrideCb && overrideFields) {
        overrideCb.addEventListener("change", () => {
            overrideFields.hidden = !overrideCb.checked;
            calculateAmmoniaTool();
        calculateMasterGrowth();
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
        calculateMasterGrowth();

            btnSyncLive.disabled = false;
        });
    }

// -------------------------------------------------------------
    // TOOL 2: Shrimp Growth & Zootechnical Performance (Eqs. 1–8)
    // All-in-One Engine with 8 Separate Metric Cards & Popup Dialog
    // -------------------------------------------------------------

    const GROWTH_PRESETS = {
        commercial: {
            is: 100000,
            lhc: 85000,
            doc: 90,
            ibw: 0.010,
            bw: 1700,
            bw_unit: "kg",
            tfg: 2125,
            feed_unit: "kg",
            tl: 12.9
        },
        intensive: {
            is: 150000,
            lhc: 132000,
            doc: 75,
            ibw: 0.015,
            bw: 2376,
            bw_unit: "kg",
            tfg: 2950,
            feed_unit: "kg",
            tl: 12.4
        },
        nursery: {
            is: 200000,
            lhc: 180000,
            doc: 30,
            ibw: 0.005,
            bw: 270,
            bw_unit: "kg",
            tfg: 280,
            feed_unit: "kg",
            tl: 5.8
        }
    };

    // Shared state storing current live calculation results
    let currentGrowthState = {
        isCount: 100000,
        lhcCount: 85000,
        docDays: 90,
        ibwVal: 0.010,
        bwInput: 1700,
        bwGrams: 1700000,
        bwKg: 1700,
        tfgInput: 2125,
        tfgKg: 2125,
        tlCm: 12.9,
        sr: 85.0,
        mortalityCount: 15000,
        mortalityPct: 15.0,
        fabw: 20.0,
        countPerKg: 50.0,
        adwg: 0.2221,
        weeklyGain: 1.555,
        sgr: 8.445,
        weightMult: 2000,
        ibGrams: 1000,
        ibKg: 1.0,
        fbGrams: 1700000,
        fbKg: 1700.0,
        netGainKg: 1699.0,
        fcr: 1.251,
        feedEfficiency: 79.95,
        kFactor: 0.9317
    };

    // Master Engine (All-in-One Eqs. 1–8)
    function calculateMasterGrowth() {
        const isCount = Math.max(1, Number(document.getElementById("gm-initial-stocking")?.value || 100000));
        const lhcCount = Math.max(1, Number(document.getElementById("gm-live-harvest-count")?.value || 85000));
        const docDays = Math.max(1, Number(document.getElementById("gm-days-of-culture")?.value || 90));
        const ibwVal = Math.max(0.0001, Number(document.getElementById("gm-initial-weight")?.value || 0.010));
        const bwInput = Math.max(0.1, Number(document.getElementById("gm-bulk-weight")?.value || 1700));
        const bwUnit = document.getElementById("gm-bw-unit")?.value || "kg";
        const tfgInput = Math.max(0.1, Number(document.getElementById("gm-total-feed")?.value || 2125));
        const feedUnit = document.getElementById("gm-feed-unit")?.value || "kg";
        const tlCm = Math.max(0.1, Number(document.getElementById("gm-total-length")?.value || 12.9));

        // Normalizations
        const bwGrams = bwUnit === "kg" ? bwInput * 1000.0 : bwInput;
        const bwKg = bwGrams / 1000.0;
        const tfgKg = feedUnit === "kg" ? tfgInput : tfgInput / 1000.0;

        // Eq. 1: Survival Rate (SR) = (LHC / IS) * 100
        const sr = (lhcCount / isCount) * 100.0;
        const mortalityCount = Math.max(0, isCount - lhcCount);
        const mortalityPct = Math.max(0, 100.0 - sr);

        // Eq. 2: Final Average Body Weight (FABW) = BW / LHC
        const fabw = bwGrams / lhcCount;
        const countPerKg = fabw > 0 ? (1000.0 / fabw) : 0;

        // Eq. 3: Average Daily Weight Gain (ADWG) = (FABW - IBW) / DOC
        const adwg = (fabw - ibwVal) / docDays;
        const weeklyGain = adwg * 7.0;

        // Eq. 4: Specific Growth Rate (SGR) = ((ln FABW - ln IBW) / DOC) * 100
        const sgr = ((Math.log(fabw) - Math.log(ibwVal)) / docDays) * 100.0;
        const weightMult = fabw / ibwVal;

        // Eq. 5: Initial Biomass (IB) = IS * IBW
        const ibGrams = isCount * ibwVal;
        const ibKg = ibGrams / 1000.0;

        // Eq. 6: Final Biomass (FB) = LHC * FABW
        const fbGrams = lhcCount * fabw;
        const fbKg = fbGrams / 1000.0;
        const netGainKg = Math.max(0.0001, fbKg - ibKg);

        // Eq. 7: Feed Conversion Ratio (FCR) = TFG / (FB - IB)
        const fcr = tfgKg / netGainKg;
        const feedEfficiency = fcr > 0 ? (100.0 / fcr) : 0;

        // Eq. 8: Fulton's Condition Factor (K) = (FABW / TL^3) * 100
        const kFactor = (fabw / Math.pow(tlCm, 3)) * 100.0;

        // Update state
        currentGrowthState = {
            isCount, lhcCount, docDays, ibwVal, bwInput, bwGrams, bwKg,
            tfgInput, tfgKg, tlCm, sr, mortalityCount, mortalityPct,
            fabw, countPerKg, adwg, weeklyGain, sgr, weightMult,
            ibGrams, ibKg, fbGrams, fbKg, netGainKg, fcr, feedEfficiency, kFactor
        };

        // DOM Updates - Eq. 1: Survival Rate
        const srValEl = document.getElementById("gm-res-sr-val");
        const srBadgeEl = document.getElementById("gm-res-sr-badge");
        const mortCountEl = document.getElementById("gm-res-mortality-count");
        const mortPctEl = document.getElementById("gm-res-mortality-pct");
        if (srValEl) srValEl.textContent = sr.toFixed(2);
        if (mortCountEl) mortCountEl.textContent = Math.round(mortalityCount).toLocaleString();
        if (mortPctEl) mortPctEl.textContent = `${mortalityPct.toFixed(2)}%`;
        if (srBadgeEl) {
            if (sr >= 80.0) {
                srBadgeEl.textContent = "Optimal (≥80%)";
                srBadgeEl.className = "wqi-metric-badge badge-optimal";
            } else if (sr >= 65.0) {
                srBadgeEl.textContent = "Acceptable (65–79%)";
                srBadgeEl.className = "wqi-metric-badge badge-warning";
            } else {
                srBadgeEl.textContent = "Suboptimal (<65%)";
                srBadgeEl.className = "wqi-metric-badge badge-critical";
            }
        }

        // DOM Updates - Eq. 2: FABW
        const fabwValEl = document.getElementById("gm-res-fabw-val");
        const countKgEl = document.getElementById("gm-res-count-per-kg");
        const bulkSummaryEl = document.getElementById("gm-res-bulk-summary");
        if (fabwValEl) fabwValEl.textContent = fabw.toFixed(2);
        if (countKgEl) countKgEl.textContent = countPerKg.toFixed(1);
        if (bulkSummaryEl) bulkSummaryEl.textContent = `${bwKg.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} kg (${Math.round(bwGrams).toLocaleString()} g)`;

        // DOM Updates - Eq. 3: ADWG (SEPARATE)
        const adwgValEl = document.getElementById("gm-res-adwg-val");
        const adwgBadgeEl = document.getElementById("gm-res-adwg-badge");
        const weeklyGainEl = document.getElementById("gm-res-weekly-gain");
        if (adwgValEl) adwgValEl.textContent = adwg.toFixed(4);
        if (weeklyGainEl) weeklyGainEl.textContent = weeklyGain.toFixed(3);
        if (adwgBadgeEl) {
            if (adwg >= 0.22) {
                adwgBadgeEl.textContent = "Fast Growth";
                adwgBadgeEl.className = "wqi-metric-badge badge-optimal";
            } else if (adwg >= 0.18) {
                adwgBadgeEl.textContent = "Optimal Growth";
                adwgBadgeEl.className = "wqi-metric-badge badge-optimal";
            } else {
                adwgBadgeEl.textContent = "Slow Growth";
                adwgBadgeEl.className = "wqi-metric-badge badge-warning";
            }
        }

        // DOM Updates - Eq. 4: SGR (SEPARATE)
        const sgrValEl = document.getElementById("gm-res-sgr-val");
        const weightMultEl = document.getElementById("gm-res-weight-mult");
        if (sgrValEl) sgrValEl.textContent = sgr.toFixed(3);
        if (weightMultEl) weightMultEl.textContent = `${Math.round(weightMult).toLocaleString()}×`;

        // DOM Updates - Eq. 5: Initial Biomass (SEPARATE)
        const ibKgEl = document.getElementById("gm-res-ib-kg");
        const ibGramsEl = document.getElementById("gm-res-ib-grams");
        if (ibKgEl) ibKgEl.textContent = ibKg.toFixed(2);
        if (ibGramsEl) ibGramsEl.textContent = Math.round(ibGrams).toLocaleString();

        // DOM Updates - Eq. 6: Final Biomass (SEPARATE)
        const fbKgEl = document.getElementById("gm-res-fb-kg");
        const netBioEl = document.getElementById("gm-res-net-biomass");
        if (fbKgEl) fbKgEl.textContent = fbKg.toFixed(2);
        if (netBioEl) netBioEl.textContent = netGainKg.toFixed(2);

        // DOM Updates - Eq. 7: Feed Conversion Ratio
        const fcrValEl = document.getElementById("gm-res-fcr-val");
        const fcrBadgeEl = document.getElementById("gm-res-fcr-badge");
        const feedEffEl = document.getElementById("gm-res-feed-efficiency");
        const tfgSummaryEl = document.getElementById("gm-res-tfg-summary");
        const gainSummaryEl = document.getElementById("gm-res-gain-summary");
        if (fcrValEl) fcrValEl.textContent = fcr.toFixed(3);
        if (feedEffEl) feedEffEl.textContent = `${feedEfficiency.toFixed(2)}%`;
        if (tfgSummaryEl) tfgSummaryEl.textContent = `${tfgKg.toFixed(1)} kg`;
        if (gainSummaryEl) gainSummaryEl.textContent = `${netGainKg.toFixed(1)} kg`;
        if (fcrBadgeEl) {
            if (fcr < 1.20) {
                fcrBadgeEl.textContent = "Exceptional (<1.20)";
                fcrBadgeEl.className = "wqi-metric-badge badge-optimal";
            } else if (fcr <= 1.50) {
                fcrBadgeEl.textContent = "Optimal (1.20–1.50)";
                fcrBadgeEl.className = "wqi-metric-badge badge-optimal";
            } else if (fcr <= 1.80) {
                fcrBadgeEl.textContent = "Acceptable (1.51–1.80)";
                fcrBadgeEl.className = "wqi-metric-badge badge-warning";
            } else {
                fcrBadgeEl.textContent = "Suboptimal (>1.80)";
                fcrBadgeEl.className = "wqi-metric-badge badge-critical";
            }
        }

        // DOM Updates - Eq. 8: Fulton's Condition Factor
        const kValEl = document.getElementById("gm-res-k-val");
        const kBadgeEl = document.getElementById("gm-res-k-badge");
        const kProfileEl = document.getElementById("gm-res-k-profile");
        if (kValEl) kValEl.textContent = kFactor.toFixed(4);
        if (kBadgeEl && kProfileEl) {
            if (kFactor >= 0.80 && kFactor <= 1.15) {
                kBadgeEl.textContent = "Optimal Condition (0.80–1.15)";
                kBadgeEl.className = "wqi-metric-badge badge-optimal";
                kProfileEl.textContent = "Healthy, well-proportioned robust girth";
            } else if (kFactor < 0.80) {
                kBadgeEl.textContent = "Slender / Lean (<0.80)";
                kBadgeEl.className = "wqi-metric-badge badge-warning";
                kProfileEl.textContent = "Slender body profile; check post-molt phase or dietary energy";
            } else {
                kBadgeEl.textContent = "Heavy / Plump (>1.15)";
                kBadgeEl.className = "wqi-metric-badge badge-optimal";
                kProfileEl.textContent = "High muscle density and heavy carapace girth";
            }
        }
    }

    // Modal popup dialog definitions for Equations 1 to 8
    const EQUATION_SPECS = {
        "1": {
            title: "Equation 1: Survival Rate (SR)",
            subtitle: "Percentage of stocked post-larvae that survive until harvest",
            formula: "SR = (LHC / IS) × 100",
            variables: [
                "<strong>LHC</strong> = Live harvest count (shrimp)",
                "<strong>IS</strong> = Initial stocking (shrimp)",
                "<strong>SR</strong> = Survival rate (%)"
            ],
            getSubstitution: (s) => `SR = (${s.lhcCount.toLocaleString()} shrimp / ${s.isCount.toLocaleString()} shrimp) × 100 = <strong>${s.sr.toFixed(2)}%</strong><br><small style="color:#64748b;">Mortality: ${s.mortalityCount.toLocaleString()} shrimp (${s.mortalityPct.toFixed(2)}%)</small>`,
            getEval: (s) => ({
                badge: s.sr >= 80 ? "Optimal (≥80%)" : (s.sr >= 65 ? "Acceptable (65–79%)" : "Suboptimal (<65%)"),
                badgeClass: s.sr >= 80 ? "badge-optimal" : (s.sr >= 65 ? "badge-warning" : "badge-critical"),
                text: s.sr >= 80
                    ? `Optimal survival rate (${s.sr.toFixed(2)}%) exceeding typical commercial Penaeus vannamei benchmarks (≥80%). Mortality was contained to ${s.mortalityCount.toLocaleString()} shrimp (${s.mortalityPct.toFixed(2)}%), indicating stable water quality, clean bottom soil, and strong biosecurity.`
                    : (s.sr >= 65
                        ? `Moderate survival rate (${s.sr.toFixed(2)}%). Total cumulative loss is ${s.mortalityCount.toLocaleString()} shrimp (${s.mortalityPct.toFixed(2)}%). Check for dissolved oxygen drops during night hours (22:00–06:00) and monitor benthic sediment accumulation.`
                        : `Suboptimal survival rate (${s.sr.toFixed(2)}%). High mortality (${s.mortalityCount.toLocaleString()} shrimp lost, ${s.mortalityPct.toFixed(2)}%). Investigate sudden salinity or temperature swings, unionized ammonia toxicity, or pathogen challenge.`),
                tip: "<strong>Pond Action Tip:</strong> Ensure paddlewheel aerators maintain DO > 4.0 ppm continuously throughout molting cycles to prevent cannibalism and hypoxic mortality."
            })
        },
        "2": {
            title: "Equation 2: Final Average Body Weight (FABW)",
            subtitle: "Average weight of individual shrimp at harvest",
            formula: "FABW = BW / LHC",
            variables: [
                "<strong>BW</strong> = Bulk harvested biomass weight (g)",
                "<strong>LHC</strong> = Live harvest count (shrimp)",
                "<strong>FABW</strong> = Final average body weight (g)"
            ],
            getSubstitution: (s) => `FABW = ${Math.round(s.bwGrams).toLocaleString()} g / ${s.lhcCount.toLocaleString()} shrimp = <strong>${s.fabw.toFixed(2)} g/shrimp</strong><br><small style="color:#64748b;">Market Count: ${s.countPerKg.toFixed(1)} pcs/kg (${Math.round(s.countPerKg)} count)</small>`,
            getEval: (s) => ({
                badge: s.fabw >= 18 ? "Optimal Commercial Size" : "Sub-Commercial Size",
                badgeClass: s.fabw >= 18 ? "badge-optimal" : "badge-warning",
                text: `Harvested average body weight of ${s.fabw.toFixed(2)} g corresponds to Size ${s.countPerKg.toFixed(0)} count (${s.countPerKg.toFixed(1)} pieces per kilogram). In high-density vannamei farming, 18–25 g represents the premium commercial export grade.`,
                tip: "<strong>Pond Action Tip:</strong> Uniform size distribution is achieved by distributing feed across check trays and wide feeding lanes, preventing dominant individuals from monopolizing feed."
            })
        },
        "3": {
            title: "Equation 3: Average Daily Weight Gain (ADWG)",
            subtitle: "Linear daily weight increment across the culture period",
            formula: "ADWG = (FABW - IBW) / DOC",
            variables: [
                "<strong>FABW</strong> = Final average body weight (g)",
                "<strong>IBW</strong> = Initial body weight at stocking (g)",
                "<strong>DOC</strong> = Days of culture (days)",
                "<strong>ADWG</strong> = Average daily weight gain (g/day)"
            ],
            getSubstitution: (s) => `ADWG = (${s.fabw.toFixed(2)} g - ${s.ibwVal.toFixed(3)} g) / ${s.docDays} days = <strong>${s.adwg.toFixed(4)} g/day</strong><br><small style="color:#64748b;">Weekly Gain: ${s.weeklyGain.toFixed(3)} g/week</small>`,
            getEval: (s) => ({
                badge: s.adwg >= 0.22 ? "Fast Growth (≥0.22 g/d)" : (s.adwg >= 0.18 ? "Optimal (0.18–0.22 g/d)" : "Slow (<0.18 g/d)"),
                badgeClass: s.adwg >= 0.18 ? "badge-optimal" : "badge-warning",
                text: s.adwg >= 0.18
                    ? `Average daily gain of ${s.adwg.toFixed(4)} g/day (${s.weeklyGain.toFixed(3)} g/week) is within or above the optimal standard for Penaeus vannamei. Digestive enzymes and feed intake have operated efficiently.`
                    : `Average daily gain of ${s.adwg.toFixed(4)} g/day is lower than standard commercial targets (<0.18 g/day). Growth may have been dampened by low water temperatures (<26 °C), reduced natural productivity, or high stocking density.`,
                tip: "<strong>Pond Action Tip:</strong> Monitor water temperature regularly; digestive protease activity drops significantly below 28 °C. Adjust feeding rations dynamically using temperature telemetry."
            })
        },
        "4": {
            title: "Equation 4: Specific Growth Rate (SGR)",
            subtitle: "Logarithmic biological compounding rate per day",
            formula: "SGR = [(ln FABW - ln IBW) / DOC] × 100",
            variables: [
                "<strong>FABW</strong> = Final average body weight (g)",
                "<strong>IBW</strong> = Initial body weight at stocking (g)",
                "<strong>DOC</strong> = Days of culture (days)",
                "<strong>ln</strong> = Natural logarithm",
                "<strong>SGR</strong> = Specific growth rate (%/day)"
            ],
            getSubstitution: (s) => `SGR = [(ln ${s.fabw.toFixed(2)} - ln ${s.ibwVal.toFixed(3)}) / ${s.docDays}] × 100 = <strong>${s.sgr.toFixed(3)}% / day</strong><br><small style="color:#64748b;">Weight Multiplication: ${Math.round(s.weightMult).toLocaleString()}× stocking weight</small>`,
            getEval: (s) => ({
                badge: "Logarithmic Growth Index",
                badgeClass: "badge-optimal",
                text: `Specific growth rate evaluates relative percentage growth compounding each day. Over the ${s.docDays}-day cycle, individual shrimp increased in weight by ${Math.round(s.weightMult).toLocaleString()} times their stocking mass.`,
                tip: "<strong>Pond Action Tip:</strong> SGR is steepest during nursery/early juvenile stages (DOC 1–30) and gradually flattens during late growout as metabolic maintenance increases."
            })
        },
        "5": {
            title: "Equation 5: Initial Biomass (IB)",
            subtitle: "Total biological mass introduced at pond stocking",
            formula: "IB = IS × IBW",
            variables: [
                "<strong>IS</strong> = Initial stocking count (shrimp)",
                "<strong>IBW</strong> = Initial body weight per shrimp (g)",
                "<strong>IB</strong> = Initial total biomass (g / kg)"
            ],
            getSubstitution: (s) => `IB = ${s.isCount.toLocaleString()} shrimp × ${s.ibwVal.toFixed(3)} g = ${Math.round(s.ibGrams).toLocaleString()} g = <strong>${s.ibKg.toFixed(2)} kg</strong>`,
            getEval: (s) => ({
                badge: "Stocking Base Biomass",
                badgeClass: "badge-optimal",
                text: `Total initial biological load stocked into the pond was ${s.ibKg.toFixed(2)} kg (${Math.round(s.ibGrams).toLocaleString()} grams). This establishes the base baseline from which total biological production is measured.`,
                tip: "<strong>Pond Action Tip:</strong> Proper acclimatization of post-larvae (gradual temperature and salinity equalization over 1–2 hours) directly protects this initial investment."
            })
        },
        "6": {
            title: "Equation 6: Final Biomass (FB)",
            subtitle: "Total standing biological biomass harvested from the pond",
            formula: "FB = LHC × FABW",
            variables: [
                "<strong>LHC</strong> = Live harvest count (shrimp)",
                "<strong>FABW</strong> = Final average body weight (g)",
                "<strong>FB</strong> = Final total biomass (g / kg)"
            ],
            getSubstitution: (s) => `FB = ${s.lhcCount.toLocaleString()} shrimp × ${s.fabw.toFixed(2)} g = ${Math.round(s.fbGrams).toLocaleString()} g = <strong>${s.fbKg.toFixed(2)} kg</strong><br><small style="color:#64748b;">Net Live Yield Gain: ${s.netGainKg.toFixed(2)} kg</small>`,
            getEval: (s) => ({
                badge: "Harvest Standing Crop",
                badgeClass: "badge-optimal",
                text: `Total harvest standing crop yielded ${s.fbKg.toFixed(2)} kg (${(s.fbKg / 1000.0).toFixed(2)} metric tons). Subtracting initial biomass (${s.ibKg.toFixed(2)} kg) reveals a net live biomass gain of ${s.netGainKg.toFixed(2)} kg.`,
                tip: "<strong>Pond Action Tip:</strong> Ensure paddlewheel aeration maintains at least 1 HP per 350–400 kg of standing biomass in the final month to prevent hypoxic crashes."
            })
        },
        "7": {
            title: "Equation 7: Feed Conversion Ratio (FCR)",
            subtitle: "Feed utilization efficiency: kg of feed per kg of live weight gain",
            formula: "FCR = TFG / (FB - IB)",
            variables: [
                "<strong>TFG</strong> = Total feed given across crop (kg)",
                "<strong>FB</strong> = Final harvest biomass (kg)",
                "<strong>IB</strong> = Initial stocking biomass (kg)",
                "<strong>FCR</strong> = Feed conversion ratio"
            ],
            getSubstitution: (s) => `FCR = ${s.tfgKg.toFixed(1)} kg feed / (${s.fbKg.toFixed(1)} kg - ${s.ibKg.toFixed(1)} kg) net gain = <strong>${s.fcr.toFixed(3)}</strong><br><small style="color:#64748b;">Feed Assimilation Efficiency: ${s.feedEfficiency.toFixed(2)}%</small>`,
            getEval: (s) => ({
                badge: s.fcr < 1.20 ? "Exceptional (<1.20)" : (s.fcr <= 1.50 ? "Optimal (1.20–1.50)" : (s.fcr <= 1.80 ? "Acceptable (1.51–1.80)" : "Suboptimal (>1.80)")),
                badgeClass: s.fcr <= 1.50 ? "badge-optimal" : (s.fcr <= 1.80 ? "badge-warning" : "badge-critical"),
                text: s.fcr <= 1.50
                    ? `Excellent FCR of ${s.fcr.toFixed(3)}. Standard commercial targets for Penaeus vannamei range between 1.20 and 1.50. High feed efficiency (${s.feedEfficiency.toFixed(2)}%) indicates minimal feed wastage, healthy gut microbiota, and low ammonia generation.`
                    : (s.fcr <= 1.80
                        ? `Acceptable FCR of ${s.fcr.toFixed(3)}. Feed utilization was moderate (${s.feedEfficiency.toFixed(2)}%). Regularly monitor feeding check trays to ensure feed is fully consumed within 2 hours.`
                        : `Suboptimal FCR of ${s.fcr.toFixed(3)} (>1.80). Indicates feed wastage, overfeeding, or poor water quality reducing appetite. Excess unconsumed pellets decay on pond bottom, driving up toxic unionized ammonia.`),
                tip: "<strong>Pond Action Tip:</strong> Check feed trays 1.5–2 hours after every meal. If >10% remains uneaten, immediately reduce the next feeding by 20%."
            })
        },
        "8": {
            title: "Equation 8: Fulton's Condition Factor (K)",
            subtitle: "Morphometric body condition, tail meat fullness, and muscle density",
            formula: "K = (FABW / TL³) × 100",
            variables: [
                "<strong>FABW</strong> = Final average body weight (g)",
                "<strong>TL</strong> = Total length from rostrum tip to telson tip (cm)",
                "<strong>K</strong> = Fulton's body condition factor"
            ],
            getSubstitution: (s) => `K = (${s.fabw.toFixed(2)} g / ${s.tlCm.toFixed(1)}³ cm³) × 100 = (${s.fabw.toFixed(2)} / ${Math.pow(s.tlCm, 3).toFixed(3)}) × 100 = <strong>${s.kFactor.toFixed(4)}</strong>`,
            getEval: (s) => ({
                badge: (s.kFactor >= 0.80 && s.kFactor <= 1.15) ? "Optimal Robust (0.80–1.15)" : (s.kFactor < 0.80 ? "Slender / Lean (<0.80)" : "Heavy Plump (>1.15)"),
                badgeClass: (s.kFactor >= 0.80 && s.kFactor <= 1.15) ? "badge-optimal" : (s.kFactor < 0.80 ? "badge-warning" : "badge-optimal"),
                text: (s.kFactor >= 0.80 && s.kFactor <= 1.15)
                    ? `Optimal Fulton's condition factor (${s.kFactor.toFixed(4)}). A K factor between 0.80 and 1.15 is the ideal biological index for healthy Penaeus vannamei, denoting dense abdominal tail meat filling, firm muscle texture, and a well-proportioned carapace.`
                    : (s.kFactor < 0.80
                        ? `Slender body profile (K = ${s.kFactor.toFixed(4)} < 0.80). Shrimp may have recently completed ecdysis (molting) where carapace expands before flesh fills out, or they may require higher dietary energy/protein.`
                        : `Heavy plump body profile (K = ${s.kFactor.toFixed(4)} > 1.15). Indicates high muscle girth and thick abdominal flesh.`),
                tip: "<strong>Pond Action Tip:</strong> Sample 30–50 shrimp during weekly cast-net sampling to track K factor trends and verify tail meat fullness before scheduling commercial harvest."
            })
        }
    };

    // Modal Opening & Closing Functions
    function openGrowthModal(eqNumber) {
        const modal = document.getElementById("growth-equation-modal");
        const spec = EQUATION_SPECS[String(eqNumber)];
        if (!modal || !spec) return;

        const titleEl = document.getElementById("growth-modal-title");
        const subtitleEl = document.getElementById("growth-modal-subtitle");
        const formulaEl = document.getElementById("growth-modal-formula");
        const varsEl = document.getElementById("growth-modal-variables");
        const subEl = document.getElementById("growth-modal-substitution");
        const badgeEl = document.getElementById("growth-modal-badge");
        const recEl = document.getElementById("growth-modal-recommendation");
        const tipEl = document.getElementById("growth-modal-action-tip");

        if (titleEl) titleEl.textContent = spec.title;
        if (subtitleEl) subtitleEl.textContent = spec.subtitle;
        if (formulaEl) formulaEl.innerHTML = spec.formula;

        if (varsEl) {
            varsEl.innerHTML = spec.variables.map(v => `<div>${v}</div>`).join("");
        }

        if (subEl) {
            subEl.innerHTML = spec.getSubstitution(currentGrowthState);
        }

        const evaluation = spec.getEval(currentGrowthState);
        if (badgeEl) {
            badgeEl.textContent = evaluation.badge;
            badgeEl.className = `wqi-metric-badge ${evaluation.badgeClass}`;
        }
        if (recEl) {
            recEl.textContent = evaluation.text;
        }
        if (tipEl) {
            tipEl.innerHTML = evaluation.tip;
        }

        modal.hidden = false;
        document.body.style.overflow = "hidden";
    }

    function closeGrowthModal() {
        const modal = document.getElementById("growth-equation-modal");
        if (modal) {
            modal.hidden = true;
            document.body.style.overflow = "";
        }
    }

    // Input Listeners for Master Engine
    [
        "gm-initial-stocking", "gm-live-harvest-count", "gm-days-of-culture",
        "gm-initial-weight", "gm-bulk-weight", "gm-bw-unit",
        "gm-total-feed", "gm-feed-unit", "gm-total-length"
    ].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", calculateMasterGrowth);
            el.addEventListener("change", calculateMasterGrowth);
        }
    });

    // Preset Buttons
    const growthPresetButtons = document.querySelectorAll("#growth-master-presets .preset-chip, .btn-preset-growth");
    growthPresetButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            growthPresetButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const presetKey = btn.dataset.preset;
            const p = GROWTH_PRESETS[presetKey];
            if (!p) return;

            const isInput = document.getElementById("gm-initial-stocking");
            const lhcInput = document.getElementById("gm-live-harvest-count");
            const docInput = document.getElementById("gm-days-of-culture");
            const ibwInput = document.getElementById("gm-initial-weight");
            const bwInput = document.getElementById("gm-bulk-weight");
            const bwUnitSelect = document.getElementById("gm-bw-unit");
            const tfgInput = document.getElementById("gm-total-feed");
            const feedUnitSelect = document.getElementById("gm-feed-unit");
            const tlInput = document.getElementById("gm-total-length");

            if (isInput) isInput.value = p.is;
            if (lhcInput) lhcInput.value = p.lhc;
            if (docInput) docInput.value = p.doc;
            if (ibwInput) ibwInput.value = p.ibw;
            if (bwInput) bwInput.value = p.bw;
            if (bwUnitSelect) bwUnitSelect.value = p.bw_unit;
            if (tfgInput) tfgInput.value = p.tfg;
            if (feedUnitSelect) feedUnitSelect.value = p.feed_unit;
            if (tlInput) tlInput.value = p.tl;

            calculateMasterGrowth();
        });
    });

    // Sync from Biomass Tool (Section 1)
    const btnSyncFromBiomass = document.getElementById("btn-sync-from-biomass");
    if (btnSyncFromBiomass) {
        btnSyncFromBiomass.addEventListener("click", () => {
            const area = Number(document.getElementById("feed-pond-area")?.value || 1000);
            const density = Number(document.getElementById("feed-stocking-density")?.value || 60);
            const survival = Number(document.getElementById("feed-survival-rate")?.value || 85);
            const abw = Number(document.getElementById("feed-abw")?.value || 15.0);

            const isCount = Math.round(area * density);
            const lhcCount = Math.round(isCount * (survival / 100.0));
            const bwKg = (lhcCount * abw) / 1000.0;

            const isInput = document.getElementById("gm-initial-stocking");
            const lhcInput = document.getElementById("gm-live-harvest-count");
            const bwInput = document.getElementById("gm-bulk-weight");
            const bwUnitSelect = document.getElementById("gm-bw-unit");

            if (isInput) isInput.value = isCount;
            if (lhcInput) lhcInput.value = lhcCount;
            if (bwInput) bwInput.value = bwKg.toFixed(1);
            if (bwUnitSelect) bwUnitSelect.value = "kg";

            calculateMasterGrowth();
        });
    }

    // Modal Trigger Buttons on each of the 8 cards
    document.querySelectorAll(".growth-calc-details-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const eqNum = btn.dataset.eq;
            openGrowthModal(eqNum);
        });
    });

    const closeGrowthModalBtn = document.getElementById("close-growth-modal");
    const closeGrowthActionBtn = document.getElementById("growth-modal-close-action");
    const growthModalBackdrop = document.getElementById("growth-equation-modal");

    if (closeGrowthModalBtn) closeGrowthModalBtn.addEventListener("click", closeGrowthModal);
    if (closeGrowthActionBtn) closeGrowthActionBtn.addEventListener("click", closeGrowthModal);
    if (growthModalBackdrop) {
        growthModalBackdrop.addEventListener("click", (e) => {
            if (e.target === growthModalBackdrop) closeGrowthModal();
        });
    }
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && growthModalBackdrop && !growthModalBackdrop.hidden) {
            closeGrowthModal();
        }
    });

// -------------------------------------------------------------
    // Initial Load & Boot
    // -------------------------------------------------------------
    // -------------------------------------------------------------
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
                        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
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


    // =============================================================
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
    let growthChartHoveredParam = null;
    let growthHistoryRecords = [];

    // DOM Elements for Graph Modal
    const growthGraphModal = document.getElementById("growth-trend-graph-modal");
    const closeGrowthGraphModalBtn = document.getElementById("close-growth-graph-modal");
    const closeGrowthGraphActionBtn = document.getElementById("close-growth-graph-action-btn");
    const btnOpenGrowthChart = document.getElementById("btn-open-growth-chart");
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

            // Circular points with hover halo and focused item glow
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
            });
        });
    }

    function renderGrowthTooltip(index, pointX, targetY, focusedParam, containerWidth, containerHeight) {
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
        growthTooltip.style.top = `${Math.round(topPos)}px`;
    }



    async function openGrowthGraphModal() {
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
        growthChartHoveredParam = null;
    }

    // Graph Modal Event Listeners
    if (btnOpenGrowthChart) btnOpenGrowthChart.addEventListener("click", openGrowthGraphModal);
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
                renderGrowthChart();
        });
    });

    if (btnToggleAllGrowthMetrics) {
        btnToggleAllGrowthMetrics.addEventListener("click", () => {
            selectedGrowthMetrics = new Set(["sr", "fabw", "adwg", "sgr", "fb", "fcr", "k"]);
            growthMetricChips.forEach(chip => chip.classList.add("active"));
                renderGrowthChart();
        });
    }

    function handleGrowthPointerMove(event) {
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
        calculateMasterGrowth();
    }

    boot();
    setInterval(fetchLatestTelemetry, 15000);
});
