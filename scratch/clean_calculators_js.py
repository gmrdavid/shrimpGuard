with open("static/js/calculators.js", "r", encoding="utf-8") as f:
    js = f.read()

# Replace the two functions with nothing or a comment
target_funcs = """    function updateGrowthChartLegend() {
        const legendEl = document.getElementById("growth-chart-legend");
        if (!legendEl) return;
        const activeKeys = Array.from(selectedGrowthMetrics);
        legendEl.innerHTML = activeKeys.map(key => {
            const conf = GROWTH_METRICS_CONFIG[key];
            return `
                <span>
                    <i style="background:${conf.color};"></i>
                    ${conf.eq}: ${conf.label} ${conf.unit ? '(' + conf.unit + ')' : ''}
                </span>
            `;
        }).join("");
    }

    function updateGrowthMiniStats() {
        const cur = collectCurrentCalculations();
        const setEl = (id, text) => {
            const el = document.getElementById(id);
            if (el) el.textContent = text;
        };

        setEl("mini-stat-sr", `${cur.eq1_sr_pct.toFixed(2)} %`);
        setEl("mini-stat-fabw", `${cur.eq2_fabw_g.toFixed(2)} g`);
        setEl("mini-sub-fabw", `${cur.eq2_count_per_kg.toFixed(1)}/kg`);
        setEl("mini-stat-adwg", `${cur.eq3_adwg_g_day.toFixed(3)} g/d`);
        setEl("mini-stat-sgr", `${cur.eq4_sgr_pct_day.toFixed(2)} %/d`);
        setEl("mini-stat-fb", `${cur.eq6_fb_kg.toLocaleString(undefined, {maximumFractionDigits: 1})} kg`);
        setEl("mini-stat-fcr", cur.eq7_fcr.toFixed(2));
        setEl("mini-stat-k", cur.eq8_fulton_k.toFixed(4));

        const badgeSr = document.getElementById("mini-badge-sr");
        if (badgeSr) {
            const evalSr = GROWTH_METRICS_CONFIG.sr.evaluator(cur.eq1_sr_pct);
            badgeSr.textContent = evalSr.status;
            badgeSr.className = `mini-badge ${evalSr.badgeClass}`;
        }
        const badgeAdwg = document.getElementById("mini-badge-adwg");
        if (badgeAdwg) {
            const evalAdwg = GROWTH_METRICS_CONFIG.adwg.evaluator(cur.eq3_adwg_g_day);
            badgeAdwg.textContent = evalAdwg.status;
            badgeAdwg.className = `mini-badge ${evalAdwg.badgeClass}`;
        }
        const badgeFcr = document.getElementById("mini-badge-fcr");
        if (badgeFcr) {
            const evalFcr = GROWTH_METRICS_CONFIG.fcr.evaluator(cur.eq7_fcr);
            badgeFcr.textContent = evalFcr.status;
            badgeFcr.className = `mini-badge ${evalFcr.badgeClass}`;
        }
        const badgeK = document.getElementById("mini-badge-k");
        if (badgeK) {
            const evalK = GROWTH_METRICS_CONFIG.k.evaluator(cur.eq8_fulton_k);
            badgeK.textContent = evalK.status;
            badgeK.className = `mini-badge ${evalK.badgeClass}`;
        }
    }"""

if target_funcs in js:
    js = js.replace(target_funcs, "")
    print("SUCCESS: Removed updateGrowthChartLegend and updateGrowthMiniStats functions.")
else:
    norm_js = js.replace("\r\n", "\n")
    norm_tf = target_funcs.replace("\r\n", "\n")
    if norm_tf in norm_js:
        js = norm_js.replace(norm_tf, "")
        print("SUCCESS: Normalized replace of functions.")
    else:
        print("WARNING: target_funcs not found!")

# Remove invocations
js = js.replace("        updateGrowthMiniStats();\n", "")
js = js.replace("        updateGrowthChartLegend();\n", "")
js = js.replace("            updateGrowthChartLegend();\n", "")
js = js.replace("        updateGrowthMiniStats();\r\n", "")
js = js.replace("        updateGrowthChartLegend();\r\n", "")
js = js.replace("            updateGrowthChartLegend();\r\n", "")

with open("static/js/calculators.js", "w", encoding="utf-8", newline="\r\n") as f:
    f.write(js)

print("Updated static/js/calculators.js successfully.")

