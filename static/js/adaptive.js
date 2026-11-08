/**
 * ShrimpGuard Adaptive Web Engine (AWS)
 * Automatically adjusts structure, content, and presentation based on
 * user behavior, interaction history, device context, and pond telemetry.
 */
(() => {
    "use strict";

    const STORAGE_KEY = "shrimpguard_adaptive_model";
    const SYNC_INTERVAL_MS = 45000;

    const PERSONA_CONFIGS = {
        field_inspector: {
            id: "field_inspector",
            title: "Field Inspector",
            badge: "Field Inspector",
            description: "Tailored for rapid pond-side telemetry checks, alarm monitoring, and touch operation.",
            icon: "icon-monitor",
            density: "comfort",
            shortcuts: [
                { label: "Live Telemetry", url: "/monitoring", icon: "icon-monitor", badge: "Live" },
                { label: "Pond Dashboard", url: "/dashboard", icon: "icon-dashboard" },
                { label: "Active Alerts", url: "/alerts", icon: "icon-alert" },
                { label: "Sensor Health", url: "/devices", icon: "icon-cpu" }
            ]
        },
        farm_planner: {
            id: "farm_planner",
            title: "Aquaculture Farm Planner",
            badge: "Farm Planner",
            description: "Tailored for daily feed calculations, biomass projection, chemical liming, and molasses dosing.",
            icon: "icon-calculator",
            density: "comfort",
            shortcuts: [
                { label: "Aquaculture Calculators", url: "/calculators", icon: "icon-calculator", badge: "Tools" },
                { label: "Feed & Biomass", url: "/calculators#feeding-calculator-panel", icon: "icon-calculator" },
                { label: "Real-time Monitoring", url: "/monitoring", icon: "icon-monitor" },
                { label: "Pond Dashboard", url: "/dashboard", icon: "icon-dashboard" }
            ]
        },
        data_analyst: {
            id: "data_analyst",
            title: "Pond Data Analyst",
            badge: "Data Analyst",
            description: "Tailored for high-density multi-parameter trend audits, historical reporting, and CSV data exports.",
            icon: "icon-chart",
            density: "compact",
            shortcuts: [
                { label: "Analytics & Trends", url: "/analytics", icon: "icon-chart", badge: "Reports" },
                { label: "Historical Audits", url: "/historical", icon: "icon-history" },
                { label: "Live Monitoring", url: "/monitoring", icon: "icon-monitor" },
                { label: "Calculators", url: "/calculators", icon: "icon-calculator" }
            ]
        },
        balanced_operator: {
            id: "balanced_operator",
            title: "Balanced Farm Operator",
            badge: "Standard Operator",
            description: "Balanced multi-module view across real-time telemetry, pond calculators, and alerts.",
            icon: "icon-dashboard",
            density: "auto",
            shortcuts: [
                { label: "Pond Dashboard", url: "/dashboard", icon: "icon-dashboard" },
                { label: "Real-time Monitoring", url: "/monitoring", icon: "icon-monitor" },
                { label: "Aquaculture Calculators", url: "/calculators", icon: "icon-calculator" },
                { label: "Alerts & Notifications", url: "/alerts", icon: "icon-alert" }
            ]
        }
    };

    // --- 1. MODEL STATE MANAGEMENT ---
    function getDefaultModel() {
        return {
            version: "2.0",
            interactions: {
                monitoring: 1,
                calculators: 0,
                analytics: 0,
                alerts: 0,
                devices: 0
            },
            dwell_times: {
                monitoring: 10,
                calculators: 0,
                analytics: 0,
                alerts: 0,
                devices: 0
            },
            total_actions: 1,
            preferences: {
                auto_adapt: true,
                density: "auto",         // 'auto', 'compact', 'comfort'
                sunlight_mode: "auto",   // 'auto', 'always', 'off'
                data_saver: "auto"       // 'auto', 'on', 'off'
            },
            last_sync: 0,
            first_seen: Date.now()
        };
    }

    function loadModel() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return getDefaultModel();
            const parsed = JSON.parse(raw);
            return Object.assign(getDefaultModel(), parsed);
        } catch {
            return getDefaultModel();
        }
    }

    function saveModel(model) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(model));
        } catch (e) {
            console.warn("Adaptive model could not be written to localStorage:", e);
        }
    }

    let model = loadModel();

    // --- 2. DEVICE & ENVIRONMENT DETECTION ---
    function detectDevice() {
        const isTouch = ("ontouchstart" in window) || (navigator.maxTouchPoints > 0) || window.matchMedia("(pointer: coarse)").matches;
        const width = window.innerWidth;
        const isMobile = width <= 768 || (isTouch && width <= 900);
        const isTablet = !isMobile && (width <= 1100 || (isTouch && width <= 1200));

        let connType = "4g";
        let isSaveData = false;
        const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        if (conn) {
            connType = conn.effectiveType || "4g";
            isSaveData = Boolean(conn.saveData);
        }

        return {
            is_touch: isTouch,
            is_mobile: isMobile,
            is_tablet: isTablet,
            is_desktop: !isMobile && !isTablet,
            type: isMobile ? "mobile_field" : (isTablet ? "tablet_hybrid" : "desktop_workstation"),
            width,
            connection: connType,
            save_data: isSaveData || ["slow-2g", "2g", "3g"].includes(connType)
        };
    }

    // --- 3. INTERACTION MODEL & BEHAVIORAL SCORING ---
    function classifyPersona(modelState) {
        const interactions = modelState.interactions || {};
        const dwell = modelState.dwell_times || {};

        const rawScores = {
            monitoring: (interactions.monitoring || 0) + (dwell.monitoring || 0) / 60.0,
            calculators: (interactions.calculators || 0) + (dwell.calculators || 0) / 60.0,
            analytics: (interactions.analytics || 0) + (dwell.analytics || 0) / 60.0,
            alerts: (interactions.alerts || 0) + (dwell.alerts || 0) / 60.0,
            devices: (interactions.devices || 0) + (dwell.devices || 0) / 60.0
        };

        const total = Object.values(rawScores).reduce((a, b) => a + b, 0);
        if (total < 4.0) {
            return {
                persona_id: "balanced_operator",
                percentages: { monitoring: 25, calculators: 25, analytics: 25, alerts: 25, devices: 0 }
            };
        }

        const percentages = {};
        for (const [k, v] of Object.entries(rawScores)) {
            percentages[k] = Math.round((v / total) * 100);
        }

        const sorted = Object.entries(percentages).sort((a, b) => b[1] - a[1]);
        const [topCat, topPct] = sorted[0];
        const secondPct = sorted[1] ? sorted[1][1] : 0;

        let persona_id = "balanced_operator";
        if (topPct >= 38 && (topPct - secondPct >= 8)) {
            if (topCat === "monitoring" || (topCat === "alerts" && (percentages.monitoring || 0) >= 20)) {
                persona_id = "field_inspector";
            } else if (topCat === "calculators") {
                persona_id = "farm_planner";
            } else if (topCat === "analytics") {
                persona_id = "data_analyst";
            }
        } else if ((percentages.monitoring || 0) + (percentages.alerts || 0) >= 55) {
            persona_id = "field_inspector";
        }

        return { persona_id, percentages };
    }

    function getProficiencyLevel(modelState) {
        const total = modelState.total_actions || 0;
        if (total < 15) return "novice";
        if (total < 60) return "proficient";
        return "advanced";
    }

    function identifyCurrentCategory() {
        const path = window.location.pathname.toLowerCase();
        if (path.includes("calculat")) return "calculators";
        if (path.includes("monitor")) return "monitoring";
        if (path.includes("alert")) return "alerts";
        if (path.includes("analytic") || path.includes("historic")) return "analytics";
        if (path.includes("device") || path.includes("hardware")) return "devices";
        if (path.includes("dashboard")) return "monitoring";
        return null;
    }

    // --- 4. TELEMETRY EVENT TRACKING ---
    function recordInteraction(category, action = "click", weight = 1) {
        if (!category) return;
        if (!model.interactions[category]) {
            model.interactions[category] = 0;
        }
        model.interactions[category] += weight;
        model.total_actions = (model.total_actions || 0) + weight;
        saveModel(model);
        debounceApplyAdaptations();
    }

    function trackDwellTime(category, seconds = 5) {
        if (!category) return;
        if (!model.dwell_times[category]) {
            model.dwell_times[category] = 0;
        }
        model.dwell_times[category] += seconds;
        saveModel(model);
    }

    // --- 5. AUTOMATIC PRESENTATION ADAPTATION ---
    function applyPresentationClasses() {
        const device = detectDevice();
        const { persona_id } = classifyPersona(model);
        const personaCfg = PERSONA_CONFIGS[persona_id] || PERSONA_CONFIGS.balanced_operator;
        const prefs = model.preferences || {};

        const root = document.documentElement;
        const body = document.body;
        if (!body) return;

        // Clean previous adaptive classes
        body.classList.remove(
            "adaptive-device-mobile", "adaptive-device-tablet", "adaptive-device-desktop",
            "adaptive-touch", "adaptive-compact", "adaptive-comfort",
            "adaptive-sunlight", "adaptive-data-saver",
            "adaptive-persona-field_inspector", "adaptive-persona-farm_planner",
            "adaptive-persona-data_analyst", "adaptive-persona-balanced_operator"
        );

        root.classList.add("adaptive-ready");

        // Device classes
        if (device.is_mobile) body.classList.add("adaptive-device-mobile");
        else if (device.is_tablet) body.classList.add("adaptive-device-tablet");
        else body.classList.add("adaptive-device-desktop");

        if (device.is_touch) body.classList.add("adaptive-touch");

        // Persona class
        body.classList.add(`adaptive-persona-${persona_id}`);

        // Density adaptation
        let density = prefs.density;
        if (density === "auto") {
            density = device.is_touch ? "comfort" : personaCfg.density;
        }
        if (density === "comfort") body.classList.add("adaptive-comfort");
        else if (density === "compact") body.classList.add("adaptive-compact");

        // Sunlight / Outdoor mode adaptation
        let sunlight = false;
        if (prefs.sunlight_mode === "always") {
            sunlight = true;
        } else if (prefs.sunlight_mode === "off") {
            sunlight = false;
        } else {
            // Auto: active if user enabled high contrast in OS or outdoor daytime touch
            const highContrastOS = window.matchMedia && window.matchMedia("(prefers-contrast: more)").matches;
            sunlight = Boolean(highContrastOS);
        }
        if (sunlight) body.classList.add("adaptive-sunlight");

        // Data-Saver adaptation
        let dataSaver = false;
        if (prefs.data_saver === "on") dataSaver = true;
        else if (prefs.data_saver === "off") dataSaver = false;
        else dataSaver = device.save_data;

        if (dataSaver) body.classList.add("adaptive-data-saver");
    }

    // --- 6. AUTOMATIC STRUCTURE ADAPTATION ---
    function renderAdaptiveShortcutsBar() {
        if (!model.preferences.auto_adapt) {
            const existing = document.getElementById("adaptive-shortcuts-bar");
            if (existing) existing.remove();
            return;
        }

        // Only render on authenticated dashboard/client app layouts
        const layoutHeader = document.querySelector(".dashboard-header, .settings-header, .history-header, .analytics-header, .tools-header");
        const mainEl = document.querySelector(".dashboard-layout > main, .settings-layout-page > main, main.main-content, main");
        if (!layoutHeader || !mainEl) return;

        let bar = document.getElementById("adaptive-shortcuts-bar");
        if (!bar) {
            bar = document.createElement("nav");
            bar.id = "adaptive-shortcuts-bar";
            bar.className = "adaptive-shortcuts-bar";
            bar.setAttribute("aria-label", "Adaptive smart shortcuts");
            layoutHeader.insertAdjacentElement("afterend", bar);
        }

        const { persona_id } = classifyPersona(model);
        const personaCfg = PERSONA_CONFIGS[persona_id] || PERSONA_CONFIGS.balanced_operator;
        const currentPath = window.location.pathname.toLowerCase();

        const shortcutsHtml = personaCfg.shortcuts
            .map(sc => {
                const isActive = currentPath.startsWith(sc.url.split("#")[0]);
                const badge = sc.badge ? `<span class="adaptive-chip-badge">${sc.badge}</span>` : "";
                return `
                    <a href="${sc.url}" class="adaptive-chip ${isActive ? "active" : ""}">
                        <svg class="ui-icon" aria-hidden="true"><use href="#${sc.icon}"></use></svg>
                        <span>${sc.label}</span>
                        ${badge}
                    </a>
                `;
            })
            .join("");

        const isSunlight = document.body.classList.contains("adaptive-sunlight");

        bar.innerHTML = `
            <div class="adaptive-shortcuts-left">
                <span class="adaptive-persona-pill" title="${personaCfg.description}">
                    <svg class="ui-icon" aria-hidden="true"><use href="#${personaCfg.icon}"></use></svg>
                    <span>${personaCfg.badge} Mode</span>
                </span>
                <div class="adaptive-chips-group">
                    ${shortcutsHtml}
                </div>
            </div>
            <div class="adaptive-shortcuts-right">
                <div id="adaptive-next-action-slot" class="adaptive-next-action-slot"></div>
                <button type="button" id="adaptive-toggle-sunlight" class="adaptive-sunlight-toggle ${isSunlight ? "active" : ""}" title="Toggle high-contrast outdoor field mode">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-sparkles"></use></svg>
                    <span>${isSunlight ? "Sunlight ON" : "Field View"}</span>
                </button>
            </div>
        `;

        const sunBtn = bar.querySelector("#adaptive-toggle-sunlight");
        if (sunBtn) {
            sunBtn.addEventListener("click", () => {
                toggleSunlightMode();
            });
        }

        updateNextActionBanner();
    }

    function renderMobileBottomNav() {
        const device = detectDevice();
        let bottomNav = document.getElementById("adaptive-bottom-nav");

        // Only on mobile touch devices
        if (!device.is_mobile || !model.preferences.auto_adapt) {
            if (bottomNav) bottomNav.remove();
            document.body.classList.remove("has-adaptive-bottom-nav");
            return;
        }

        // Only for logged-in app layouts (not login/signup/landing)
        const isClientPage = document.querySelector(".dashboard-layout, .settings-layout-page, .sidebar");
        if (!isClientPage) {
            if (bottomNav) bottomNav.remove();
            return;
        }

        if (!bottomNav) {
            bottomNav = document.createElement("nav");
            bottomNav.id = "adaptive-bottom-nav";
            bottomNav.className = "adaptive-bottom-nav";
            bottomNav.setAttribute("aria-label", "Thumb navigation");
            document.body.appendChild(bottomNav);
        }

        document.body.classList.add("has-adaptive-bottom-nav");

        const path = window.location.pathname.toLowerCase();
        const items = [
            { id: "home", label: "Dashboard", url: "/dashboard", icon: "icon-dashboard", active: path === "/dashboard" },
            { id: "monitor", label: "Monitoring", url: "/monitoring", icon: "icon-monitor", active: path.includes("/monitoring") },
            { id: "calc", label: "Calculators", url: "/calculators", icon: "icon-calculator", active: path.includes("/calculat") },
            { id: "alerts", label: "Alerts", url: "/alerts", icon: "icon-alert", active: path.includes("/alert") },
            { id: "settings", label: "Settings", url: "/settings", icon: "icon-settings", active: path.includes("/settings") }
        ];

        bottomNav.innerHTML = items.map(it => `
            <a href="${it.url}" class="adaptive-bottom-item ${it.active ? "active" : ""}" data-adaptive-nav="${it.id}">
                <svg class="ui-icon" aria-hidden="true"><use href="#${it.icon}"></use></svg>
                <span>${it.label}</span>
            </a>
        `).join("");
    }

    // --- 7. AUTOMATIC CONTENT ADAPTATION ---
    async function updateNextActionBanner() {
        const slot = document.getElementById("adaptive-next-action-slot");
        if (!slot) return;

        try {
            // Check latest sensor telemetry
            const res = await fetch("/api/readings/latest");
            if (!res.ok) return;
            const data = await res.json();
            if (!data) return;

            const temp = Number(data.temperature);
            const ph = Number(data.ph);
            const { persona_id } = classifyPersona(model);

            let actionObj = null;

            if (ph > 8.50) {
                actionObj = {
                    type: "warning",
                    text: `pH is elevated (${ph.toFixed(2)}) &rarr; Calculate Molasses Dosing`,
                    url: "/calculators#molasses-calculator-panel"
                };
            } else if (ph < 7.50) {
                actionObj = {
                    type: "warning",
                    text: `pH is low (${ph.toFixed(2)}) &rarr; Calculate Agricultural Lime Dose`,
                    url: "/calculators#lime-calculator-panel"
                };
            } else if (temp < 26.0 || temp > 32.0) {
                actionObj = {
                    type: "warning",
                    text: `Temp is ${temp.toFixed(2)} °C &rarr; Adjust Feeding Factor`,
                    url: "/calculators#feeding-calculator-panel"
                };
            } else {
                // Optimal recommendations personalized to persona
                if (persona_id === "farm_planner") {
                    actionObj = {
                        type: "optimal",
                        text: "Pond optimal &bull; Run Daily Biomass Feed Calc",
                        url: "/calculators#feeding-calculator-panel"
                    };
                } else if (persona_id === "data_analyst") {
                    actionObj = {
                        type: "optimal",
                        text: "Baseline stable &bull; Audit Today's 24h WQI Trends",
                        url: "/analytics"
                    };
                } else {
                    actionObj = {
                        type: "optimal",
                        text: "Pond parameters optimal &bull; Sensor Node 1 Active",
                        url: "/monitoring"
                    };
                }
            }

            if (actionObj) {
                slot.innerHTML = `
                    <a href="${actionObj.url}" class="adaptive-next-action-pill pill-${actionObj.type}">
                        <span class="adaptive-pulse-dot"></span>
                        <span>${actionObj.text}</span>
                    </a>
                `;
            }
        } catch {
            // Silently ignore network fetch errors for suggestions
        }
    }

    function adaptMetricCards() {
        // Prioritize metric cards on dashboard and monitoring if abnormal
        const tempCard = document.getElementById("temperature")?.closest(".metric-card, .metric-box, .sensor-metric-card");
        const phCard = document.getElementById("ph")?.closest(".metric-card, .metric-box, .sensor-metric-card");
        if (!tempCard && !phCard) return;

        const { persona_id } = classifyPersona(model);
        if (persona_id === "farm_planner" && phCard) {
            phCard.style.order = "-1";
        } else if (tempCard) {
            tempCard.style.order = "-1";
        }
    }

    function adaptLandingPage() {
        if (!window.location.pathname.endsWith("/") && !window.location.pathname.endsWith("landing") && window.location.pathname !== "") return;
        const heroActions = document.querySelector(".landing-hero-actions");
        if (!heroActions) return;

        // If returning user has previous sessions
        if (model.total_actions > 5) {
            const hasResumeBtn = document.getElementById("adaptive-resume-btn");
            if (!hasResumeBtn) {
                const resumeLink = document.createElement("a");
                resumeLink.id = "adaptive-resume-btn";
                resumeLink.href = "/dashboard";
                resumeLink.className = "landing-btn landing-btn-primary landing-btn-resume";
                resumeLink.innerHTML = `
                    <svg class="ui-icon" aria-hidden="true" style="width:18px;height:18px;margin-right:6px;"><use href="#icon-sparkles"></use></svg>
                    <span>Resume Pond Dashboard &rarr;</span>
                `;
                heroActions.insertBefore(resumeLink, heroActions.firstChild);
            }
        }
    }

    function adaptGuidanceTooltips() {
        const proficiency = getProficiencyLevel(model);
        const root = document.documentElement;

        if (proficiency === "novice") {
            root.classList.add("adaptive-guidance-active");
        } else {
            root.classList.remove("adaptive-guidance-active");
        }
    }

    // --- 8. SYNC MODEL TO BACKEND ---
    async function syncModelToBackend() {
        const device = detectDevice();
        try {
            const payload = {
                interactions: model.interactions,
                dwell: model.dwell_times,
                device: {
                    type: device.type,
                    is_touch: device.is_touch,
                    connection: device.connection,
                    save_data: device.save_data
                },
                preferences: model.preferences
            };

            const response = await fetch("/api/adaptive/sync", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                model.last_sync = Date.now();
                saveModel(model);
            }
        } catch (err) {
            // Offline or unauthenticated; model remains locally cached
        }
    }

    // --- 9. PUBLIC METHODS & ADAPTIVE SETTINGS ---
    function toggleSunlightMode() {
        const isCurrent = document.body.classList.contains("adaptive-sunlight");
        const nextState = !isCurrent;
        model.preferences.sunlight_mode = nextState ? "always" : "off";
        saveModel(model);
        applyPresentationClasses();
        renderAdaptiveShortcutsBar();
    }

    function updatePreferences(newPrefs) {
        model.preferences = Object.assign(model.preferences || {}, newPrefs);
        saveModel(model);
        applyAdaptations();
        syncModelToBackend();
    }

    function resetModel() {
        model = getDefaultModel();
        saveModel(model);
        applyAdaptations();
        fetch("/api/adaptive/reset", { method: "POST" }).catch(() => {});
    }

    function applyAdaptations() {
        applyPresentationClasses();
        renderAdaptiveShortcutsBar();
        renderMobileBottomNav();
        adaptMetricCards();
        adaptLandingPage();
        adaptGuidanceTooltips();
    }

    let debounceTimer = null;
    function debounceApplyAdaptations() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(applyAdaptations, 100);
    }

    // --- 10. EVENT LISTENERS SETUP ---
    function setupInteractionListeners() {
        // Track current page visit
        const currentCat = identifyCurrentCategory();
        if (currentCat) {
            recordInteraction(currentCat, "page_view", 1);
            setInterval(() => {
                if (document.visibilityState === "visible") {
                    trackDwellTime(currentCat, 5);
                }
            }, 5000);
        }

        // Global delegated click tracking
        document.addEventListener("click", (evt) => {
            const target = evt.target.closest("a, button, input[type='submit'], .calc-btn, .metric-card");
            if (!target) return;

            // Link click
            if (target.tagName === "A" && target.href) {
                const url = target.getAttribute("href") || "";
                if (url.includes("calculat")) recordInteraction("calculators", "click_nav", 2);
                else if (url.includes("monitor")) recordInteraction("monitoring", "click_nav", 2);
                else if (url.includes("analytic") || url.includes("historic")) recordInteraction("analytics", "click_nav", 2);
                else if (url.includes("alert")) recordInteraction("alerts", "click_nav", 2);
            }

            // Calculation submit button
            if (target.classList.contains("sim-btn-submit") || target.closest("#quality-form")) {
                recordInteraction("monitoring", "telemetry_test", 3);
            }
            if (target.closest(".calculator-card, .calc-panel, [id*='calc']")) {
                recordInteraction("calculators", "calc_action", 3);
            }
            if (target.closest(".analytics-controls, .history-filter, [id*='export']")) {
                recordInteraction("analytics", "analytics_action", 3);
            }
        }, { passive: true });

        // Responsive orientation/resize handler
        window.addEventListener("resize", () => {
            debounceApplyAdaptations();
        }, { passive: true });

        // Listen for sensor telemetry dispatch
        window.addEventListener("shrimpguard:telemetry-update", () => {
            updateNextActionBanner();
            adaptMetricCards();
        });

        // Periodic sync
        setInterval(() => {
            syncModelToBackend();
        }, SYNC_INTERVAL_MS);

        window.addEventListener("pagehide", () => {
            syncModelToBackend();
        });
    }

    // --- BOOTSTRAP ---
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => {
            setupInteractionListeners();
            applyAdaptations();
        });
    } else {
        setupInteractionListeners();
        applyAdaptations();
    }

    // Expose global API
    window.ShrimpGuardAdaptive = {
        getModel: () => model,
        getPersona: () => classifyPersona(model),
        getDevice: detectDevice,
        track: recordInteraction,
        updatePreferences,
        resetModel,
        toggleSunlightMode,
        applyAdaptations
    };
})();
