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

    // -------------------------------------------------------------
    // TOOL 2: Shrimp Growth & Zootechnical Performance (Eqs. 1–8)
    // -------------------------------------------------------------

    // Tab Switching for Growth Calculators (Uniform Chip Pills)
    const growthTabButtons = document.querySelectorAll(".tools-tab-chips .preset-chip, .growth-tabs-bar .growth-tab-item");
    const growthTabPanes = document.querySelectorAll(".growth-tab-pane");

    growthTabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const paneKey = btn.dataset.pane || "";
            const targetPaneId = paneKey ? `pane-growth-${paneKey}` : btn.getAttribute("aria-controls");
            growthTabButtons.forEach(b => {
                b.classList.remove("active");
                b.setAttribute("aria-selected", "false");
            });
            growthTabPanes.forEach(p => {
                p.classList.remove("active");
                p.hidden = true;
                p.style.display = "none";
            });

            btn.classList.add("active");
            btn.setAttribute("aria-selected", "true");
            const activePane = document.getElementById(targetPaneId);
            if (activePane) {
                activePane.classList.add("active");
                activePane.hidden = false;
                activePane.style.display = "block";
            }
        });
    });

    // Preset Configurations for Penaeus vannamei
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

        // DOM Updates - Eq. 1
        const srValEl = document.getElementById("gm-res-sr-val");
        const srBadgeEl = document.getElementById("gm-res-sr-badge");
        const mortCountEl = document.getElementById("gm-res-mortality-count");
        const mortPctEl = document.getElementById("gm-res-mortality-pct");
        const subSrEl = document.getElementById("gm-sub-sr");
        if (srValEl) srValEl.textContent = sr.toFixed(2);
        if (mortCountEl) mortCountEl.textContent = Math.round(mortalityCount).toLocaleString();
        if (mortPctEl) mortPctEl.textContent = `${mortalityPct.toFixed(2)}%`;
        if (subSrEl) subSrEl.innerHTML = `(${lhcCount.toLocaleString()} / ${isCount.toLocaleString()}) &times; 100 = ${sr.toFixed(2)}%`;
        if (srBadgeEl) {
            if (sr >= 80.0) {
                srBadgeEl.textContent = "Optimal";
                srBadgeEl.className = "wqi-metric-badge badge-optimal";
            } else if (sr >= 65.0) {
                srBadgeEl.textContent = "Acceptable";
                srBadgeEl.className = "wqi-metric-badge badge-warning";
            } else {
                srBadgeEl.textContent = "Suboptimal";
                srBadgeEl.className = "wqi-metric-badge badge-critical";
            }
        }

        // DOM Updates - Eq. 2
        const fabwValEl = document.getElementById("gm-res-fabw-val");
        const countKgEl = document.getElementById("gm-res-count-per-kg");
        const subFabwEl = document.getElementById("gm-sub-fabw");
        if (fabwValEl) fabwValEl.textContent = fabw.toFixed(2);
        if (countKgEl) countKgEl.textContent = countPerKg.toFixed(1);
        if (subFabwEl) subFabwEl.innerHTML = `${Math.round(bwGrams).toLocaleString()} g / ${lhcCount.toLocaleString()} = ${fabw.toFixed(2)} g`;

        // DOM Updates - Eq. 3
        const adwgValEl = document.getElementById("gm-res-adwg-val");
        const adwgBadgeEl = document.getElementById("gm-res-adwg-badge");
        const weeklyGainEl = document.getElementById("gm-res-weekly-gain");
        const subAdwgEl = document.getElementById("gm-sub-adwg");
        if (adwgValEl) adwgValEl.textContent = adwg.toFixed(4);
        if (weeklyGainEl) weeklyGainEl.textContent = weeklyGain.toFixed(3);
        if (subAdwgEl) subAdwgEl.innerHTML = `(${fabw.toFixed(2)} - ${ibwVal.toFixed(3)}) / ${docDays} = ${adwg.toFixed(4)} g/day`;
        if (adwgBadgeEl) {
            if (adwg >= 0.25) {
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

        // DOM Updates - Eq. 4
        const sgrValEl = document.getElementById("gm-res-sgr-val");
        const weightMultEl = document.getElementById("gm-res-weight-mult");
        const subSgrEl = document.getElementById("gm-sub-sgr");
        if (sgrValEl) sgrValEl.textContent = sgr.toFixed(3);
        if (weightMultEl) weightMultEl.textContent = `${Math.round(weightMult).toLocaleString()}×`;
        if (subSgrEl) subSgrEl.innerHTML = `((ln ${fabw.toFixed(2)} - ln ${ibwVal.toFixed(3)}) / ${docDays}) &times; 100 = ${sgr.toFixed(3)}%`;

        // DOM Updates - Eqs. 5 & 6
        const ibKgEl = document.getElementById("gm-res-ib-kg");
        const fbKgEl = document.getElementById("gm-res-fb-kg");
        const netBioEl = document.getElementById("gm-res-net-biomass");
        const subBioEl = document.getElementById("gm-sub-biomass");
        if (ibKgEl) ibKgEl.textContent = ibKg.toFixed(2);
        if (fbKgEl) fbKgEl.textContent = fbKg.toFixed(2);
        if (netBioEl) netBioEl.textContent = netGainKg.toFixed(2);
        if (subBioEl) subBioEl.innerHTML = `Gain: ${fbKg.toFixed(2)} kg - ${ibKg.toFixed(2)} kg = ${netGainKg.toFixed(2)} kg`;

        // DOM Updates - Eq. 7
        const fcrValEl = document.getElementById("gm-res-fcr-val");
        const fcrBadgeEl = document.getElementById("gm-res-fcr-badge");
        const feedEffEl = document.getElementById("gm-res-feed-efficiency");
        const subFcrEl = document.getElementById("gm-sub-fcr");
        if (fcrValEl) fcrValEl.textContent = fcr.toFixed(3);
        if (feedEffEl) feedEffEl.textContent = `${feedEfficiency.toFixed(2)}%`;
        if (subFcrEl) subFcrEl.innerHTML = `${tfgKg.toFixed(1)} kg / ${netGainKg.toFixed(2)} kg = ${fcr.toFixed(3)}`;
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

        // DOM Updates - Eq. 8
        const kValEl = document.getElementById("gm-res-k-val");
        const kBadgeEl = document.getElementById("gm-res-k-badge");
        const kProfileEl = document.getElementById("gm-res-k-profile");
        const subKEl = document.getElementById("gm-sub-k");
        if (kValEl) kValEl.textContent = kFactor.toFixed(4);
        if (subKEl) subKEl.innerHTML = `(${fabw.toFixed(2)} / ${tlCm.toFixed(1)}&sup3;) &times; 100 = ${kFactor.toFixed(4)}`;
        if (kBadgeEl && kProfileEl) {
            if (kFactor >= 0.80 && kFactor <= 1.15) {
                kBadgeEl.textContent = "Optimal Condition";
                kBadgeEl.className = "wqi-metric-badge badge-optimal";
                kProfileEl.textContent = "Healthy, well-proportioned robust girth";
            } else if (kFactor < 0.80) {
                kBadgeEl.textContent = "Slender / Lean";
                kBadgeEl.className = "wqi-metric-badge badge-warning";
                kProfileEl.textContent = "Slender body profile; check feeding assimilation or post-molt state";
            } else {
                kBadgeEl.textContent = "Heavy / Plump";
                kBadgeEl.className = "wqi-metric-badge badge-optimal";
                kProfileEl.textContent = "High muscle density and heavy carapace girth";
            }
        }

        // Sync to individual calculators
        syncMasterToIndividual({
            isCount, lhcCount, docDays, ibwVal, bwInput, bwUnit, tfgInput, feedUnit, tlCm,
            fabw, ibKg, fbKg, tfgKg
        });
    }

    function syncMasterToIndividual(data) {
        const indivIs = document.getElementById("indiv-is");
        const indivLhc = document.getElementById("indiv-lhc");
        if (indivIs && !indivIs.dataset.manualEdited) indivIs.value = data.isCount;
        if (indivLhc && !indivLhc.dataset.manualEdited) indivLhc.value = data.lhcCount;

        const indivBw = document.getElementById("indiv-bw");
        const indivBwUnit = document.getElementById("indiv-bw-unit");
        const indivFabwLhc = document.getElementById("indiv-fabw-lhc");
        if (indivBw && !indivBw.dataset.manualEdited) indivBw.value = data.bwInput;
        if (indivBwUnit && !indivBwUnit.dataset.manualEdited) indivBwUnit.value = data.bwUnit;
        if (indivFabwLhc && !indivFabwLhc.dataset.manualEdited) indivFabwLhc.value = data.lhcCount;

        const indivGrowIbw = document.getElementById("indiv-grow-ibw");
        const indivGrowFabw = document.getElementById("indiv-grow-fabw");
        const indivGrowDoc = document.getElementById("indiv-grow-doc");
        if (indivGrowIbw && !indivGrowIbw.dataset.manualEdited) indivGrowIbw.value = data.ibwVal;
        if (indivGrowFabw && !indivGrowFabw.dataset.manualEdited) indivGrowFabw.value = data.fabw.toFixed(2);
        if (indivGrowDoc && !indivGrowDoc.dataset.manualEdited) indivGrowDoc.value = data.docDays;

        const indivBioIs = document.getElementById("indiv-bio-is");
        const indivBioIbw = document.getElementById("indiv-bio-ibw");
        const indivBioLhc = document.getElementById("indiv-bio-lhc");
        const indivBioFabw = document.getElementById("indiv-bio-fabw");
        if (indivBioIs && !indivBioIs.dataset.manualEdited) indivBioIs.value = data.isCount;
        if (indivBioIbw && !indivBioIbw.dataset.manualEdited) indivBioIbw.value = data.ibwVal;
        if (indivBioLhc && !indivBioLhc.dataset.manualEdited) indivBioLhc.value = data.lhcCount;
        if (indivBioFabw && !indivBioFabw.dataset.manualEdited) indivBioFabw.value = data.fabw.toFixed(2);

        const indivFcrTfg = document.getElementById("indiv-fcr-tfg");
        const indivFcrTfgUnit = document.getElementById("indiv-fcr-tfg-unit");
        const indivFcrFb = document.getElementById("indiv-fcr-fb");
        const indivFcrIb = document.getElementById("indiv-fcr-ib");
        if (indivFcrTfg && !indivFcrTfg.dataset.manualEdited) indivFcrTfg.value = data.tfgInput;
        if (indivFcrTfgUnit && !indivFcrTfgUnit.dataset.manualEdited) indivFcrTfgUnit.value = data.feedUnit;
        if (indivFcrFb && !indivFcrFb.dataset.manualEdited) indivFcrFb.value = data.fbKg.toFixed(2);
        if (indivFcrIb && !indivFcrIb.dataset.manualEdited) indivFcrIb.value = data.ibKg.toFixed(2);

        const indivKFabw = document.getElementById("indiv-k-fabw");
        const indivKTl = document.getElementById("indiv-k-tl");
        if (indivKFabw && !indivKFabw.dataset.manualEdited) indivKFabw.value = data.fabw.toFixed(2);
        if (indivKTl && !indivKTl.dataset.manualEdited) indivKTl.value = data.tlCm.toFixed(1);

        calculateIndividualSR();
        calculateIndividualFABW();
        calculateIndividualGrowth();
        calculateIndividualBiomass();
        calculateIndividualFCR();
        calculateIndividualK();
    }

    // Individual Eq. 1: Survival Rate
    function calculateIndividualSR() {
        const isCount = Math.max(1, Number(document.getElementById("indiv-is")?.value || 100000));
        const lhcCount = Math.max(1, Number(document.getElementById("indiv-lhc")?.value || 85000));

        const sr = (lhcCount / isCount) * 100.0;
        const mortalityCount = Math.max(0, isCount - lhcCount);
        const mortalityPct = Math.max(0, 100.0 - sr);

        const resEl = document.getElementById("indiv-sr-result");
        const badgeEl = document.getElementById("indiv-sr-badge");
        const mortCountEl = document.getElementById("indiv-sr-mortality-count");
        const mortPctEl = document.getElementById("indiv-sr-mortality-pct");
        const stepMathEl = document.getElementById("indiv-sr-step-math");
        const ratingEl = document.getElementById("indiv-sr-rating");

        if (resEl) resEl.textContent = sr.toFixed(2);
        if (mortCountEl) mortCountEl.textContent = `${Math.round(mortalityCount).toLocaleString()} shrimp`;
        if (mortPctEl) mortPctEl.textContent = `${mortalityPct.toFixed(2)}%`;
        if (stepMathEl) stepMathEl.innerHTML = `SR = (${lhcCount.toLocaleString()} / ${isCount.toLocaleString()}) &times; 100 = ${sr.toFixed(2)}%`;

        if (badgeEl && ratingEl) {
            if (sr >= 80.0) {
                badgeEl.textContent = "Optimal";
                badgeEl.className = "wqi-metric-badge badge-optimal";
                ratingEl.textContent = "Optimal survival rate exceeding typical commercial benchmark (≥80%). Favorable pond conditions and healthy stock transition.";
            } else if (sr >= 65.0) {
                badgeEl.textContent = "Acceptable";
                badgeEl.className = "wqi-metric-badge badge-warning";
                ratingEl.textContent = "Moderate survival rate (65%–79%). Review benthic sediment conditions, feeding tray consumption, and stocking density.";
            } else {
                badgeEl.textContent = "Suboptimal";
                badgeEl.className = "wqi-metric-badge badge-critical";
                ratingEl.textContent = "Low survival rate (<65%). Investigate potential pathogen pressure, nocturnal hypoxia, or predator interference.";
            }
        }
    }

    // Individual Eq. 2: Final Average Body Weight
    function calculateIndividualFABW() {
        const bwInput = Math.max(0.1, Number(document.getElementById("indiv-bw")?.value || 1700));
        const bwUnit = document.getElementById("indiv-bw-unit")?.value || "kg";
        const lhcCount = Math.max(1, Number(document.getElementById("indiv-fabw-lhc")?.value || 85000));

        const bwGrams = bwUnit === "kg" ? bwInput * 1000.0 : bwInput;
        const bwKg = bwGrams / 1000.0;
        const fabw = bwGrams / lhcCount;
        const countPerKg = fabw > 0 ? (1000.0 / fabw) : 0;

        const resEl = document.getElementById("indiv-fabw-result");
        const countEl = document.getElementById("indiv-fabw-count-per-kg");
        const bulkEl = document.getElementById("indiv-fabw-bulk-kg");
        const stepEl = document.getElementById("indiv-fabw-step-math");

        if (resEl) resEl.textContent = fabw.toFixed(2);
        if (countEl) countEl.textContent = `${countPerKg.toFixed(1)} pcs / kg`;
        if (bulkEl) bulkEl.textContent = `${bwKg.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} kg (${Math.round(bwGrams).toLocaleString()} g)`;
        if (stepEl) stepEl.innerHTML = `FABW = ${Math.round(bwGrams).toLocaleString()} g / ${lhcCount.toLocaleString()} shrimp = ${fabw.toFixed(2)} g`;
    }

    // Individual Eqs. 3 & 4: ADWG & SGR
    function calculateIndividualGrowth() {
        const ibw = Math.max(0.0001, Number(document.getElementById("indiv-grow-ibw")?.value || 0.010));
        const fabw = Math.max(0.01, Number(document.getElementById("indiv-grow-fabw")?.value || 20.00));
        const doc = Math.max(1, Number(document.getElementById("indiv-grow-doc")?.value || 90));

        const adwg = (fabw - ibw) / doc;
        const weeklyGain = adwg * 7.0;
        const sgr = ((Math.log(fabw) - Math.log(ibw)) / doc) * 100.0;
        const mult = fabw / ibw;

        const adwgEl = document.getElementById("indiv-adwg-result");
        const adwgBadgeEl = document.getElementById("indiv-adwg-badge");
        const weeklyEl = document.getElementById("indiv-adwg-weekly");
        const sgrEl = document.getElementById("indiv-sgr-result");
        const sgrMultEl = document.getElementById("indiv-sgr-mult");
        const adwgStepEl = document.getElementById("indiv-adwg-step-math");
        const sgrStepEl = document.getElementById("indiv-sgr-step-math");

        if (adwgEl) adwgEl.textContent = adwg.toFixed(4);
        if (weeklyEl) weeklyEl.textContent = `${weeklyGain.toFixed(3)} g / week`;
        if (sgrEl) sgrEl.textContent = sgr.toFixed(3);
        if (sgrMultEl) sgrMultEl.textContent = `${Math.round(mult).toLocaleString()}×`;
        if (adwgStepEl) adwgStepEl.innerHTML = `(${fabw.toFixed(2)} - ${ibw.toFixed(3)}) / ${doc} = ${adwg.toFixed(4)} g/day`;
        if (sgrStepEl) sgrStepEl.innerHTML = `[(ln ${fabw.toFixed(2)} - ln ${ibw.toFixed(3)}) / ${doc}] &times; 100 = ${sgr.toFixed(3)}%/day`;

        if (adwgBadgeEl) {
            if (adwg >= 0.25) {
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
    }

    // Individual Eqs. 5 & 6: Biomass (IB & FB)
    function calculateIndividualBiomass() {
        const isCount = Math.max(1, Number(document.getElementById("indiv-bio-is")?.value || 100000));
        const ibw = Math.max(0.0001, Number(document.getElementById("indiv-bio-ibw")?.value || 0.010));
        const lhcCount = Math.max(1, Number(document.getElementById("indiv-bio-lhc")?.value || 85000));
        const fabw = Math.max(0.01, Number(document.getElementById("indiv-bio-fabw")?.value || 20.00));

        const ibGrams = isCount * ibw;
        const ibKg = ibGrams / 1000.0;
        const fbGrams = lhcCount * fabw;
        const fbKg = fbGrams / 1000.0;
        const gainKg = Math.max(0, fbKg - ibKg);

        const ibEl = document.getElementById("indiv-bio-ib-val");
        const ibSubEl = document.getElementById("indiv-bio-ib-sub");
        const fbEl = document.getElementById("indiv-bio-fb-val");
        const fbSubEl = document.getElementById("indiv-bio-fb-sub");
        const gainEl = document.getElementById("indiv-bio-gain-val");
        const ibStepEl = document.getElementById("indiv-bio-ib-step");
        const fbStepEl = document.getElementById("indiv-bio-fb-step");

        if (ibEl) ibEl.textContent = `${ibKg.toFixed(2)} kg`;
        if (ibSubEl) ibSubEl.textContent = `(${Math.round(ibGrams).toLocaleString()} g)`;
        if (fbEl) fbEl.textContent = `${fbKg.toFixed(2)} kg`;
        if (fbSubEl) fbSubEl.textContent = `(${Math.round(fbGrams).toLocaleString()} g)`;
        if (gainEl) gainEl.textContent = `${gainKg.toFixed(2)} kg (${(gainKg / 1000.0).toFixed(2)} metric tons)`;
        if (ibStepEl) ibStepEl.innerHTML = `${isCount.toLocaleString()} &times; ${ibw.toFixed(3)} g = ${Math.round(ibGrams).toLocaleString()} g (${ibKg.toFixed(2)} kg)`;
        if (fbStepEl) fbStepEl.innerHTML = `${lhcCount.toLocaleString()} &times; ${fabw.toFixed(2)} g = ${Math.round(fbGrams).toLocaleString()} g (${fbKg.toFixed(2)} kg)`;
    }

    // Individual Eq. 7: Feed Conversion Ratio
    function calculateIndividualFCR() {
        const tfgInput = Math.max(0.1, Number(document.getElementById("indiv-fcr-tfg")?.value || 2125));
        const feedUnit = document.getElementById("indiv-fcr-tfg-unit")?.value || "kg";
        const fbKg = Math.max(0.1, Number(document.getElementById("indiv-fcr-fb")?.value || 1700));
        const ibKg = Math.max(0.001, Number(document.getElementById("indiv-fcr-ib")?.value || 1.0));

        const tfgKg = feedUnit === "kg" ? tfgInput : tfgInput / 1000.0;
        const gainKg = Math.max(0.001, fbKg - ibKg);
        const fcr = tfgKg / gainKg;
        const efficiency = fcr > 0 ? (100.0 / fcr) : 0;

        const resEl = document.getElementById("indiv-fcr-result");
        const badgeEl = document.getElementById("indiv-fcr-badge");
        const effEl = document.getElementById("indiv-fcr-efficiency");
        const gainDescEl = document.getElementById("indiv-fcr-gain-desc");
        const stepEl = document.getElementById("indiv-fcr-step-math");
        const ratingEl = document.getElementById("indiv-fcr-rating");

        if (resEl) resEl.textContent = fcr.toFixed(3);
        if (effEl) effEl.textContent = `${efficiency.toFixed(2)}%`;
        if (gainDescEl) gainDescEl.textContent = `${gainKg.toFixed(2)} kg`;
        if (stepEl) stepEl.innerHTML = `FCR = ${tfgKg.toFixed(1)} kg / (${fbKg.toFixed(1)} - ${ibKg.toFixed(1)}) kg = ${fcr.toFixed(3)}`;

        if (badgeEl && ratingEl) {
            if (fcr < 1.20) {
                badgeEl.textContent = "Exceptional (<1.20)";
                badgeEl.className = "wqi-metric-badge badge-optimal";
                ratingEl.textContent = "Outstanding feed efficiency (<1.20). Excellent nutrient assimilation and minimum uneaten pellet degradation.";
            } else if (fcr <= 1.50) {
                badgeEl.textContent = "Optimal (1.20–1.50)";
                badgeEl.className = "wqi-metric-badge badge-optimal";
                ratingEl.textContent = "Standard target commercial FCR (1.20–1.50) for Penaeus vannamei culture.";
            } else if (fcr <= 1.80) {
                badgeEl.textContent = "Acceptable (1.51–1.80)";
                badgeEl.className = "wqi-metric-badge badge-warning";
                ratingEl.textContent = "Moderate feed efficiency (1.51–1.80). Regularly inspect feed check trays to prevent overfeeding and ammonia spikes.";
            } else {
                badgeEl.textContent = "Suboptimal (>1.80)";
                badgeEl.className = "wqi-metric-badge badge-critical";
                ratingEl.textContent = "High FCR (>1.80). Signals feed wastage, biological stress, low dissolved oxygen, or pellet disintegration.";
            }
        }
    }

    // Individual Eq. 8: Fulton's Condition Factor
    function calculateIndividualK() {
        const fabw = Math.max(0.1, Number(document.getElementById("indiv-k-fabw")?.value || 20.00));
        const tlCm = Math.max(0.1, Number(document.getElementById("indiv-k-tl")?.value || 12.9));

        const tlCubed = Math.pow(tlCm, 3);
        const kFactor = (fabw / tlCubed) * 100.0;

        const resEl = document.getElementById("indiv-k-result");
        const badgeEl = document.getElementById("indiv-k-badge");
        const sumEl = document.getElementById("indiv-k-summary");
        const stepEl = document.getElementById("indiv-k-step-math");
        const ratingEl = document.getElementById("indiv-k-rating");

        if (resEl) resEl.textContent = kFactor.toFixed(4);
        if (stepEl) stepEl.innerHTML = `K = (${fabw.toFixed(2)} / ${tlCm.toFixed(1)}&sup3;) &times; 100 = (${fabw.toFixed(2)} / ${tlCubed.toFixed(3)}) &times; 100 = ${kFactor.toFixed(4)}`;

        if (badgeEl && sumEl && ratingEl) {
            if (kFactor >= 0.80 && kFactor <= 1.15) {
                badgeEl.textContent = "Optimal Condition";
                badgeEl.className = "wqi-metric-badge badge-optimal";
                sumEl.textContent = "Robust & Well-proportioned";
                ratingEl.textContent = "A Fulton's condition factor between 0.80 and 1.15 is the ideal biological index for healthy commercial Penaeus vannamei, denoting dense muscle tissue and robust carapace girth.";
            } else if (kFactor < 0.80) {
                badgeEl.textContent = "Slender / Lean";
                badgeEl.className = "wqi-metric-badge badge-warning";
                sumEl.textContent = "Slender Body Profile";
                ratingEl.textContent = "K < 0.80 suggests lean body mass. Check if shrimp recently completed ecdysis (molting) or require increased dietary protein/energy.";
            } else {
                badgeEl.textContent = "Heavy / Plump";
                badgeEl.className = "wqi-metric-badge badge-optimal";
                sumEl.textContent = "High Carapace Girth & Muscle Density";
                ratingEl.textContent = "K > 1.15 indicates dense muscle filling and excellent abdominal meat ratio.";
            }
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

    const gmBtnCalc = document.getElementById("gm-btn-calculate");
    if (gmBtnCalc) {
        gmBtnCalc.addEventListener("click", calculateMasterGrowth);
    }

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

            // Clear manual edited dataset on individual inputs so preset propagates
            document.querySelectorAll(".individual-growth-panel input, .individual-growth-panel select").forEach(el => {
                delete el.dataset.manualEdited;
            });

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

    // Individual Input Event Listeners
    // Eq. 1
    ["indiv-is", "indiv-lhc"].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", () => {
                el.dataset.manualEdited = "true";
                calculateIndividualSR();
            });
            el.addEventListener("change", () => {
                el.dataset.manualEdited = "true";
                calculateIndividualSR();
            });
        }
    });
    const btnEq1 = document.getElementById("btn-calc-eq1");
    if (btnEq1) btnEq1.addEventListener("click", calculateIndividualSR);

    // Eq. 2
    ["indiv-bw", "indiv-bw-unit", "indiv-fabw-lhc"].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", () => {
                el.dataset.manualEdited = "true";
                calculateIndividualFABW();
            });
            el.addEventListener("change", () => {
                el.dataset.manualEdited = "true";
                calculateIndividualFABW();
            });
        }
    });
    const btnEq2 = document.getElementById("btn-calc-eq2");
    if (btnEq2) btnEq2.addEventListener("click", calculateIndividualFABW);

    // Eqs. 3 & 4
    ["indiv-grow-ibw", "indiv-grow-fabw", "indiv-grow-doc"].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", () => {
                el.dataset.manualEdited = "true";
                calculateIndividualGrowth();
            });
            el.addEventListener("change", () => {
                el.dataset.manualEdited = "true";
                calculateIndividualGrowth();
            });
        }
    });
    const btnEq34 = document.getElementById("btn-calc-eq34");
    if (btnEq34) btnEq34.addEventListener("click", calculateIndividualGrowth);

    // Eqs. 5 & 6
    ["indiv-bio-is", "indiv-bio-ibw", "indiv-bio-lhc", "indiv-bio-fabw"].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", () => {
                el.dataset.manualEdited = "true";
                calculateIndividualBiomass();
            });
            el.addEventListener("change", () => {
                el.dataset.manualEdited = "true";
                calculateIndividualBiomass();
            });
        }
    });
    const btnEq56 = document.getElementById("btn-calc-eq56");
    if (btnEq56) btnEq56.addEventListener("click", calculateIndividualBiomass);

    // Eq. 7
    ["indiv-fcr-tfg", "indiv-fcr-tfg-unit", "indiv-fcr-fb", "indiv-fcr-ib"].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", () => {
                el.dataset.manualEdited = "true";
                calculateIndividualFCR();
            });
            el.addEventListener("change", () => {
                el.dataset.manualEdited = "true";
                calculateIndividualFCR();
            });
        }
    });
    const btnEq7 = document.getElementById("btn-calc-eq7");
    if (btnEq7) btnEq7.addEventListener("click", calculateIndividualFCR);

    // Eq. 8
    ["indiv-k-fabw", "indiv-k-tl"].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", () => {
                el.dataset.manualEdited = "true";
                calculateIndividualK();
            });
            el.addEventListener("change", () => {
                el.dataset.manualEdited = "true";
                calculateIndividualK();
            });
        }
    });
    const btnEq8 = document.getElementById("btn-calc-eq8");
    if (btnEq8) btnEq8.addEventListener("click", calculateIndividualK);


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
        calculateMasterGrowth();
    }

    boot();
    setInterval(fetchLatestTelemetry, 15000);
});

