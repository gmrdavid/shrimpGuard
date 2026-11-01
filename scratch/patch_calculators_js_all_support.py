with open("static/js/calculators.js", "r", encoding="utf-8") as f:
    js = f.read()

def normalize(s):
    return s.replace("\r\n", "\n")

js_norm = normalize(js)

# 1. Update collectModuleDataForAi to handle "all"
target_collect = """    function collectModuleDataForAi(moduleKey) {
        if (moduleKey === "feeding") {"""

replacement_collect = """    function collectModuleDataForAi(moduleKey) {
        if (moduleKey === "all") {
            return {
                feeding: collectModuleDataForAi("feeding"),
                growth: collectModuleDataForAi("growth"),
                remediation: collectModuleDataForAi("remediation"),
                ammonia: collectModuleDataForAi("ammonia"),
                co2: collectModuleDataForAi("co2")
            };
        } else if (moduleKey === "feeding") {"""

assert normalize(target_collect) in js_norm, "target_collect not found"
js_norm = js_norm.replace(normalize(target_collect), normalize(replacement_collect), 1)

# 2. Update getActiveModuleKey and getModuleContextLabels and executeAiDecisionAnalysis
target_active_key = """    function getActiveModuleKey() {
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
        const meta = getModuleContextLabels(moduleKey);"""

replacement_active_key = """    function getActiveModuleKey() {
        try {
            const stored = localStorage.getItem("shrimpguard_active_calc_module");
            if (stored && stored !== "standards") return stored;
        } catch (e) {}

        const activeItem = document.querySelector(".module-dropdown-item.active");
        if (activeItem && activeItem.dataset.module && activeItem.dataset.module !== "standards") {
            return activeItem.dataset.module;
        }
        return "all";
    }

    function getModuleContextLabels(moduleKey) {
        const temp = (liveSensor ? liveSensor.temperature.toFixed(1) : "29.5") + " °C";
        if (moduleKey === "all") {
            const feedKg = document.getElementById("res-adjusted-feed")?.textContent || "24.5";
            const bioKg = document.getElementById("res-biomass-kg")?.textContent || "765.0";
            const fcr = document.getElementById("gm-res-fcr-val")?.textContent || "1.25";
            const nh3 = document.getElementById("tools-ammonia-result")?.textContent || "0.0224";
            const co2 = document.getElementById("tools-co2-result")?.textContent || "6.75";
            return {
                focus: "Comprehensive Master Assessment (All 5 Modules)",
                temp: temp,
                metric: `Biomass: ${bioKg} kg • Feed: ${feedKg} kg/d • FCR: ${fcr} • NH₃: ${nh3} ppm • CO₂: ${co2} mg/L`
            };
        } else if (moduleKey === "feeding") {
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
        return { focus: "Comprehensive Master Assessment (All 5 Modules)", temp: temp, metric: "Live Pond Sensor Data" };
    }

    async function executeAiDecisionAnalysis(triggerBtn = null, targetModule = null) {
        const moduleKey = targetModule || getActiveModuleKey();
        const data = collectModuleDataForAi(moduleKey);
        const meta = getModuleContextLabels(moduleKey);

        // Synchronize modal tabs
        document.querySelectorAll(".ai-modal-tab").forEach(tab => {
            const isMatch = tab.dataset.tab === moduleKey;
            tab.classList.toggle("active", isMatch);
            tab.setAttribute("aria-selected", isMatch ? "true" : "false");
        });"""

assert normalize(target_active_key) in js_norm, "target_active_key not found"
js_norm = js_norm.replace(normalize(target_active_key), normalize(replacement_active_key), 1)

# 3. Add tab click listeners in initAiModalListeners
target_listeners = """        if (btnReanalyzeAi) {
            btnReanalyzeAi.addEventListener("click", () => executeAiDecisionAnalysis(btnReanalyzeAi));
        }"""

replacement_listeners = """        if (btnReanalyzeAi) {
            btnReanalyzeAi.addEventListener("click", () => {
                const activeTab = document.querySelector(".ai-modal-tab.active");
                const mod = activeTab?.dataset.tab || getActiveModuleKey();
                executeAiDecisionAnalysis(btnReanalyzeAi, mod);
            });
        }

        // Inner modal tabs switching
        document.querySelectorAll(".ai-modal-tab").forEach(tab => {
            tab.addEventListener("click", () => {
                const mod = tab.dataset.tab;
                if (mod) executeAiDecisionAnalysis(btnReanalyzeAi, mod);
            });
        });"""

assert normalize(target_listeners) in js_norm, "target_listeners not found"
js_norm = js_norm.replace(normalize(target_listeners), normalize(replacement_listeners), 1)

with open("static/js/calculators.js", "w", encoding="utf-8") as f:
    f.write(js_norm)

print("Updated calculators.js with full 'all' modules support and modal tab switching successfully!")

