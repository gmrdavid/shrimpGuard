with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

def normalize(text):
    return text.replace("\r\n", "\n")

html_norm = normalize(html)

# 1. Section 5 CO2 Calculator placement
co2_section = """        <!-- 5. FREE CARBON DIOXIDE (CO2) ESTIMATION & TUCKER MATRIX -->
        <section class="dashboard-section" id="tools-co2-section" aria-labelledby="tools-co2-heading">

            <div class="section-heading-row">
                <div>
                    <span class="section-eyebrow">RESPIRATORY GAS &amp; CARBONATE EQUILIBRIUM</span>
                    <h2 id="tools-co2-heading">Free Carbon Dioxide (CO₂) Concentration Estimation</h2>
                    <p>Tucker (1984) equilibrium factor based on water pH, temperature, and total alkalinity.</p>
                </div>
                <span class="section-count">Tool 5 of 5</span>
            </div>

            <article class="panel dashboard-panel ammonia-panel co2-panel" aria-labelledby="tools-co2-heading">

                <div class="panel-heading">
                    <div class="panel-heading-icon ammonia-heading-icon co2-heading-icon">
                        <svg class="ui-icon" aria-hidden="true">
                            <use href="#icon-activity"></use>
                        </svg>
                    </div>

                    <div>
                        <h2>Free Carbon Dioxide Estimation</h2>
                        <p>Formula: CO₂ (mg/L) = Factor (<em>f</em>) &times; Total Alkalinity (mg/L CaCO₃) &bull; Threshold for <em>P. vannamei</em>: &lt; 10.0 mg/L safe, &gt; 20.0 mg/L critical</p>
                    </div>
                </div>

                <div class="ammonia-calc-grid">

                    <!-- INPUT CARD -->
                    <div class="ammonia-card ammonia-card-input">
                        <div class="ammonia-card-header">
                            <span class="ammonia-card-label">INPUT ALKALINITY &amp; SENSOR PARAMETERS</span>
                        </div>

                        <!-- ALKALINITY INPUT -->
                        <div class="ammonia-field-group">
                            <div class="ammonia-input-label-row">
                                <label for="tools-co2-alkalinity" class="ammonia-input-label">Total Alkalinity</label>
                                <span class="ammonia-input-unit">mg/L (ppm CaCO₃)</span>
                            </div>
                            <div class="ammonia-input-controls">
                                <input
                                    type="number"
                                    id="tools-co2-alkalinity"
                                    class="ammonia-number-input"
                                    min="10"
                                    max="500"
                                    step="1"
                                    value="140"
                                    placeholder="e.g. 140">
                                <button type="button" id="tools-co2-calc-btn" class="ammonia-btn-primary">
                                    Calculate
                                </button>
                            </div>
                        </div>

                        <!-- PRESETS -->
                        <div class="ammonia-presets-row">
                            <span class="ammonia-presets-label">Common Alkalinity Presets:</span>
                            <div class="ammonia-preset-chips" id="tools-co2-preset-chips">
                                <button type="button" class="preset-chip" data-alk="80">80 ppm</button>
                                <button type="button" class="preset-chip" data-alk="100">100 ppm</button>
                                <button type="button" class="preset-chip" data-alk="120">120 ppm</button>
                                <button type="button" class="preset-chip active" data-alk="140">140 ppm</button>
                                <button type="button" class="preset-chip" data-alk="160">160 ppm</button>
                                <button type="button" class="preset-chip" data-alk="180">180 ppm</button>
                            </div>
                        </div>

                        <!-- LIVE SENSORS SYNC INDICATORS -->
                        <div class="ammonia-live-sensors">
                            <div class="ammonia-sensor-badge">
                                <span class="sensor-badge-title">LIVE SENSOR TEMP</span>
                                <span class="sensor-badge-val"><span id="tools-co2-live-temp">--</span> °C</span>
                            </div>
                            <div class="ammonia-sensor-badge">
                                <span class="sensor-badge-title">LIVE SENSOR pH</span>
                                <span class="sensor-badge-val"><span id="tools-co2-live-ph">--</span> pH</span>
                            </div>
                        </div>

                        <!-- SIMULATION / OVERRIDE TOGGLE -->
                        <div class="ammonia-override-box">
                            <label class="ammonia-checkbox-label">
                                <input type="checkbox" id="tools-co2-override-cb">
                                <span>Simulate custom temperature &amp; pH (What-if scenario)</span>
                            </label>
                            <div id="tools-co2-override-fields" class="ammonia-override-fields" hidden>
                                <div class="override-field">
                                    <label for="tools-co2-custom-temp">Temp (°C):</label>
                                    <input type="number" id="tools-co2-custom-temp" min="5" max="35" step="0.1" value="28.0" class="override-input">
                                </div>
                                <div class="override-field">
                                    <label for="tools-co2-custom-ph">pH Level:</label>
                                    <input type="number" id="tools-co2-custom-ph" min="6.0" max="9.0" step="0.05" value="7.60" class="override-input">
                                </div>
                            </div>
                        </div>

                    </div>

                    <!-- OUTPUT CARD -->
                    <div class="ammonia-card ammonia-card-result">
                        <div class="ammonia-card-header">
                            <span class="ammonia-card-label">ESTIMATED FREE CARBON DIOXIDE (CO₂)</span>
                            <span id="tools-co2-badge" class="wqi-metric-badge badge-optimal">Safe (&lt; 10.0 mg/L)</span>
                        </div>

                        <div class="ammonia-result-display">
                            <span id="tools-co2-result" class="ammonia-big-value">6.748</span>
                            <span class="ammonia-big-unit">mg/L (ppm)</span>
                        </div>

                        <!-- BREAKDOWN STEPS -->
                        <div class="ammonia-formula-breakdown">
                            <div class="formula-step">
                                <span class="step-tag">Step 1</span>
                                <span>Table factor at <strong id="tools-co2-step-temp">28.0°C</strong> &amp; pH <strong id="tools-co2-step-ph">7.60</strong>: <strong><em>f</em> = <span id="tools-co2-step-factor">0.0482</span></strong></span>
                            </div>
                            <div class="formula-step">
                                <span class="step-tag">Step 2</span>
                                <span>Multiply by Alkalinity: <span id="tools-co2-step-math">0.0482 &times; 140 mg/L</span> = <strong id="tools-co2-step-final">6.748 mg/L</strong></span>
                            </div>
                        </div>

                        <!-- BIOLOGICAL ASSESSMENT -->
                        <div id="tools-co2-assessment" class="ammonia-assessment is-safe">
                            <p id="tools-co2-assessment-text">
                                Free CO₂ (6.748 mg/L) is within the safe zootechnical range (&lt; 10.0 mg/L) for Penaeus vannamei. Shrimp respiration and hemocyanin oxygen affinity remain optimal.
                            </p>
                        </div>

                        <!-- SENSITIVITY CALLOUT -->
                        <div class="ammonia-sensitivity-callout">
                            <svg class="ui-icon" aria-hidden="true">
                                <use href="#icon-lightbulb"></use>
                            </svg>
                            <p id="tools-co2-sensitivity">
                                <strong>Diurnal Dynamics Insight:</strong> Free CO₂ reaches peak concentrations just before dawn due to uninterrupted shrimp and plankton respiration during the night, while pH dips to its diurnal trough. Daytime photosynthesis rapidly strips CO₂ and elevates pH.
                            </p>
                        </div>

                    </div>

                </div>

                <!-- CARD FOOTER WITH MODAL TRIGGER -->
                <div class="ammonia-dialog-trigger-row">
                    <button type="button" id="open-tools-tucker" class="ammonia-matrix-popup-btn">
                        <svg class="ui-icon" aria-hidden="true">
                            <use href="#icon-chart"></use>
                        </svg>
                        <span>View Tucker (1984) Reference Matrix</span>
                    </button>
                    <span class="matrix-hint-text">Opens reference table with dynamic sensor temperature &amp; pH highlighting</span>
                </div>

            </article>

        </section>"""

