with open("static/js/calculators.js", "r", encoding="utf-8") as f:
    js = f.read()

def normalize(s):
    return s.replace("\r\n", "\n")

js_norm = normalize(js)

ai_modal_logic = """    // -------------------------------------------------------------
    // Gemini AI Biological Decision Support Modal & Execution
    // -------------------------------------------------------------
    const aiDecisionModal = document.getElementById("ai-decision-modal");
    const closeAiModalBtn = document.getElementById("close-ai-modal");
    const closeAiModalAction = document.getElementById("close-ai-modal-action");
    const btnAnalyzeWithAi = document.getElementById("btn-analyze-with-ai");
    const btnReanalyzeAi = document.getElementById("btn-reanalyze-ai");

    const aiModalBadge = document.getElementById("ai-modal-badge");
    const aiModalFocusName = document.getElementById("ai-modal-focus-name");
    const aiModalTempVal = document.getElementById("ai-modal-temp-val");
    const aiModalKeyMetric = document.getElementById("ai-modal-key-metric");
    const aiModalEvalText = document.getElementById("ai-modal-eval-text");
    const aiModalActionsList = document.getElementById("ai-modal-actions-list");
    const aiModalSourceStamp = document.getElementById("ai-modal-source-stamp");

    function openAiDecisionModal() {
        if (!aiDecisionModal) return;
        aiDecisionModal.hidden = false;
        document.body.style.overflow = "hidden";
    }

    function closeAiDecisionModal() {
        if (!aiDecisionModal) return;
        aiDecisionModal.hidden = true;
        document.body.style.overflow = "";
    }

    function getActiveModuleKey() {
        try {
            const stored = localStorage.getItem("shrimpguard_active_calc_module");
            if (stored && stored !== "all" && stored !== "standards") return stored;
        } catch (e) {}

        const activeItem = document.querySelector(".module-dropdown-item.active");
        if (activeItem && activeItem.dataset.module && activeItem.dataset.module !== "all") {
            return activeItem.dataset.module;
        }
        return "feeding";
    }

    function getModuleContextLabels(moduleKey) {
        const temp = (liveSensor ? liveSensor.temperature.toFixed(1) : "29.5") + " °C";
        if (moduleKey === "feeding") {
            const feedKg = document.getElementById("res-adjusted-feed")?.textContent || "24.5";
            const bioKg = document.getElementById("res-biomass-kg")?.textContent || "765.0";
            return {
                focus: "Feeding Management",
                temp: temp,
                metric: `${feedKg} kg/day (${bioKg} kg Biomass)`
            };
        } else if (moduleKey === "growth") {
            const fcr = document.getElementById("gm-res-fcr-val")?.textContent || "1.25";
            const adwg = document.getElementById("gm-res-adwg-val")?.textContent || "0.222";
            return {
                focus: "Growth Performance (Eqs. 1–8)",
                temp: temp,
                metric: `FCR: ${fcr} • ADWG: ${adwg} g/day`
            };
        } else if (moduleKey === "remediation") {
            const lime = document.getElementById("lime-dosage-kg")?.textContent || "54.0";
            const molasses = document.getElementById("molasses-dosage-kg")?.textContent || "18.4";
            return {
                focus: "Water Remediation & Dosing",
                temp: temp,
                metric: `Lime: ${lime} kg • Carbon: ${molasses} kg`
            };
        } else if (moduleKey === "ammonia") {
            const nh3 = document.getElementById("tools-ammonia-result")?.textContent || "0.0224";
            const tan = document.getElementById("tools-ammonia-tan")?.value || "0.80";
            return {
                focus: "Unionized Ammonia (NH₃) Toxicity",
                temp: temp,
                metric: `Toxic NH₃: ${nh3} ppm (TAN: ${tan} ppm)`
            };
        } else if (moduleKey === "co2") {
            const co2 = document.getElementById("tools-co2-result")?.textContent || "6.75";
            const alk = document.getElementById("tools-co2-alkalinity")?.value || "140";
            return {
                focus: "Free Carbon Dioxide (CO₂)",
                temp: temp,
                metric: `Free CO₂: ${co2} mg/L (Alkalinity: ${alk} mg/L)`
            };
        }
        return { focus: "Aquaculture Calculation", temp: temp, metric: "Live Pond Sensor Data" };
    }

    async function executeAiDecisionAnalysis(triggerBtn = null) {
        const moduleKey = getActiveModuleKey();
        const data = collectModuleDataForAi(moduleKey);
        const meta = getModuleContextLabels(moduleKey);

        if (triggerBtn) {
            triggerBtn.classList.add("is-loading");
            triggerBtn.disabled = true;
            const span = triggerBtn.querySelector("span");
            if (span) span.textContent = "Analyzing with AI...";
        }

        try {
            const resp = await fetch("/api/calculators/ai-insight", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ module: moduleKey, data: data })
            });
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const result = await resp.json();

            // Populate Modal Content
            if (aiModalFocusName) aiModalFocusName.textContent = meta.focus;
            if (aiModalTempVal) aiModalTempVal.textContent = meta.temp;
            if (aiModalKeyMetric) aiModalKeyMetric.textContent = meta.metric;

            if (aiModalBadge && result.status) {
                aiModalBadge.textContent = result.status;
                aiModalBadge.className = `ai-status-pill badge-${result.status.toLowerCase()}`;
            }

            if (aiModalEvalText && result.evaluation) {
                aiModalEvalText.textContent = result.evaluation;
            }

            if (aiModalActionsList && Array.isArray(result.action_items)) {
                aiModalActionsList.innerHTML = "";
                result.action_items.forEach(action => {
                    const li = document.createElement("li");
                    li.textContent = action;
                    aiModalActionsList.appendChild(li);
                });
            }

            if (aiModalSourceStamp && result.source) {
                aiModalSourceStamp.textContent = `Powered by ${result.source} • Penaeus vannamei Engine`;
            }

            // Open the Dialog Pop-up
            openAiDecisionModal();

        } catch (err) {
            console.error("AI Decision Analysis failed:", err);
            alert("Could not complete AI analysis at this moment. Please try again.");
        } finally {
            if (triggerBtn) {
                triggerBtn.classList.remove("is-loading");
                triggerBtn.disabled = false;
                const span = triggerBtn.querySelector("span");
                if (span) span.textContent = "Analyze with AI";
            }
        }
    }

    function initAiModalListeners() {
        if (btnAnalyzeWithAi) {
            btnAnalyzeWithAi.addEventListener("click", () => executeAiDecisionAnalysis(btnAnalyzeWithAi));
        }

        if (btnReanalyzeAi) {
            btnReanalyzeAi.addEventListener("click", () => executeAiDecisionAnalysis(btnReanalyzeAi));
        }

        if (closeAiModalBtn) {
            closeAiModalBtn.addEventListener("click", closeAiDecisionModal);
        }

        if (closeAiModalAction) {
            closeAiModalAction.addEventListener("click", closeAiDecisionModal);
        }

        if (aiDecisionModal) {
            aiDecisionModal.addEventListener("click", (e) => {
                if (e.target === aiDecisionModal) closeAiDecisionModal();
            });
        }

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && aiDecisionModal && !aiDecisionModal.hidden) {
                closeAiDecisionModal();
            }
        });
    }
"""

target_ai_block = """    async function requestCalculatorAiInsight(moduleKey, triggerBtn = null) {
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
    }"""

assert normalize(target_ai_block) in js_norm, "target_ai_block not found in calculators.js"
js_norm = js_norm.replace(normalize(target_ai_block), normalize(ai_modal_logic), 1)

target_init_call = """initCalculatorAiInsights();"""
replacement_init_call = """initAiModalListeners();"""
assert normalize(target_init_call) in js_norm, "target_init_call not found in calculators.js"
js_norm = js_norm.replace(normalize(target_init_call), normalize(replacement_init_call), 1)

with open("static/js/calculators.js", "w", encoding="utf-8") as f:
    f.write(js_norm)

print("Updated static/js/calculators.js with AI Decision Support popup modal logic successfully!")

