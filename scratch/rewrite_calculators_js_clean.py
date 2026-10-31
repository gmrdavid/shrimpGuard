# -*- coding: utf-8 -*-
"""
Reconstruct static/js/calculators.js cleanly without any duplicates.
"""

tool2_code = '''
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
                srBadgeEl.textContent = "Optimal (\u226580%)";
                srBadgeEl.className = "wqi-metric-badge badge-optimal";
            } else if (sr >= 65.0) {
                srBadgeEl.textContent = "Acceptable (65\u201379%)";
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
        if (weightMultEl) weightMultEl.textContent = `${Math.round(weightMult).toLocaleString()}\u00D7`;

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
            formula: "SR = (LHC / IS) \u00D7 100",
            variables: [
                "<strong>LHC</strong> = Live harvest count (shrimp)",
                "<strong>IS</strong> = Initial stocking (shrimp)",
                "<strong>SR</strong> = Survival rate (%)"
            ],
            getSubstitution: (s) => `SR = (${s.lhcCount.toLocaleString()} shrimp / ${s.isCount.toLocaleString()} shrimp) \u00D7 100 = <strong>${s.sr.toFixed(2)}%</strong><br><small style="color:#64748b;">Mortality: ${s.mortalityCount.toLocaleString()} shrimp (${s.mortalityPct.toFixed(2)}%)</small>`,
            getEval: (s) => ({
                badge: s.sr >= 80 ? "Optimal (\u226580%)" : (s.sr >= 65 ? "Acceptable (65\u201379%)" : "Suboptimal (<65%)"),
                badgeClass: s.sr >= 80 ? "badge-optimal" : (s.sr >= 65 ? "badge-warning" : "badge-critical"),
                text: s.sr >= 80
                    ? `Optimal survival rate (${s.sr.toFixed(2)}%) exceeding typical commercial Penaeus vannamei benchmarks (\u226580%). Mortality was contained to ${s.mortalityCount.toLocaleString()} shrimp (${s.mortalityPct.toFixed(2)}%), indicating stable water quality, clean bottom soil, and strong biosecurity.`
                    : (s.sr >= 65
                        ? `Moderate survival rate (${s.sr.toFixed(2)}%). Total cumulative loss is ${s.mortalityCount.toLocaleString()} shrimp (${s.mortalityPct.toFixed(2)}%). Check for dissolved oxygen drops during night hours (22:00\u201306:00) and monitor benthic sediment accumulation.`
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
                text: `Harvested average body weight of ${s.fabw.toFixed(2)} g corresponds to Size ${s.countPerKg.toFixed(0)} count (${s.countPerKg.toFixed(1)} pieces per kilogram). In high-density vannamei farming, 18\u201325 g represents the premium commercial export grade.`,
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
                badge: s.adwg >= 0.22 ? "Fast Growth (\u22650.22 g/d)" : (s.adwg >= 0.18 ? "Optimal (0.18\u20130.22 g/d)" : "Slow (<0.18 g/d)"),
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
            formula: "SGR = [(ln FABW - ln IBW) / DOC] \u00D7 100",
            variables: [
                "<strong>FABW</strong> = Final average body weight (g)",
                "<strong>IBW</strong> = Initial body weight at stocking (g)",
                "<strong>DOC</strong> = Days of culture (days)",
                "<strong>ln</strong> = Natural logarithm",
                "<strong>SGR</strong> = Specific growth rate (%/day)"
            ],
            getSubstitution: (s) => `SGR = [(ln ${s.fabw.toFixed(2)} - ln ${s.ibwVal.toFixed(3)}) / ${s.docDays}] \u00D7 100 = <strong>${s.sgr.toFixed(3)}% / day</strong><br><small style="color:#64748b;">Weight Multiplication: ${Math.round(s.weightMult).toLocaleString()}\u00D7 stocking weight</small>`,
            getEval: (s) => ({
                badge: "Logarithmic Growth Index",
                badgeClass: "badge-optimal",
                text: `Specific growth rate evaluates relative percentage growth compounding each day. Over the ${s.docDays}-day cycle, individual shrimp increased in weight by ${Math.round(s.weightMult).toLocaleString()} times their stocking mass.`,
                tip: "<strong>Pond Action Tip:</strong> SGR is steepest during nursery/early juvenile stages (DOC 1\u201330) and gradually flattens during late growout as metabolic maintenance increases."
            })
        },
        "5": {
            title: "Equation 5: Initial Biomass (IB)",
            subtitle: "Total biological mass introduced at pond stocking",
            formula: "IB = IS \u00D7 IBW",
            variables: [
                "<strong>IS</strong> = Initial stocking count (shrimp)",
                "<strong>IBW</strong> = Initial body weight per shrimp (g)",
                "<strong>IB</strong> = Initial total biomass (g / kg)"
            ],
            getSubstitution: (s) => `IB = ${s.isCount.toLocaleString()} shrimp \u00D7 ${s.ibwVal.toFixed(3)} g = ${Math.round(s.ibGrams).toLocaleString()} g = <strong>${s.ibKg.toFixed(2)} kg</strong>`,
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
            formula: "FB = LHC \u00D7 FABW",
            variables: [
                "<strong>LHC</strong> = Live harvest count (shrimp)",
                "<strong>FABW</strong> = Final average body weight (g)",
                "<strong>FB</strong> = Final total biomass (g / kg)"
            ],
            getSubstitution: (s) => `FB = ${s.lhcCount.toLocaleString()} shrimp \u00D7 ${s.fabw.toFixed(2)} g = ${Math.round(s.fbGrams).toLocaleString()} g = <strong>${s.fbKg.toFixed(2)} kg</strong><br><small style="color:#64748b;">Net Live Yield Gain: ${s.netGainKg.toFixed(2)} kg</small>`,
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
                badge: s.fcr < 1.20 ? "Exceptional (<1.20)" : (s.fcr <= 1.50 ? "Optimal (1.20\u20131.50)" : (s.fcr <= 1.80 ? "Acceptable (1.51\u20131.80)" : "Suboptimal (>1.80)")),
                badgeClass: s.fcr <= 1.50 ? "badge-optimal" : (s.fcr <= 1.80 ? "badge-warning" : "badge-critical"),
                text: s.fcr <= 1.50
                    ? `Excellent FCR of ${s.fcr.toFixed(3)}. Standard commercial targets for Penaeus vannamei range between 1.20 and 1.50. High feed efficiency (${s.feedEfficiency.toFixed(2)}%) indicates minimal feed wastage, healthy gut microbiota, and low ammonia generation.`
                    : (s.fcr <= 1.80
                        ? `Acceptable FCR of ${s.fcr.toFixed(3)}. Feed utilization was moderate (${s.feedEfficiency.toFixed(2)}%). Regularly monitor feeding check trays to ensure feed is fully consumed within 2 hours.`
                        : `Suboptimal FCR of ${s.fcr.toFixed(3)} (>1.80). Indicates feed wastage, overfeeding, or poor water quality reducing appetite. Excess unconsumed pellets decay on pond bottom, driving up toxic unionized ammonia.`),
                tip: "<strong>Pond Action Tip:</strong> Check feed trays 1.5\u20132 hours after every meal. If >10% remains uneaten, immediately reduce the next feeding by 20%."
            })
        },
        "8": {
            title: "Equation 8: Fulton's Condition Factor (K)",
            subtitle: "Morphometric body condition, tail meat fullness, and muscle density",
            formula: "K = (FABW / TL\u00B3) \u00D7 100",
            variables: [
                "<strong>FABW</strong> = Final average body weight (g)",
                "<strong>TL</strong> = Total length from rostrum tip to telson tip (cm)",
                "<strong>K</strong> = Fulton's body condition factor"
            ],
            getSubstitution: (s) => `K = (${s.fabw.toFixed(2)} g / ${s.tlCm.toFixed(1)}\u00B3 cm\u00B3) \u00D7 100 = (${s.fabw.toFixed(2)} / ${Math.pow(s.tlCm, 3).toFixed(3)}) \u00D7 100 = <strong>${s.kFactor.toFixed(4)}</strong>`,
            getEval: (s) => ({
                badge: (s.kFactor >= 0.80 && s.kFactor <= 1.15) ? "Optimal Robust (0.80\u20131.15)" : (s.kFactor < 0.80 ? "Slender / Lean (<0.80)" : "Heavy Plump (>1.15)"),
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
'''

boot_code = '''
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
'''

def clean_reconstruct():
    with open('static/js/calculators.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the end of btnSyncLive listener in the first block
    # We look for "btnSyncLive.disabled = false;"
    marker_search = 'btnSyncLive.disabled = false;'
    idx_first_sync = content.find(marker_search)
    if idx_first_sync == -1:
        print("Could not find btnSyncLive.disabled = false;")
        return False

    # Find the closing brace of that listener
    idx_close = content.find('});\n    }', idx_first_sync)
    if idx_close == -1:
        idx_close = content.find('});\r\n    }', idx_first_sync)

    if idx_close == -1:
        print("Could not find closing brace of btnSyncLive listener.")
        return False

    idx_cut = idx_close + len('});\n    }')

    # Cut content up to end of btnSyncLive
    top_clean = content[:idx_cut].strip()

    # Assemble new file
    final_content = top_clean + '\n\n' + tool2_code.strip() + '\n\n' + boot_code.strip() + '\n'

    with open('static/js/calculators.js', 'w', encoding='utf-8') as f:
        f.write(final_content)

    print("Cleanly reconstructed static/js/calculators.js!")
    return True

if __name__ == '__main__':
    clean_reconstruct()

