import re

# 1. Update templates/calculators.html
with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

# Remove the legend container
old_legend = """            <!-- Legend (Uniform with water quality trend) -->
            <div id="growth-chart-legend" class="chart-legend monitoring-chart-legend growth-chart-legend" aria-label="Growth performance chart legend">
                <!-- Dynamically rendered / populated -->
            </div>"""

if old_legend in html:
    html = html.replace(old_legend, "")
    print("SUCCESS: Removed growth-chart-legend container from calculators.html")
else:
    # Try regex if whitespace differs
    pattern = re.compile(r'\s*<!-- Legend.*?-->\s*<div id="growth-chart-legend".*?<\/div>', re.DOTALL)
    html, count = pattern.subn("", html)
    print(f"Regex removed legend container: {count}")

# Replace table cells with badge spans for Warning and Critical
old_table_rows = """                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-thermometer"></use></svg>
                                        <strong>Water Temperature</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">28.0 ≤ x ≤ 32.0 °C</span></td>
                                <td>20.0 ≤ x < 28.0 or 32.0 < x ≤ 35.0 °C</td>
                                <td>x < 20.0 or x > 35.0 °C</td>
                                <td>If high: increase water depth (&gt;1.2m), run paddlewheels, reduce feed by 20–50%. If low: cease feeding, maintain high bottom DO.</td>
                            </tr>
                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                                        <strong>pH Level</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">7.5 ≤ x ≤ 8.5 pH</span></td>
                                <td>6.5 ≤ x < 7.5 or 8.5 < x ≤ 9.0 pH</td>
                                <td>x < 6.5 or x > 9.0 pH</td>
                                <td>If low (&lt;7.5): apply Agricultural Lime (CaCO₃) or Dolomite at 20–50 ppm. If high (&gt;8.5): apply fermented molasses/sugar, exchange surface water.</td>
                            </tr>
                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-activity"></use></svg>
                                        <strong>Dissolved Oxygen (DO)</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">5.0 ≤ x ≤ 9.0 mg/L</span></td>
                                <td>2.0 ≤ x < 5.0 or 9.0 < x ≤ 10.0 mg/L</td>
                                <td>x < 2.0 or x > 10.0 mg/L</td>
                                <td>Deploy all paddlewheels, apply emergency sodium percarbonate (granular oxygen), cease feeding immediately until DO recovers &gt;4.0 mg/L.</td>
                            </tr>
                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-sparkles"></use></svg>
                                        <strong>Unionized Ammonia (NH₃)</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">&lt; 0.03 ppm</span></td>
                                <td>0.03 – 0.05 ppm</td>
                                <td>&gt; 0.05 ppm (gill damage)</td>
                                <td>Apply molasses to stimulate biofloc heterotrophic uptake (C:N 15:1), increase bottom aeration, avoid high pH during peak afternoon heat.</td>
                            </tr>
                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                        <strong>Total Ammonia Nitrogen (TAN)</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">x < 0.50 mg/L</span></td>
                                <td>0.50 ≤ x ≤ 1.00 mg/L</td>
                                <td>x > 1.00 mg/L</td>
                                <td>Siphon central pond sludge drain, adjust feed input downwards, dose beneficial nitrifying probiotic bacteria (Nitrosomonas/Nitrobacter).</td>
                            </tr>
                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                                        <strong>Salinity</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">15 – 25 ppt</span></td>
                                <td>5–14 ppt &bull; 26–32 ppt</td>
                                <td>&lt; 2 ppt or &gt; 38 ppt</td>
                                <td>Euryhaline species. Maintain ionic ratios: Ca (400 mg/L), Mg (1200 mg/L), K (380 mg/L) at full seawater; scale proportionately for lower salinity.</td>
                            </tr>
                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-check-circle"></use></svg>
                                        <strong>Total Alkalinity</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">120 ≤ x ≤ 180 mg/L CaCO₃</span></td>
                                <td>80 ≤ x < 120 or 180 < x ≤ 250 mg/L</td>
                                <td>x < 80 or x > 250 mg/L (soft shell)</td>
                                <td>Apply sodium bicarbonate (NaHCO₃) to elevate alkalinity without raising pH excessively; essential for regular shrimp molting cycles.</td>
                            </tr>"""

