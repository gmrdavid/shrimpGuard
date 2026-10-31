# -*- coding: utf-8 -*-
"""
Script to insert Shrimp Growth Calculators logic into static/js/calculators.js.
"""

growth_js = '''
    // -------------------------------------------------------------
    // TOOL 2: Shrimp Growth & Zootechnical Performance (Eqs. 1–8)
    // -------------------------------------------------------------

    // Tab Switching for Growth Calculators
    const growthTabButtons = document.querySelectorAll(".growth-tabs-bar .growth-tab-item");
    const growthTabPanes = document.querySelectorAll(".growth-section .growth-tab-pane");

    growthTabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetPaneId = btn.getAttribute("aria-controls");
            growthTabButtons.forEach(b => {
                b.classList.remove("active");
                b.setAttribute("aria-selected", "false");
            });
            growthTabPanes.forEach(p => {
                p.classList.remove("active");
                p.hidden = true;
            });

            btn.classList.add("active");
            btn.setAttribute("aria-selected", "true");
            const activePane = document.getElementById(targetPaneId);
            if (activePane) {
                activePane.classList.add("active");
                activePane.hidden = false;
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
        if (weightMultEl) weightMultEl.textContent = `${Math.round(weightMult).toLocaleString()}\u00D7`;
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
                ratingEl.textContent = "Optimal survival rate exceeding typical commercial benchmark (\u226580%). Favorable pond conditions and healthy stock transition.";
            } else if (sr >= 65.0) {
                badgeEl.textContent = "Acceptable";
                badgeEl.className = "wqi-metric-badge badge-warning";
                ratingEl.textContent = "Moderate survival rate (65%\u201379%). Review benthic sediment conditions, feeding tray consumption, and stocking density.";
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
        if (sgrMultEl) sgrMultEl.textContent = `${Math.round(mult).toLocaleString()}\u00D7`;
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
                ratingEl.textContent = "Standard target commercial FCR (1.20\u20131.50) for Penaeus vannamei culture.";
            } else if (fcr <= 1.80) {
                badgeEl.textContent = "Acceptable (1.51–1.80)";
                badgeEl.className = "wqi-metric-badge badge-warning";
                ratingEl.textContent = "Moderate feed efficiency (1.51\u20131.80). Regularly inspect feed check trays to prevent overfeeding and ammonia spikes.";
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
    const growthPresetButtons = document.querySelectorAll(".btn-preset-growth");
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

'''

def update_calculators_js():
    with open('static/js/calculators.js', 'r', encoding='utf-8') as f:
        content = f.read()

    marker = '// TOOL 2: Shrimp Growth & Zootechnical Performance'
    if marker in content:
        print("Growth code already exists in calculators.js.")
        return

    # Find where btnSyncLive event listener ends or before boot()
    target_boot = '    // Initial Load & Boot\n    // -------------------------------------------------------------\n    async function boot() {'
    if target_boot not in content:
        # try CRLF
        target_boot = '    // Initial Load & Boot\r\n    // -------------------------------------------------------------\r\n    async function boot() {'

    if target_boot not in content:
        print("Could not find boot function marker.")
        return

    # Insert growth_js before boot
    updated = content.replace(target_boot, growth_js + '\n' + target_boot)

    # In boot(), add calculateMasterGrowth();
    boot_calc_marker = 'calculateAmmoniaTool();'
    if boot_calc_marker in updated:
        updated = updated.replace(boot_calc_marker, 'calculateAmmoniaTool();\n        calculateMasterGrowth();')

    with open('static/js/calculators.js', 'w', encoding='utf-8') as f:
        f.write(updated)

    print("Successfully updated static/js/calculators.js!")

if __name__ == '__main__':
    update_calculators_js()