target_after_ammonia = """            </article>

        </section>


        <!-- 5. PENAEUS VANNAMEI SPECIES WATER QUALITY STANDARDS & PROTOCOLS -->"""

replacement_after_ammonia = f"""            </article>

        </section>


{co2_section}


        <!-- 6. PENAEUS VANNAMEI SPECIES WATER QUALITY STANDARDS & PROTOCOLS -->"""

assert normalize(target_after_ammonia) in html_norm, "target_after_ammonia not found"
html_norm = html_norm.replace(normalize(target_after_ammonia), normalize(replacement_after_ammonia), 1)

# 2. Tucker Matrix Modal placement (after Van Wyk modal)
tucker_modal = """<!-- TUCKER (1984) REFERENCE MATRIX POPUP DIALOG -->
<div id="tools-tucker-modal" class="modal-dialog-backdrop" hidden>
    <div class="modal-dialog-container" role="dialog" aria-modal="true" aria-labelledby="tools-modal-tucker-title">

        <div class="modal-dialog-header">
            <div class="modal-header-text">
                <div class="panel-heading-icon ammonia-heading-icon modal-icon">
                    <svg class="ui-icon" aria-hidden="true">
                        <use href="#icon-chart"></use>
                    </svg>
                </div>
                <div>
                    <h3 id="tools-modal-tucker-title">Tucker (1984) Reference Matrix</h3>
                    <p>Factors for calculating carbon dioxide concentrations in water with known pH, temperature and alkalinity measurements</p>
                </div>
            </div>
            <button type="button" id="close-tools-tucker" class="modal-close-btn" aria-label="Close dialog">
                &times;
            </button>
        </div>

        <div class="modal-dialog-body">

            <div class="table-legend-row">
                <span class="legend-text">Active values highlighted:</span>
                <div class="legend-badges">
                    <span class="legend-chip chip-col">Active Temp Column</span>
                    <span class="legend-chip chip-row">Active pH Row</span>
                    <span class="legend-chip chip-intersect">Intersection Factor (<em>f</em>)</span>
                </div>
            </div>

            <div class="table-responsive van-wyk-table-scroll tucker-table-scroll">
                <table class="van-wyk-grid tucker-grid" id="tools-tucker-matrix">
                    <thead>
                        <tr>
                            <th rowspan="2" class="th-ph">pH</th>
                            <th colspan="7" class="th-temp-header">Temperatures (°C)</th>
                        </tr>
                        <tr class="th-temp-sub">
                            <th data-temp="5">5</th>
                            <th data-temp="10">10</th>
                            <th data-temp="15">15</th>
                            <th data-temp="20">20</th>
                            <th data-temp="25">25</th>
                            <th data-temp="30">30</th>
                            <th data-temp="35">35</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr data-ph="6.0"><td class="td-ph">6.0</td><td data-temp="5">2.915</td><td data-temp="10">2.539</td><td data-temp="15">2.315</td><td data-temp="20">2.112</td><td data-temp="25">1.970</td><td data-temp="30">1.882</td><td data-temp="35">1.839</td></tr>
                        <tr data-ph="6.2"><td class="td-ph">6.2</td><td data-temp="5">1.839</td><td data-temp="10">1.602</td><td data-temp="15">1.460</td><td data-temp="20">1.333</td><td data-temp="25">1.244</td><td data-temp="30">1.187</td><td data-temp="35">1.160</td></tr>
                        <tr data-ph="6.4"><td class="td-ph">6.4</td><td data-temp="5">1.160</td><td data-temp="10">1.010</td><td data-temp="15">0.921</td><td data-temp="20">0.841</td><td data-temp="25">0.784</td><td data-temp="30">0.749</td><td data-temp="35">0.732</td></tr>
                        <tr data-ph="6.6"><td class="td-ph">6.6</td><td data-temp="5">0.732</td><td data-temp="10">0.637</td><td data-temp="15">0.582</td><td data-temp="20">0.531</td><td data-temp="25">0.495</td><td data-temp="30">0.473</td><td data-temp="35">0.462</td></tr>
                        <tr data-ph="6.8"><td class="td-ph">6.8</td><td data-temp="5">0.462</td><td data-temp="10">0.402</td><td data-temp="15">0.367</td><td data-temp="20">0.335</td><td data-temp="25">0.313</td><td data-temp="30">0.298</td><td data-temp="35">0.291</td></tr>
                        <tr data-ph="7.0"><td class="td-ph">7.0</td><td data-temp="5">0.291</td><td data-temp="10">0.254</td><td data-temp="15">0.232</td><td data-temp="20">0.211</td><td data-temp="25">0.197</td><td data-temp="30">0.188</td><td data-temp="35">0.184</td></tr>
                        <tr data-ph="7.2"><td class="td-ph">7.2</td><td data-temp="5">0.184</td><td data-temp="10">0.160</td><td data-temp="15">0.146</td><td data-temp="20">0.133</td><td data-temp="25">0.124</td><td data-temp="30">0.119</td><td data-temp="35">0.116</td></tr>
                        <tr data-ph="7.4"><td class="td-ph">7.4</td><td data-temp="5">0.116</td><td data-temp="10">0.101</td><td data-temp="15">0.092</td><td data-temp="20">0.084</td><td data-temp="25">0.078</td><td data-temp="30">0.075</td><td data-temp="35">0.073</td></tr>
                        <tr data-ph="7.6"><td class="td-ph">7.6</td><td data-temp="5">0.073</td><td data-temp="10">0.064</td><td data-temp="15">0.058</td><td data-temp="20">0.053</td><td data-temp="25">0.050</td><td data-temp="30">0.047</td><td data-temp="35">0.046</td></tr>
                        <tr data-ph="7.8"><td class="td-ph">7.8</td><td data-temp="5">0.046</td><td data-temp="10">0.040</td><td data-temp="15">0.037</td><td data-temp="20">0.034</td><td data-temp="25">0.031</td><td data-temp="30">0.030</td><td data-temp="35">0.030</td></tr>
                        <tr data-ph="8.0"><td class="td-ph">8.0</td><td data-temp="5">0.029</td><td data-temp="10">0.025</td><td data-temp="15">0.023</td><td data-temp="20">0.021</td><td data-temp="25">0.020</td><td data-temp="30">0.019</td><td data-temp="35">0.018</td></tr>
                        <tr data-ph="8.2"><td class="td-ph">8.2</td><td data-temp="5">0.018</td><td data-temp="10">0.016</td><td data-temp="15">0.015</td><td data-temp="20">0.013</td><td data-temp="25">0.012</td><td data-temp="30">0.012</td><td data-temp="35">0.011</td></tr>
                        <tr data-ph="8.4"><td class="td-ph">8.4</td><td data-temp="5">0.012</td><td data-temp="10">0.010</td><td data-temp="15">0.009</td><td data-temp="20">0.008</td><td data-temp="25">0.008</td><td data-temp="30">0.008</td><td data-temp="35">0.007</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="van-wyk-source-credit tucker-source-credit">
                Tucker (1984). Factors should be multiplied by total alkalinity (mg/L) to get carbon dioxide (mg/L). For practical purposes, CO₂ concentrations are negligible above pH = 8.4.
            </div>

        </div>

        <div class="modal-dialog-footer">
            <button type="button" id="tools-tucker-modal-close-action" class="ammonia-btn-primary">
                Close Matrix
            </button>
        </div>

    </div>
</div>"""