new_table_rows = """                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-thermometer"></use></svg>
                                        <strong>Water Temperature</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">28.0 ≤ x ≤ 32.0 °C</span></td>
                                <td><span class="tools-badge-warn">20.0 ≤ x &lt; 28.0 or 32.0 &lt; x ≤ 35.0 °C</span></td>
                                <td><span class="tools-badge-crit">x &lt; 20.0 or x &gt; 35.0 °C</span></td>
                                <td>If high: increase water depth (&gt;1.2m), run paddlewheels, reduce feed by 20–50%. If low: cease feeding, maintain high bottom DO.</td>
                            </tr>
                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                                        <strong>pH Level</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">7.5 ≤ x ≤ 8.5 pH</span></td>
                                <td><span class="tools-badge-warn">6.5 ≤ x &lt; 7.5 or 8.5 &lt; x ≤ 9.0 pH</span></td>
                                <td><span class="tools-badge-crit">x &lt; 6.5 or x &gt; 9.0 pH</span></td>
                                <td>If low (&lt;7.5): apply Agricultural Lime (CaCO₃) or Dolomite at 20–50 ppm. If high (&gt;8.5): apply fermented molasses/sugar, exchange surface water.</td>
                            </tr>
                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-activity"></use></svg>
                                        <strong>Dissolved Oxygen (DO)</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">5.0 ≤ x ≤ 9.0 mg/L</span></td>
                                <td><span class="tools-badge-warn">2.0 ≤ x &lt; 5.0 or 9.0 &lt; x ≤ 10.0 mg/L</span></td>
                                <td><span class="tools-badge-crit">x &lt; 2.0 or x &gt; 10.0 mg/L</span></td>
                                <td>Deploy all paddlewheels, apply emergency sodium percarbonate (granular oxygen), cease feeding immediately until DO recovers &gt;4.0 mg/L.</td>
                            </tr>
                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-sparkles"></use></svg>
                                        <strong>Unionized Ammonia (NH₃)</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">&lt; 0.03 ppm</span></td>
                                <td><span class="tools-badge-warn">0.03 – 0.05 ppm</span></td>
                                <td><span class="tools-badge-crit">&gt; 0.05 ppm (gill damage)</span></td>
                                <td>Apply molasses to stimulate biofloc heterotrophic uptake (C:N 15:1), increase bottom aeration, avoid high pH during peak afternoon heat.</td>
                            </tr>
                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                        <strong>Total Ammonia Nitrogen (TAN)</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">x &lt; 0.50 mg/L</span></td>
                                <td><span class="tools-badge-warn">0.50 ≤ x ≤ 1.00 mg/L</span></td>
                                <td><span class="tools-badge-crit">x &gt; 1.00 mg/L</span></td>
                                <td>Siphon central pond sludge drain, adjust feed input downwards, dose beneficial nitrifying probiotic bacteria (Nitrosomonas/Nitrobacter).</td>
                            </tr>
                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                                        <strong>Salinity</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">15 – 25 ppt</span></td>
                                <td><span class="tools-badge-warn">5–14 ppt &bull; 26–32 ppt</span></td>
                                <td><span class="tools-badge-crit">&lt; 2 ppt or &gt; 38 ppt</span></td>
                                <td>Euryhaline species. Maintain ionic ratios: Ca (400 mg/L), Mg (1200 mg/L), K (380 mg/L) at full seawater; scale proportionately for lower salinity.</td>
                            </tr>
                            <tr>
                                <td>
                                    <div class="param-cell-title">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-check-circle"></use></svg>
                                        <strong>Total Alkalinity</strong>
                                    </div>
                                </td>
                                <td><span class="tools-badge-opt">120 ≤ x ≤ 180 mg/L CaCO₃</span></td>
                                <td><span class="tools-badge-warn">80 ≤ x &lt; 120 or 180 &lt; x ≤ 250 mg/L</span></td>
                                <td><span class="tools-badge-crit">x &lt; 80 or x &gt; 250 mg/L (soft shell)</span></td>
                                <td>Apply sodium bicarbonate (NaHCO₃) to elevate alkalinity without raising pH excessively; essential for regular shrimp molting cycles.</td>
                            </tr>"""

if old_table_rows in html:
    html = html.replace(old_table_rows, new_table_rows)
    print("SUCCESS: Updated all table rows with tools-badge-warn and tools-badge-crit in calculators.html")
else:
    print("WARNING: old_table_rows not matched exactly, checking with normalized newlines...")
    norm_html = html.replace("\r\n", "\n")
    norm_old = old_table_rows.replace("\r\n", "\n")
    norm_new = new_table_rows.replace("\r\n", "\n")
    if norm_old in norm_html:
        norm_html = norm_html.replace(norm_old, norm_new)
        html = norm_html
        print("SUCCESS: Normalized replace worked for table rows.")
    else:
        print("ERROR: table rows still not matched!")

with open("templates/calculators.html", "w", encoding="utf-8", newline="\r\n") as f:
    f.write(html)

# 2. Update static/css/style.css with tools-badge-warn and tools-badge-crit
with open("static/css/style.css", "r", encoding="utf-8") as f:
    css = f.read()

old_badge_css = """.calculators-page .tools-badge-opt {
    display: inline-block;
    padding: 4px 9px;
    font-size: 12px;
    font-weight: 750;
    color: #166534;
    background: #dcfce7;
    border: 1px solid #bbf7d0;
    border-radius: 6px;
    white-space: nowrap;
}"""

new_badge_css = """.calculators-page .tools-badge-opt {
    display: inline-block;
    padding: 4px 9px;
    font-size: 12px;
    font-weight: 750;
    color: #166534;
    background: #dcfce7;
    border: 1px solid #bbf7d0;
    border-radius: 6px;
    white-space: nowrap;
}

.calculators-page .tools-badge-warn {
    display: inline-block;
    padding: 4px 9px;
    font-size: 12px;
    font-weight: 750;
    color: #b45309;
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 6px;
    white-space: nowrap;
}

.calculators-page .tools-badge-crit {
    display: inline-block;
    padding: 4px 9px;
    font-size: 12px;
    font-weight: 750;
    color: #b91c1c;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 6px;
    white-space: nowrap;
}"""

if old_badge_css in css:
    css = css.replace(old_badge_css, new_badge_css)
    print("SUCCESS: Added tools-badge-warn and tools-badge-crit to style.css")
    with open("static/css/style.css", "w", encoding="utf-8", newline="\r\n") as f:
        f.write(css)
else:
    print("WARNING: old_badge_css not found in style.css!")

