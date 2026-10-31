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