target_after_van_wyk = """        <div class="modal-dialog-footer">
            <button type="button" id="tools-modal-close-action" class="ammonia-btn-primary">
                Close Matrix
            </button>
        </div>

    </div>
</div>"""

replacement_after_van_wyk = f"""        <div class="modal-dialog-footer">
            <button type="button" id="tools-modal-close-action" class="ammonia-btn-primary">
                Close Matrix
            </button>
        </div>

    </div>
</div>


{tucker_modal}"""

assert normalize(target_after_van_wyk) in html_norm, "target_after_van_wyk not found"
html_norm = html_norm.replace(normalize(target_after_van_wyk), normalize(replacement_after_van_wyk), 1)

# 3. Save calculation snapshot modal preview item
target_save_preview = """                    <div class="save-summary-item">
                        <span class="summary-label">Unionized NH₃:</span>
                        <span id="save-preview-nh3" class="summary-val">-- ppm</span>
                    </div>"""

replacement_save_preview = """                    <div class="save-summary-item">
                        <span class="summary-label">Unionized NH₃:</span>
                        <span id="save-preview-nh3" class="summary-val">-- ppm</span>
                    </div>
                    <div class="save-summary-item">
                        <span class="summary-label">Free CO₂:</span>
                        <span id="save-preview-co2" class="summary-val">-- mg/L</span>
                    </div>"""

