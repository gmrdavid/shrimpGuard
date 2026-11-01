with open("static/js/calculators.js", "r", encoding="utf-8") as f:
    js = f.read()

def normalize(s):
    return s.replace("\r\n", "\n")

js_norm = normalize(js)

ai_functions_code = """
    // -------------------------------------------------------------
    // Gemini AI Biological Decision Support Engine for Calculators
    // -------------------------------------------------------------
    function collectModuleDataForAi(moduleKey) {
        if (moduleKey === "feeding") {
            const area = parseFloat(document.getElementById("feed-pond-area")?.value) || 1000;
            const depth = parseFloat(document.getElementById("feed-pond-depth")?.value) || 1.2;
            const density = parseFloat(document.getElementById("feed-stocking-density")?.value) || 60;
            const survival = parseFloat(document.getElementById("feed-survival-rate")?.value) || 85;
            const abw = parseFloat(document.getElementById("feed-abw")?.value) || 15.0;
            const base_rate = parseFloat(document.getElementById("feed-rate-percent")?.value) || 3.2;
            const meals = parseInt(document.getElementById("feed-meals-day")?.value, 10) || 4;
            const temp = parseFloat(document.getElementById("feed-current-temp")?.value) || (liveSensor ? liveSensor.temperature : 29.5);
            const biomass_kg = parseFloat(document.getElementById("res-biomass-kg")?.textContent) || 765.0;
            const adjusted_feed_kg = parseFloat(document.getElementById("res-adjusted-feed")?.textContent) || 24.5;
            const temp_factor = parseFloat(document.getElementById("res-temp-factor")?.textContent.replace("×", "")) || 1.0;
            return { area, depth, density, survival, abw, base_rate, meals, temp, biomass_kg, adjusted_feed_kg, temp_factor };
        } else if (moduleKey === "growth") {
            const doc = parseFloat(document.getElementById("gm-doc")?.value) || 90;
            const initial_stocking = parseFloat(document.getElementById("gm-init-stock")?.value) || 100000;
            const live_count = parseFloat(document.getElementById("gm-live-count")?.value) || 85000;
            const survival_rate = parseFloat(document.getElementById("gm-res-sr-val")?.textContent) || 85.0;
            const fabw = parseFloat(document.getElementById("gm-res-fabw-val")?.textContent) || 20.0;
            const adwg = parseFloat(document.getElementById("gm-res-adwg-val")?.textContent) || 0.222;
            const sgr = parseFloat(document.getElementById("gm-res-sgr-val")?.textContent) || 8.44;
            const final_biomass = parseFloat(document.getElementById("gm-res-fb-val")?.textContent) || 1700.0;
            const fcr = parseFloat(document.getElementById("gm-res-fcr-val")?.textContent) || 1.25;
            const k_factor = parseFloat(document.getElementById("gm-res-k-val")?.textContent) || 0.85;
            return { doc, initial_stocking, live_count, survival_rate, fabw, adwg, sgr, final_biomass, fcr, k_factor };
        } else if (moduleKey === "remediation") {
            const lime_ph = parseFloat(document.getElementById("lime-current-ph")?.value) || 7.2;
            const lime_target = parseFloat(document.getElementById("lime-target-ph")?.value) || 8.0;
            const pond_volume = parseFloat(document.getElementById("lime-pond-volume")?.value) || 1200;
            const lime_kg = parseFloat(document.getElementById("lime-dosage-kg")?.textContent) || 54.0;
            const daily_feed = parseFloat(document.getElementById("molasses-daily-feed")?.value) || 25.0;
            const protein_pct = parseFloat(document.getElementById("molasses-protein-pct")?.value) || 35;
            const target_cn = parseFloat(document.getElementById("molasses-target-cn")?.value) || 15;
            const carbon_source = document.getElementById("molasses-carbon-source")?.value || "cane_molasses";
            const molasses_kg = parseFloat(document.getElementById("molasses-dosage-kg")?.textContent) || 18.4;
            const biomass_aero = parseFloat(document.getElementById("aero-biomass-input")?.value) || 1000.0;
            const target_do = parseFloat(document.getElementById("aero-target-do")?.value) || 5.0;
            const temp_aero = parseFloat(document.getElementById("aero-temp-input")?.value) || 29.5;
            const aerator_hp = parseFloat(document.getElementById("aero-power-hp")?.textContent) || 2.0;
            return { lime_ph, lime_target, pond_volume, lime_kg, daily_feed, protein_pct, target_cn, carbon_source, molasses_kg, biomass_aero, target_do, temp_aero, aerator_hp };
        } else if (moduleKey === "ammonia") {
            const tan = parseFloat(document.getElementById("tools-ammonia-tan")?.value) || 0.8;
            const temp = parseFloat(document.getElementById("tools-step-temp")?.textContent.replace("°C", "")) || 28.0;
            const ph = parseFloat(document.getElementById("tools-step-ph")?.textContent) || 7.6;
            const salinity = parseFloat(document.getElementById("tools-ammonia-salinity")?.value) || 20.0;
            const nh3_ppm = parseFloat(document.getElementById("tools-ammonia-result")?.textContent) || 0.0224;
            const factor = parseFloat(document.getElementById("tools-step-factor")?.textContent) || 0.028;
            return { tan, temp, ph, salinity, nh3_ppm, factor };
        } else if (moduleKey === "co2") {
            const alkalinity = parseFloat(document.getElementById("tools-co2-alkalinity")?.value) || 140.0;
            const temp = parseFloat(document.getElementById("tools-co2-step-temp")?.textContent.replace("°C", "")) || 28.0;
            const ph = parseFloat(document.getElementById("tools-co2-step-ph")?.textContent) || 7.6;
            const co2_ppm = parseFloat(document.getElementById("tools-co2-result")?.textContent) || 6.75;
            const factor = parseFloat(document.getElementById("tools-co2-step-factor")?.textContent) || 0.0482;
            return { alkalinity, temp, ph, co2_ppm, factor };
        }
        return {};
    }

    async function requestCalculatorAiInsight(moduleKey, triggerBtn = null) {
        if (!moduleKey || moduleKey === "all" || moduleKey === "standards") return;
        const data = collectModuleDataForAi(moduleKey);

        const evalEl = document.getElementById(`ai-eval-${moduleKey}`);
        const actionsEl = document.getElementById(`ai-actions-${moduleKey}`);
        const sourceEl = document.getElementById(`ai-source-${moduleKey}`);
        const badgeEl = document.getElementById(`ai-badge-${moduleKey}`);

        if (triggerBtn) {
            triggerBtn.classList.add("is-loading");
            triggerBtn.disabled = true;
            const labelSpan = triggerBtn.querySelector("span");
            if (labelSpan) labelSpan.textContent = "Analyzing with AI...";
        }

        try {
            const resp = await fetch("/api/calculators/ai-insight", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ module: moduleKey, data: data })
            });
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const result = await resp.json();

            if (evalEl && result.evaluation) {
                evalEl.textContent = result.evaluation;
            }

            if (actionsEl && Array.isArray(result.action_items)) {
                actionsEl.innerHTML = "";
                result.action_items.forEach(action => {
                    const li = document.createElement("li");
                    li.textContent = action;
                    actionsEl.appendChild(li);
                });
            }

            if (sourceEl && result.source) {
                sourceEl.textContent = `Powered by ${result.source} • Penaeus vannamei Engine`;
            }

            if (badgeEl && result.status) {
                badgeEl.textContent = result.status;
                const statusLower = result.status.toLowerCase();
                badgeEl.className = `ai-status-pill badge-${statusLower}`;
            }

            // Also synchronize with legacy assessment text if present
            if (moduleKey === "ammonia") {
                const legacyAmmo = document.getElementById("tools-ammonia-assessment-text");
                if (legacyAmmo && result.evaluation) legacyAmmo.textContent = result.evaluation;
            } else if (moduleKey === "co2") {
                const legacyCo2 = document.getElementById("tools-co2-assessment-text");
                if (legacyCo2 && result.evaluation) legacyCo2.textContent = result.evaluation;
            }
        } catch (err) {
            console.warn(`Could not fetch AI insight for module ${moduleKey}:`, err);
        } finally {
            if (triggerBtn) {
                triggerBtn.classList.remove("is-loading");
                triggerBtn.disabled = false;
                const labelSpan = triggerBtn.querySelector("span");
                if (labelSpan) labelSpan.textContent = "Analyze with AI";
            }
        }
    }

    function initCalculatorAiInsights() {
        document.querySelectorAll(".btn-generate-ai-insight").forEach(btn => {
            btn.addEventListener("click", () => {
                const mod = btn.dataset.module;
                if (mod) requestCalculatorAiInsight(mod, btn);
            });
        });
    }
"""

target_before_boot = """    async function boot() {"""
assert normalize(target_before_boot) in js_norm, "target_before_boot not found"
js_norm = js_norm.replace(normalize(target_before_boot), f"{ai_functions_code}\n\n    async function boot() {{", 1)

target_in_boot = """        initComputationModuleSelector();
    }"""
replacement_in_boot = """        initComputationModuleSelector();
        initCalculatorAiInsights();
    }"""
assert normalize(target_in_boot) in js_norm, "target_in_boot not found"
js_norm = js_norm.replace(normalize(target_in_boot), normalize(replacement_in_boot), 1)

with open("static/js/calculators.js", "w", encoding="utf-8") as f:
    f.write(js_norm)

print("Updated static/js/calculators.js with AI insight client integration successfully!")

