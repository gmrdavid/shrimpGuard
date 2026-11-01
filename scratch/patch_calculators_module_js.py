with open("static/js/calculators.js", "r", encoding="utf-8") as f:
    js = f.read()

def normalize(text):
    return text.replace("\r\n", "\n")

js_norm = normalize(js)

module_switcher_code = """
    // -------------------------------------------------------------
    // Computation Focus & Module Chooser Management
    // -------------------------------------------------------------
    const MODULE_DEFINITIONS = {
        feeding: {
            id: "tools-feeding-section",
            name: "Feeding Management",
            icon: "#icon-shrimp"
        },
        growth: {
            id: "tools-growth-section",
            name: "Growth Performance",
            icon: "#icon-chart"
        },
        remediation: {
            id: "tools-remediation-section",
            name: "Water Remediation",
            icon: "#icon-droplet"
        },
        ammonia: {
            id: "tools-ammonia-section",
            name: "Unionized Ammonia Toxicity",
            icon: "#icon-droplet"
        },
        co2: {
            id: "tools-co2-section",
            name: "Carbon Dioxide",
            icon: "#icon-activity"
        },
        all: {
            id: null,
            name: "Show All Modules",
            icon: "#icon-calculator"
        }
    };

    const btnChooseComputation = document.getElementById("btn-choose-computation");
    const dropdownMenu = document.getElementById("tools-module-dropdown-menu");
    const activeLabel = document.getElementById("active-computation-label");
    const dropdownItems = document.querySelectorAll(".module-dropdown-item");
    const modulePills = document.querySelectorAll(".module-pill");
    const moduleSections = document.querySelectorAll("[data-calc-module]");

    function setActiveComputationModule(moduleKey, savePreference = true) {
        if (!MODULE_DEFINITIONS[moduleKey]) {
            moduleKey = "feeding";
        }

        const currentDef = MODULE_DEFINITIONS[moduleKey];

        // 1. Update button text label
        if (activeLabel) {
            activeLabel.textContent = currentDef.name;
        }

        // 2. Synchronize Dropdown Items
        dropdownItems.forEach((item) => {
            const isMatch = item.dataset.module === moduleKey;
            item.classList.toggle("active", isMatch);
            item.setAttribute("aria-selected", isMatch ? "true" : "false");
        });

        // 3. Synchronize Pill Tabs
        modulePills.forEach((pill) => {
            const isMatch = pill.dataset.module === moduleKey;
            pill.classList.toggle("active", isMatch);
            pill.setAttribute("aria-selected", isMatch ? "true" : "false");
        });

        // 4. Filter and show ONLY the selected module (or all if "all" is chosen)
        moduleSections.forEach((section) => {
            const secModule = section.dataset.calcModule;
            if (moduleKey === "all") {
                section.hidden = false;
                section.style.display = "";
                section.classList.remove("calc-module-active");
            } else {
                if (secModule === moduleKey) {
                    section.hidden = false;
                    section.style.display = "";
                    section.classList.remove("calc-module-active");
                    void section.offsetWidth; // force reflow for smooth animation
                    section.classList.add("calc-module-active");
                } else {
                    section.hidden = true;
                    section.style.display = "none";
                    section.classList.remove("calc-module-active");
                }
            }
        });

        // 5. Close Dropdown Menu
        if (dropdownMenu && !dropdownMenu.hidden) {
            dropdownMenu.hidden = true;
            if (btnChooseComputation) {
                btnChooseComputation.setAttribute("aria-expanded", "false");
            }
        }

        // 6. Save preference to localStorage
        if (savePreference) {
            try {
                localStorage.setItem("shrimpguard_active_calc_module", moduleKey);
            } catch (err) {
                console.warn("Could not save active calc module to localStorage", err);
            }
        }
    }

    function initComputationModuleSelector() {
        if (!btnChooseComputation && dropdownItems.length === 0 && modulePills.length === 0) {
            return;
        }

        // Dropdown toggle button
        if (btnChooseComputation && dropdownMenu) {
            btnChooseComputation.addEventListener("click", (e) => {
                e.stopPropagation();
                const isHidden = dropdownMenu.hidden;
                dropdownMenu.hidden = !isHidden;
                btnChooseComputation.setAttribute("aria-expanded", isHidden ? "true" : "false");
            });
        }

        // Dropdown items click
        dropdownItems.forEach((item) => {
            item.addEventListener("click", (e) => {
                e.stopPropagation();
                const mod = item.dataset.module;
                if (mod) setActiveComputationModule(mod, true);
            });
        });

        // Pill buttons click
        modulePills.forEach((pill) => {
            pill.addEventListener("click", (e) => {
                e.stopPropagation();
                const mod = pill.dataset.module;
                if (mod) setActiveComputationModule(mod, true);
            });
        });

        // Click outside closes dropdown
        document.addEventListener("click", (e) => {
            if (dropdownMenu && !dropdownMenu.hidden) {
                if (!dropdownMenu.contains(e.target) && (!btnChooseComputation || !btnChooseComputation.contains(e.target))) {
                    dropdownMenu.hidden = true;
                    if (btnChooseComputation) {
                        btnChooseComputation.setAttribute("aria-expanded", "false");
                    }
                }
            }
        });

        // Escape closes dropdown
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && dropdownMenu && !dropdownMenu.hidden) {
                dropdownMenu.hidden = true;
                if (btnChooseComputation) {
                    btnChooseComputation.setAttribute("aria-expanded", "false");
                }
            }
        });

        // Determine initial module to display
        let initialModule = "feeding";
        const hashModule = window.location.hash.replace("#", "").toLowerCase();
        if (MODULE_DEFINITIONS[hashModule]) {
            initialModule = hashModule;
        } else {
            try {
                const storedModule = localStorage.getItem("shrimpguard_active_calc_module");
                if (storedModule && MODULE_DEFINITIONS[storedModule]) {
                    initialModule = storedModule;
                }
            } catch (err) {}
        }

        setActiveComputationModule(initialModule, false);
    }
"""

target_boot = """        calculateAmmoniaTool();
        calculateMasterGrowth();
    }"""

replacement_boot = """        calculateAmmoniaTool();
        calculateCo2Tool();
        calculateMasterGrowth();

        initComputationModuleSelector();
    }"""

assert normalize(target_boot) in js_norm, "target_boot not found in calculators.js"

# Insert module_switcher_code right before async function boot()
target_before_boot = """    async function boot() {"""
replacement_before_boot = f"""{module_switcher_code}

    async function boot() {{"""

assert normalize(target_before_boot) in js_norm, "target_before_boot not found in calculators.js"

js_norm = js_norm.replace(normalize(target_before_boot), normalize(replacement_before_boot), 1)
js_norm = js_norm.replace(normalize(target_boot), normalize(replacement_boot), 1)

with open("static/js/calculators.js", "w", encoding="utf-8") as f:
    f.write(js_norm)

print("Updated static/js/calculators.js with module selector logic successfully!")