assert normalize(target_save_preview) in html_norm, "target_save_preview not found"
html_norm = html_norm.replace(normalize(target_save_preview), normalize(replacement_save_preview), 1)

# 4. Export Modal Category 8 and Select All button
target_export_select_all = """<button type="button" id="export-cat-select-all" class="export-pill-btn">Select All (7)</button>"""
replacement_export_select_all = """<button type="button" id="export-cat-select-all" class="export-pill-btn">Select All (8)</button>"""
assert normalize(target_export_select_all) in html_norm, "target_export_select_all not found"
html_norm = html_norm.replace(normalize(target_export_select_all), normalize(replacement_export_select_all), 1)

target_export_cats = """                    <!-- Category 7: Ammonia -->
                    <label class="category-checkbox-card" id="card-cat-ammonia">
                        <input type="checkbox" name="export-category" value="ammonia" checked>
                        <div class="cat-card-body">
                            <div class="cat-card-header">
                                <span class="cat-card-title">Unionized Ammonia (NH₃)</span>
                                <span class="cat-badge">Toxicity</span>
                            </div>
                            <p class="cat-card-desc">TAN, temperature, pH, salinity, un-ionized fraction <em>f</em>, toxic NH₃ level, risk status.</p>
                        </div>
                    </label>
                </div>"""

replacement_export_cats = """                    <!-- Category 7: Ammonia -->
                    <label class="category-checkbox-card" id="card-cat-ammonia">
                        <input type="checkbox" name="export-category" value="ammonia" checked>
                        <div class="cat-card-body">
                            <div class="cat-card-header">
                                <span class="cat-card-title">Unionized Ammonia (NH₃)</span>
                                <span class="cat-badge">Toxicity</span>
                            </div>
                            <p class="cat-card-desc">TAN, temperature, pH, salinity, un-ionized fraction <em>f</em>, toxic NH₃ level, risk status.</p>
                        </div>
                    </label>

                    <!-- Category 8: Free Carbon Dioxide -->
                    <label class="category-checkbox-card" id="card-cat-co2">
                        <input type="checkbox" name="export-category" value="co2" checked>
                        <div class="cat-card-body">
                            <div class="cat-card-header">
                                <span class="cat-card-title">Free Carbon Dioxide (CO₂)</span>
                                <span class="cat-badge">Tucker 1984</span>
                            </div>
                            <p class="cat-card-desc">Total alkalinity, temperature, pH, Tucker factor <em>f</em>, free CO₂ (mg/L), risk status.</p>
                        </div>
                    </label>
                </div>"""

assert normalize(target_export_cats) in html_norm, "target_export_cats not found"
html_norm = html_norm.replace(normalize(target_export_cats), normalize(replacement_export_cats), 1)

with open("templates/calculators.html", "w", encoding="utf-8") as f:
    f.write(html_norm)

print("Successfully updated templates/calculators.html!")
