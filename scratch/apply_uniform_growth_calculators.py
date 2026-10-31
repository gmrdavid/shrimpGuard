# -*- coding: utf-8 -*-
"""
Re-architect Section 2 in templates/calculators.html to be 100% UNIFORM with Section 1 and Section 3.
Uses standard classes:
- .dashboard-section
- .section-heading-row (.section-eyebrow, h2, p, .monitoring-species-pill)
- .tools-tab-selector-bar (.tools-tab-selector-label, .tools-tab-chips with .preset-chip)
- .tools-calc-panel
- .tools-panel-header (.panel-heading-icon, h2, p)
- .tools-grid-split
- .tools-input-column (.tools-subheading-row, .tools-subheading, .tools-form-grid, .tools-field-label, .field-label-text, .dashboard-field-wrap, .input-unit, .tools-callout-tip)
- .tools-output-column (.tools-subheading, .tools-result-cards, .tools-res-card, .highlight-card, .res-card-header, .res-card-label, .res-value-row, .res-big-value, .res-accent-value, .res-unit, .res-secondary-val, .res-card-detail, .res-meal-breakdown)
"""

uniform_section2_html = '''        <!-- 2. SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE CALCULATORS (Eqs. 1–8) -->
        <section class="dashboard-section" id="tools-growth-section" aria-labelledby="growth-calculators-title">

            <div class="section-heading-row">
                <div>
                    <span class="section-eyebrow">ZOOTECHNICAL &bull; PENAEUS VANNAMEI PRODUCTION EQUATIONS</span>
                    <h2 id="growth-calculators-title">Shrimp Growth &amp; Zootechnical Performance Calculators (Eqs. 1–8)</h2>
                    <p>Standard scientific aquaculture equations computing survival rate, average body weight, daily gain, specific growth rate, pond biomass, feed conversion ratio, and Fulton's condition factor.</p>
                </div>
                <div class="monitoring-species-pill">
                    <span class="species-dot"></span>
                    <span>8 Scientific Equations</span>
                </div>
            </div>

            <!-- UNIFORM TAB SELECTOR -->
            <div class="tools-tab-selector-bar">
                <span class="tools-tab-selector-label">CALCULATOR:</span>
                <div class="tools-tab-chips" role="tablist" aria-label="Growth Calculators">
                    <button type="button" class="preset-chip active" id="tab-btn-master" role="tab" aria-selected="true" data-pane="master">
                        All-in-One Engine (Eqs. 1–8)
                    </button>
                    <button type="button" class="preset-chip" id="tab-btn-eq1" role="tab" aria-selected="false" data-pane="eq1">
                        Eq. 1: Survival Rate (SR)
                    </button>
                    <button type="button" class="preset-chip" id="tab-btn-eq2" role="tab" aria-selected="false" data-pane="eq2">
                        Eq. 2: Average Body Weight (FABW)
                    </button>
                    <button type="button" class="preset-chip" id="tab-btn-eq34" role="tab" aria-selected="false" data-pane="eq34">
                        Eqs. 3–4: ADWG &amp; SGR
                    </button>
                    <button type="button" class="preset-chip" id="tab-btn-eq56" role="tab" aria-selected="false" data-pane="eq56">
                        Eqs. 5–6: Biomass (IB &amp; FB)
                    </button>
                    <button type="button" class="preset-chip" id="tab-btn-eq7" role="tab" aria-selected="false" data-pane="eq7">
                        Eq. 7: Feed Conversion (FCR)
                    </button>
                    <button type="button" class="preset-chip" id="tab-btn-eq8" role="tab" aria-selected="false" data-pane="eq8">
                        Eq. 8: Fulton's Condition (K)
                    </button>
                </div>
            </div>

            <!-- PANE 1: MASTER UNIFIED ENGINE (Eqs. 1–8) -->
            <div id="pane-growth-master" class="growth-tab-pane active" role="tabpanel" aria-labelledby="tab-btn-master">
                <article class="panel dashboard-panel tools-calc-panel">

                    <div class="tools-panel-header">
                        <div class="panel-heading-icon tools-icon-biomass">
                            <svg class="ui-icon" aria-hidden="true">
                                <use href="#icon-shrimp"></use>
                            </svg>
                        </div>
                        <div>
                            <h2>All-in-One Growth &amp; Production Performance Engine</h2>
                            <p>Unified zootechnical model computing survival, growth velocities, biomass conversion, FCR, and Fulton's K from pond stocking and harvest data.</p>
                        </div>
                    </div>

                    <div class="tools-grid-split">

                        <!-- INPUTS COLUMN -->
                        <div class="tools-input-column">
                            <div class="tools-subheading-row">
                                <h3 class="tools-subheading">Pond Stocking &amp; Harvest Parameters</h3>
                                <button type="button" id="btn-sync-from-biomass" class="tools-chip-btn" title="Sync live population and ABW values from Biomass Section above">
                                    Sync Biomass Tool
                                </button>
                            </div>

                            <!-- Presets Row (matching Ammonia presets) -->
                            <div class="ammonia-presets-row" style="margin-bottom: 14px;">
                                <span class="ammonia-presets-label">Pond Presets:</span>
                                <div class="ammonia-preset-chips" id="growth-master-presets">
                                    <button type="button" class="preset-chip active btn-preset-growth" data-preset="commercial">Commercial 90d</button>
                                    <button type="button" class="preset-chip btn-preset-growth" data-preset="intensive">Intensive 75d</button>
                                    <button type="button" class="preset-chip btn-preset-growth" data-preset="nursery">Nursery 30d</button>
                                </div>
                            </div>

                            <div class="tools-form-grid">

                                <!-- Initial Stocking (IS) -->
                                <label class="tools-field-label" for="gm-initial-stocking">
                                    <span class="field-label-text">Initial Stocking (IS)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="gm-initial-stocking" min="1000" max="5000000" step="1000" value="100000" placeholder="e.g. 100000">
                                        <span class="input-unit">shrimp</span>
                                    </span>
                                </label>

                                <!-- Live Harvest Count (LHC) -->
                                <label class="tools-field-label" for="gm-live-harvest-count">
                                    <span class="field-label-text">Live Harvest Count (LHC)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="gm-live-harvest-count" min="100" max="5000000" step="500" value="85000" placeholder="e.g. 85000">
                                        <span class="input-unit">shrimp</span>
                                    </span>
                                </label>

                                <!-- Days of Culture (DOC) -->
                                <label class="tools-field-label" for="gm-days-of-culture">
                                    <span class="field-label-text">Days of Culture (DOC)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="gm-days-of-culture" min="1" max="365" step="1" value="90" placeholder="e.g. 90">
                                        <span class="input-unit">days</span>
                                    </span>
                                </label>

                                <!-- Initial Body Weight (IBW) -->
                                <label class="tools-field-label" for="gm-initial-weight">
                                    <span class="field-label-text">Initial Body Weight (IBW)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="gm-initial-weight" min="0.001" max="10" step="0.005" value="0.010" placeholder="e.g. 0.010">
                                        <span class="input-unit">grams</span>
                                    </span>
                                </label>

                                <!-- Bulk Weight (BW) -->
                                <label class="tools-field-label" for="gm-bulk-weight">
                                    <span class="field-label-text">Harvest Bulk Weight (BW)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="gm-bulk-weight" min="10" max="500000" step="10" value="1700" placeholder="e.g. 1700">
                                        <span class="input-unit">kg</span>
                                    </span>
                                    <input type="hidden" id="gm-bw-unit" value="kg">
                                </label>

                                <!-- Total Feed Given (TFG) -->
                                <label class="tools-field-label" for="gm-total-feed">
                                    <span class="field-label-text">Total Feed Given (TFG)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="gm-total-feed" min="10" max="500000" step="25" value="2125" placeholder="e.g. 2125">
                                        <span class="input-unit">kg</span>
                                    </span>
                                    <input type="hidden" id="gm-feed-unit" value="kg">
                                </label>

                                <!-- Total Length (TL) -->
                                <label class="tools-field-label" for="gm-total-length" style="grid-column: span 2;">
                                    <span class="field-label-text">Average Total Length (TL)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="gm-total-length" min="1.0" max="30.0" step="0.1" value="12.9" placeholder="e.g. 12.9">
                                        <span class="input-unit">cm</span>
                                    </span>
                                </label>

                            </div>

                            <!-- Scientific Model Tip -->
                            <div class="tools-callout-tip">
                                <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                                <p>
                                    <strong>Scientific Model Equations (Eqs. 1–8):</strong> Conforms to validated zootechnical research for <em>Penaeus vannamei</em> shrimp culture. Computations update in real-time as values are entered.
                                </p>
                            </div>

                        </div>

                        <!-- OUTPUTS COLUMN -->
                        <div class="tools-output-column">
                            <h3 class="tools-subheading">Computed Performance Metrics</h3>

                            <div class="tools-result-cards">

                                <!-- Eq. 1: Survival Rate -->
                                <div class="tools-res-card">
                                    <div class="res-card-header">
                                        <span class="res-card-label">EQ. 1 &bull; SURVIVAL RATE (SR)</span>
                                        <span id="gm-res-sr-badge" class="wqi-metric-badge badge-optimal">Optimal</span>
                                    </div>
                                    <div class="res-value-row">
                                        <strong id="gm-res-sr-val" class="res-big-value">85.00</strong>
                                        <span class="res-unit">%</span>
                                        <span class="res-secondary-val">(<span id="gm-res-mortality-count">15,000</span> mortality &bull; <span id="gm-res-mortality-pct">15.00%</span>)</span>
                                    </div>
                                    <p class="res-card-detail">
                                        <code>SR = (LHC / IS) &times; 100</code> &bull; <span id="gm-sub-sr">(85,000 / 100,000) &times; 100 = 85.00%</span>
                                    </p>
                                </div>

                                <!-- Eq. 2: Final Average Body Weight -->
                                <div class="tools-res-card">
                                    <div class="res-card-header">
                                        <span class="res-card-label">EQ. 2 &bull; FINAL AVG BODY WEIGHT (FABW)</span>
                                        <span class="wqi-metric-badge badge-optimal">Size 50</span>
                                    </div>
                                    <div class="res-value-row">
                                        <strong id="gm-res-fabw-val" class="res-big-value">20.00</strong>
                                        <span class="res-unit">g / shrimp</span>
                                        <span class="res-secondary-val">(<strong id="gm-res-count-per-kg">50.0</strong> pcs/kg)</span>
                                    </div>
                                    <p class="res-card-detail">
                                        <code>FABW = BW / LHC</code> &bull; <span id="gm-sub-fabw">1,700,000 g / 85,000 = 20.00 g</span>
                                    </p>
                                </div>

                                <!-- Eqs. 3 & 4: ADWG & SGR -->
                                <div class="tools-res-card">
                                    <div class="res-card-header">
                                        <span class="res-card-label">EQS. 3 &amp; 4 &bull; GROWTH RATES (ADWG &amp; SGR)</span>
                                        <span id="gm-res-adwg-badge" class="wqi-metric-badge badge-optimal">Optimal Growth</span>
                                    </div>
                                    <div class="res-value-row">
                                        <strong id="gm-res-adwg-val" class="res-big-value">0.2221</strong>
                                        <span class="res-unit">g / day</span>
                                        <span class="res-secondary-val">(<strong id="gm-res-weekly-gain">1.555</strong> g/week &bull; SGR: <strong id="gm-res-sgr-val">8.445</strong>%/day)</span>
                                    </div>
                                    <p class="res-card-detail">
                                        <code>ADWG = (FABW - IBW) / DOC</code> &bull; Weight Multiplier: <strong id="gm-res-weight-mult">2,000&times;</strong>
                                    </p>
                                </div>

                                <!-- Eqs. 5 & 6: Biomass -->
                                <div class="tools-res-card">
                                    <div class="res-card-header">
                                        <span class="res-card-label">EQS. 5 &amp; 6 &bull; POND BIOMASS CONVERSION (IB &amp; FB)</span>
                                        <span class="res-secondary-val">Standing Yield</span>
                                    </div>
                                    <div class="res-value-row">
                                        <strong id="gm-res-fb-kg" class="res-big-value">1,700.0</strong>
                                        <span class="res-unit">kg harvest</span>
                                        <span class="res-secondary-val">(Initial: <span id="gm-res-ib-kg">1.0</span> kg)</span>
                                    </div>
                                    <p class="res-card-detail">
                                        Net Pond Biomass Yield Gain: <strong id="gm-res-net-biomass">1,699.00 kg</strong> (1.70 metric tons)
                                    </p>
                                </div>

                                <!-- Eq. 7: Feed Conversion Ratio (Highlight Card) -->
                                <div class="tools-res-card highlight-card">
                                    <div class="res-card-header">
                                        <span class="res-card-label">EQ. 7 &bull; FEED CONVERSION RATIO (FCR)</span>
                                        <span id="gm-res-fcr-badge" class="wqi-metric-badge badge-optimal">Optimal (1.20–1.50)</span>
                                    </div>
                                    <div class="res-value-row">
                                        <strong id="gm-res-fcr-val" class="res-big-value res-accent-value">1.251</strong>
                                        <span class="res-unit">FCR</span>
                                        <span class="res-secondary-val">(Feed Efficiency: <strong id="gm-res-feed-efficiency">79.95%</strong>)</span>
                                    </div>
                                    <div class="res-meal-breakdown">
                                        <span>Formula: <code>FCR = TFG / (FB - IB)</code></span>
                                        <span id="gm-sub-fcr">2,125.0 kg feed / 1,699.0 kg gain = 1.251</span>
                                    </div>
                                </div>

                                <!-- Eq. 8: Fulton's Condition Factor -->
                                <div class="tools-res-card">
                                    <div class="res-card-header">
                                        <span class="res-card-label">EQ. 8 &bull; FULTON'S CONDITION FACTOR (K)</span>
                                        <span id="gm-res-k-badge" class="wqi-metric-badge badge-optimal">Optimal Condition</span>
                                    </div>
                                    <div class="res-value-row">
                                        <strong id="gm-res-k-val" class="res-big-value">0.9317</strong>
                                        <span class="res-unit">K factor</span>
                                    </div>
                                    <p class="res-card-detail">
                                        Profile: <strong id="gm-res-k-profile">Healthy, well-proportioned robust girth</strong> &bull; <code>K = (FABW / TL&sup3;) &times; 100</code>
                                    </p>
                                </div>

                            </div>

                        </div>

                    </div>

                </article>
            </div>

            <!-- PANE 2: Eq. 1 SURVIVAL RATE (SR) -->
            <div id="pane-growth-eq1" class="growth-tab-pane" role="tabpanel" aria-labelledby="tab-btn-eq1" hidden>
                <article class="panel dashboard-panel tools-calc-panel">

                    <div class="tools-panel-header">
                        <div class="panel-heading-icon tools-icon-biomass">
                            <svg class="ui-icon" aria-hidden="true">
                                <use href="#icon-shrimp"></use>
                            </svg>
                        </div>
                        <div>
                            <h2>Equation 1: Survival Rate (SR) Calculator</h2>
                            <p>Formula: <code>SR = (LHC / IS) &times; 100</code> &bull; Computes percentage of post-larvae harvested alive.</p>
                        </div>
                    </div>

                    <div class="tools-grid-split">
                        <div class="tools-input-column">
                            <h3 class="tools-subheading">Stocking &amp; Harvest Counts</h3>

                            <div class="tools-form-grid">
                                <label class="tools-field-label" for="indiv-is">
                                    <span class="field-label-text">Initial Stocking (IS)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-is" min="1000" max="10000000" step="1000" value="100000" placeholder="e.g. 100000">
                                        <span class="input-unit">shrimp</span>
                                    </span>
                                </label>

                                <label class="tools-field-label" for="indiv-lhc">
                                    <span class="field-label-text">Live Harvest Count (LHC)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-lhc" min="100" max="10000000" step="500" value="85000" placeholder="e.g. 85000">
                                        <span class="input-unit">shrimp</span>
                                    </span>
                                </label>
                            </div>

                            <div class="tools-callout-tip">
                                <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                                <p>
                                    <strong>Commercial Benchmark:</strong> Commercial <em>Penaeus vannamei</em> survival typically targets &ge;80% in well-managed biosecure ponds. Survival between 65% and 79% is acceptable; &lt;65% indicates environmental or pathogen stress.
                                </p>
                            </div>
                        </div>

                        <div class="tools-output-column">
                            <h3 class="tools-subheading">Computed Survival Results</h3>

                            <div class="tools-result-cards">
                                <div class="tools-res-card highlight-card">
                                    <div class="res-card-header">
                                        <span class="res-card-label">COMPUTED SURVIVAL RATE</span>
                                        <span id="indiv-sr-badge" class="wqi-metric-badge badge-optimal">Optimal</span>
                                    </div>
                                    <div class="res-value-row">
                                        <strong id="indiv-sr-result" class="res-big-value res-accent-value">85.00</strong>
                                        <span class="res-unit">%</span>
                                    </div>
                                    <div class="res-meal-breakdown">
                                        <span>Mortality Count: <strong id="indiv-sr-mortality-count">15,000 shrimp</strong></span>
                                        <span>Cumulative Loss: <strong id="indiv-sr-mortality-pct">15.00%</strong></span>
                                    </div>
                                </div>

                                <div class="tools-res-card">
                                    <span class="res-card-label">STEP-BY-STEP SUBSTITUTION</span>
                                    <p class="res-card-detail" style="margin-top: 6px;">
                                        <code id="indiv-sr-step-math">SR = (85,000 / 100,000) &times; 100 = 85.00%</code>
                                    </p>
                                    <p id="indiv-sr-rating" class="res-card-detail" style="margin-top: 8px;">
                                        Optimal survival rate exceeding typical commercial benchmark (&ge;80%). Favorable pond conditions and healthy stock transition.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                </article>
            </div>

            <!-- PANE 3: Eq. 2 FINAL AVERAGE BODY WEIGHT (FABW) -->
            <div id="pane-growth-eq2" class="growth-tab-pane" role="tabpanel" aria-labelledby="tab-btn-eq2" hidden>
                <article class="panel dashboard-panel tools-calc-panel">

                    <div class="tools-panel-header">
                        <div class="panel-heading-icon tools-icon-biomass">
                            <svg class="ui-icon" aria-hidden="true">
                                <use href="#icon-calculator"></use>
                            </svg>
                        </div>
                        <div>
                            <h2>Equation 2: Final Average Body Weight (FABW) Calculator</h2>
                            <p>Formula: <code>FABW = BW / LHC</code> &bull; Determines individual average shrimp weight and count per kilogram.</p>
                        </div>
                    </div>

                    <div class="tools-grid-split">
                        <div class="tools-input-column">
                            <h3 class="tools-subheading">Harvest Mass &amp; Count</h3>

                            <div class="tools-form-grid">
                                <label class="tools-field-label" for="indiv-bw">
                                    <span class="field-label-text">Harvest Bulk Weight (BW)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-bw" min="1" max="1000000" step="10" value="1700" placeholder="e.g. 1700">
                                        <span class="input-unit">kg</span>
                                    </span>
                                    <input type="hidden" id="indiv-bw-unit" value="kg">
                                </label>

                                <label class="tools-field-label" for="indiv-fabw-lhc">
                                    <span class="field-label-text">Live Harvest Count (LHC)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-fabw-lhc" min="100" max="10000000" step="500" value="85000" placeholder="e.g. 85000">
                                        <span class="input-unit">shrimp</span>
                                    </span>
                                </label>
                            </div>

                            <div class="tools-callout-tip">
                                <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                                <p>
                                    <strong>Commercial Sizing:</strong> In commercial seafood trade, shrimp size is indexed as count per kilogram ($1000 / FABW$). 20.0 g corresponds to Size 50 count, commanding strong market pricing.
                                </p>
                            </div>
                        </div>

                        <div class="tools-output-column">
                            <h3 class="tools-subheading">Computed Body Weight &amp; Size</h3>

                            <div class="tools-result-cards">
                                <div class="tools-res-card highlight-card">
                                    <div class="res-card-header">
                                        <span class="res-card-label">FINAL AVERAGE BODY WEIGHT</span>
                                        <span class="wqi-metric-badge badge-optimal">Size 50</span>
                                    </div>
                                    <div class="res-value-row">
                                        <strong id="indiv-fabw-result" class="res-big-value res-accent-value">20.00</strong>
                                        <span class="res-unit">grams</span>
                                    </div>
                                    <div class="res-meal-breakdown">
                                        <span>Market Count: <strong id="indiv-fabw-count-per-kg">50.0 pcs / kg</strong></span>
                                        <span id="indiv-fabw-bulk-kg">1,700.00 kg total bulk</span>
                                    </div>
                                </div>

                                <div class="tools-res-card">
                                    <span class="res-card-label">STEP-BY-STEP SUBSTITUTION</span>
                                    <p class="res-card-detail" style="margin-top: 6px;">
                                        <code id="indiv-fabw-step-math">FABW = 1,700,000 g / 85,000 shrimp = 20.00 g</code>
                                    </p>
                                    <p class="res-card-detail" style="margin-top: 8px;">
                                        Consistent average weight indicates uniform feeding tray distribution and low size-depressing hierarchy competition in the pond.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                </article>
            </div>

            <!-- PANE 4: Eqs. 3 & 4 ADWG and SGR -->
            <div id="pane-growth-eq34" class="growth-tab-pane" role="tabpanel" aria-labelledby="tab-btn-eq34" hidden>
                <article class="panel dashboard-panel tools-calc-panel">

                    <div class="tools-panel-header">
                        <div class="panel-heading-icon tools-icon-biomass">
                            <svg class="ui-icon" aria-hidden="true">
                                <use href="#icon-chart"></use>
                            </svg>
                        </div>
                        <div>
                            <h2>Equations 3 &amp; 4: Daily Weight Gain (ADWG) &amp; Specific Growth Rate (SGR)</h2>
                            <p>Formulas: <code>ADWG = (FABW - IBW) / DOC</code> &bull; <code>SGR = [(ln FABW - ln IBW) / DOC] &times; 100</code></p>
                        </div>
                    </div>

                    <div class="tools-grid-split">
                        <div class="tools-input-column">
                            <h3 class="tools-subheading">Growth Trajectory Inputs</h3>

                            <div class="tools-form-grid">
                                <label class="tools-field-label" for="indiv-grow-ibw">
                                    <span class="field-label-text">Initial Body Weight (IBW)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-grow-ibw" min="0.001" max="10" step="0.005" value="0.010" placeholder="e.g. 0.010">
                                        <span class="input-unit">grams</span>
                                    </span>
                                </label>

                                <label class="tools-field-label" for="indiv-grow-fabw">
                                    <span class="field-label-text">Final Avg Body Weight (FABW)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-grow-fabw" min="0.1" max="60" step="0.1" value="20.00" placeholder="e.g. 20.00">
                                        <span class="input-unit">grams</span>
                                    </span>
                                </label>

                                <label class="tools-field-label" for="indiv-grow-doc" style="grid-column: span 2;">
                                    <span class="field-label-text">Days of Culture (DOC)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-grow-doc" min="1" max="365" step="1" value="90" placeholder="e.g. 90">
                                        <span class="input-unit">days</span>
                                    </span>
                                </label>
                            </div>

                            <div class="tools-callout-tip">
                                <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                                <p>
                                    <strong>Growth Velocities:</strong> ADWG evaluates linear daily increments (target: &ge;0.20 g/day for vannamei), while SGR measures exponential biological compounding (%/day) crucial for early nursery cycles.
                                </p>
                            </div>
                        </div>

                        <div class="tools-output-column">
                            <h3 class="tools-subheading">Computed Growth Velocities</h3>

                            <div class="tools-result-cards">
                                <div class="tools-res-card highlight-card">
                                    <div class="res-card-header">
                                        <span class="res-card-label">AVERAGE DAILY GAIN (ADWG)</span>
                                        <span id="indiv-adwg-badge" class="wqi-metric-badge badge-optimal">Optimal Growth</span>
                                    </div>
                                    <div class="res-value-row">
                                        <strong id="indiv-adwg-result" class="res-big-value res-accent-value">0.2221</strong>
                                        <span class="res-unit">g / day</span>
                                    </div>
                                    <div class="res-meal-breakdown">
                                        <span>Weekly Weight Gain: <strong id="indiv-adwg-weekly">1.555 g / week</strong></span>
                                        <span>Specific Growth: <strong id="indiv-sgr-result">8.445</strong> %/day</span>
                                    </div>
                                </div>

                                <div class="tools-res-card">
                                    <div class="res-card-header">
                                        <span class="res-card-label">SPECIFIC GROWTH RATE (SGR)</span>
                                        <span class="res-secondary-val">Biomass Multiplier: <strong id="indiv-sgr-mult">2,000&times;</strong></span>
                                    </div>
                                    <p class="res-card-detail">
                                        Eq. 3 (ADWG): <code id="indiv-adwg-step-math">(20.00 - 0.010) / 90 = 0.2221 g/day</code>
                                    </p>
                                    <p class="res-card-detail" style="margin-top: 6px;">
                                        Eq. 4 (SGR): <code id="indiv-sgr-step-math">[(ln 20.00 - ln 0.010) / 90] &times; 100 = 8.445%/day</code>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                </article>
            </div>

            <!-- PANE 5: Eqs. 5 & 6 BIOMASS (IB & FB) -->
            <div id="pane-growth-eq56" class="growth-tab-pane" role="tabpanel" aria-labelledby="tab-btn-eq56" hidden>
                <article class="panel dashboard-panel tools-calc-panel">

                    <div class="tools-panel-header">
                        <div class="panel-heading-icon tools-icon-biomass">
                            <svg class="ui-icon" aria-hidden="true">
                                <use href="#icon-dashboard"></use>
                            </svg>
                        </div>
                        <div>
                            <h2>Equations 5 &amp; 6: Initial &amp; Final Biomass (IB &amp; FB) Calculator</h2>
                            <p>Formulas: <code>IB = IS &times; IBW</code> &bull; <code>FB = LHC &times; FABW</code> &bull; Standing biological yield and pond gain.</p>
                        </div>
                    </div>

                    <div class="tools-grid-split">
                        <div class="tools-input-column">
                            <h3 class="tools-subheading">Biomass Multiplier Inputs</h3>

                            <div class="tools-form-grid">
                                <label class="tools-field-label" for="indiv-bio-is">
                                    <span class="field-label-text">Initial Stocking (IS)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-bio-is" min="1000" max="10000000" step="1000" value="100000">
                                        <span class="input-unit">shrimp</span>
                                    </span>
                                </label>

                                <label class="tools-field-label" for="indiv-bio-ibw">
                                    <span class="field-label-text">Initial Weight (IBW)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-bio-ibw" min="0.001" max="10" step="0.005" value="0.010">
                                        <span class="input-unit">grams</span>
                                    </span>
                                </label>

                                <label class="tools-field-label" for="indiv-bio-lhc">
                                    <span class="field-label-text">Live Harvest Count (LHC)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-bio-lhc" min="100" max="10000000" step="500" value="85000">
                                        <span class="input-unit">shrimp</span>
                                    </span>
                                </label>

                                <label class="tools-field-label" for="indiv-bio-fabw">
                                    <span class="field-label-text">Final Avg Weight (FABW)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-bio-fabw" min="0.1" max="60" step="0.1" value="20.00">
                                        <span class="input-unit">grams</span>
                                    </span>
                                </label>
                            </div>

                            <div class="tools-callout-tip">
                                <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                                <p>
                                    <strong>Biomass Conversion:</strong> Net gain ($FB - IB$) represents the true biological meat produced, which forms the denominator of the Feed Conversion Ratio (FCR).
                                </p>
                            </div>
                        </div>

                        <div class="tools-output-column">
                            <h3 class="tools-subheading">Standing Biomass Summary</h3>

                            <div class="tools-result-cards">
                                <div class="tools-res-card highlight-card">
                                    <div class="res-card-header">
                                        <span class="res-card-label">FINAL HARVEST BIOMASS (FB)</span>
                                        <span class="res-secondary-val">Initial: <span id="indiv-bio-ib-val">1.00 kg</span></span>
                                    </div>
                                    <div class="res-value-row">
                                        <strong id="indiv-bio-fb-val" class="res-big-value res-accent-value">1,700.00 kg</strong>
                                    </div>
                                    <div class="res-meal-breakdown">
                                        <span>Net Gain: <strong id="indiv-bio-gain-val">1,699.00 kg (1.70 metric tons)</strong></span>
                                        <span id="indiv-bio-fb-sub">(1,700,000 g)</span>
                                    </div>
                                </div>

                                <div class="tools-res-card">
                                    <span class="res-card-label">STEP-BY-STEP EQUATIONS</span>
                                    <p class="res-card-detail" style="margin-top: 6px;">
                                        Eq. 5 (IB): <code id="indiv-bio-ib-step">100,000 &times; 0.010 g = 1,000 g (1.00 kg)</code>
                                    </p>
                                    <p class="res-card-detail" style="margin-top: 6px;">
                                        Eq. 6 (FB): <code id="indiv-bio-fb-step">85,000 &times; 20.00 g = 1,700,000 g (1,700.00 kg)</code>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                </article>
            </div>

            <!-- PANE 6: Eq. 7 FEED CONVERSION RATIO (FCR) -->
            <div id="pane-growth-eq7" class="growth-tab-pane" role="tabpanel" aria-labelledby="tab-btn-eq7" hidden>
                <article class="panel dashboard-panel tools-calc-panel">

                    <div class="tools-panel-header">
                        <div class="panel-heading-icon tools-icon-carbon">
                            <svg class="ui-icon" aria-hidden="true">
                                <use href="#icon-calculator"></use>
                            </svg>
                        </div>
                        <div>
                            <h2>Equation 7: Feed Conversion Ratio (FCR) Calculator</h2>
                            <p>Formula: <code>FCR = TFG / (FB - IB)</code> &bull; Kilograms of feed required to produce 1 kilogram of shrimp biomass gain.</p>
                        </div>
                    </div>

                    <div class="tools-grid-split">
                        <div class="tools-input-column">
                            <h3 class="tools-subheading">Feed &amp; Yield Parameters</h3>

                            <div class="tools-form-grid">
                                <label class="tools-field-label" for="indiv-fcr-tfg">
                                    <span class="field-label-text">Total Feed Given (TFG)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-fcr-tfg" min="1" max="1000000" step="25" value="2125">
                                        <span class="input-unit">kg</span>
                                    </span>
                                    <input type="hidden" id="indiv-fcr-tfg-unit" value="kg">
                                </label>

                                <label class="tools-field-label" for="indiv-fcr-fb">
                                    <span class="field-label-text">Final Biomass (FB)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-fcr-fb" min="1" max="1000000" step="25" value="1700">
                                        <span class="input-unit">kg</span>
                                    </span>
                                </label>

                                <label class="tools-field-label" for="indiv-fcr-ib" style="grid-column: span 2;">
                                    <span class="field-label-text">Initial Biomass (IB)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-fcr-ib" min="0.01" max="50000" step="0.5" value="1.00">
                                        <span class="input-unit">kg</span>
                                    </span>
                                </label>
                            </div>

                            <div class="tools-callout-tip">
                                <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                                <p>
                                    <strong>Commercial Efficiency Standard:</strong> Target FCR for commercial <em>P. vannamei</em> ranges between 1.20 and 1.50. Lower FCR reduces nitrogen waste, keeps water quality stable, and maximizes profitability.
                                </p>
                            </div>
                        </div>

                        <div class="tools-output-column">
                            <h3 class="tools-subheading">Computed Feed Conversion</h3>

                            <div class="tools-result-cards">
                                <div class="tools-res-card highlight-card">
                                    <div class="res-card-header">
                                        <span class="res-card-label">COMPUTED FEED CONVERSION RATIO</span>
                                        <span id="indiv-fcr-badge" class="wqi-metric-badge badge-optimal">Optimal</span>
                                    </div>
                                    <div class="res-value-row">
                                        <strong id="indiv-fcr-result" class="res-big-value res-accent-value">1.251</strong>
                                        <span class="res-unit">FCR</span>
                                    </div>
                                    <div class="res-meal-breakdown">
                                        <span>Feed Efficiency: <strong id="indiv-fcr-efficiency">79.95%</strong></span>
                                        <span>Biomass Gain: <strong id="indiv-fcr-gain-desc">1,699.00 kg</strong></span>
                                    </div>
                                </div>

                                <div class="tools-res-card">
                                    <span class="res-card-label">STEP-BY-STEP SUBSTITUTION</span>
                                    <p class="res-card-detail" style="margin-top: 6px;">
                                        <code id="indiv-fcr-step-math">FCR = 2,125.0 kg / (1,700.0 - 1.0) kg = 1.251</code>
                                    </p>
                                    <p id="indiv-fcr-rating" class="res-card-detail" style="margin-top: 8px;">
                                        Standard target commercial FCR (1.20&ndash;1.50) for Penaeus vannamei culture. Minimal feed wastage with excellent assimilation.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                </article>
            </div>

            <!-- PANE 7: Eq. 8 FULTON'S CONDITION FACTOR (K) -->
            <div id="pane-growth-eq8" class="growth-tab-pane" role="tabpanel" aria-labelledby="tab-btn-eq8" hidden>
                <article class="panel dashboard-panel tools-calc-panel">

                    <div class="tools-panel-header">
                        <div class="panel-heading-icon tools-icon-biomass">
                            <svg class="ui-icon" aria-hidden="true">
                                <use href="#icon-settings"></use>
                            </svg>
                        </div>
                        <div>
                            <h2>Equation 8: Fulton's Condition Factor (K) Calculator</h2>
                            <p>Formula: <code>K = (FABW / TL&sup3;) &times; 100</code> &bull; Morphometric assessment of shrimp robust girth and muscle density.</p>
                        </div>
                    </div>

                    <div class="tools-grid-split">
                        <div class="tools-input-column">
                            <h3 class="tools-subheading">Weight &amp; Length Inputs</h3>

                            <div class="tools-form-grid">
                                <label class="tools-field-label" for="indiv-k-fabw">
                                    <span class="field-label-text">Final Avg Body Weight (FABW)</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-k-fabw" min="0.1" max="100" step="0.1" value="20.00">
                                        <span class="input-unit">grams</span>
                                    </span>
                                </label>

                                <label class="tools-field-label" for="indiv-k-tl">
                                    <span class="field-label-text">Total Length (TL) - Rostrum to Telson</span>
                                    <span class="dashboard-field-wrap">
                                        <input type="number" id="indiv-k-tl" min="1.0" max="35.0" step="0.1" value="12.9">
                                        <span class="input-unit">cm</span>
                                    </span>
                                </label>
                            </div>

                            <div class="tools-callout-tip">
                                <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                                <p>
                                    <strong>Fulton's Index:</strong> Fulton's factor $K$ between 0.80 and 1.15 is the ideal biological index for healthy commercial <em>Penaeus vannamei</em>, denoting dense muscle tissue, full tail meat filling, and healthy exoskeleton development.
                                </p>
                            </div>
                        </div>

                        <div class="tools-output-column">
                            <h3 class="tools-subheading">Condition Evaluation</h3>

                            <div class="tools-result-cards">
                                <div class="tools-res-card highlight-card">
                                    <div class="res-card-header">
                                        <span class="res-card-label">FULTON'S CONDITION FACTOR</span>
                                        <span id="indiv-k-badge" class="wqi-metric-badge badge-optimal">Optimal Condition</span>
                                    </div>
                                    <div class="res-value-row">
                                        <strong id="indiv-k-result" class="res-big-value res-accent-value">0.9317</strong>
                                        <span class="res-unit">K factor</span>
                                    </div>
                                    <div class="res-meal-breakdown">
                                        <span>Target Range: <strong>0.80 &ndash; 1.15 K</strong></span>
                                        <span>Assessment: <strong id="indiv-k-summary">Robust &amp; Well-proportioned</strong></span>
                                    </div>
                                </div>

                                <div class="tools-res-card">
                                    <span class="res-card-label">STEP-BY-STEP SUBSTITUTION</span>
                                    <p class="res-card-detail" style="margin-top: 6px;">
                                        <code id="indiv-k-step-math">K = (20.00 / 12.9&sup3;) &times; 100 = 0.9317</code>
                                    </p>
                                    <p id="indiv-k-rating" class="res-card-detail" style="margin-top: 8px;">
                                        Well-proportioned, robust body condition characteristic of healthy Penaeus vannamei with firm muscle texture.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                </article>
            </div>

        </section>
'''

def update_templates():
    with open('templates/calculators.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find start and end of Section 2 in calculators.html
    s2_start = '<!-- 2. SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE CALCULATORS'
    s3_start = '<!-- 3. WATER TREATMENT & DOSING CALCULATORS -->'

    idx_start = content.find(s2_start)
    idx_end = content.find(s3_start)

    if idx_start == -1 or idx_end == -1:
        print(f"Error finding markers: start={idx_start}, end={idx_end}")
        return False

    new_content = content[:idx_start] + uniform_section2_html + '\n\n\n        ' + content[idx_end:]

    with open('templates/calculators.html', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("Successfully updated templates/calculators.html with uniform Section 2!")
    return True

if __name__ == '__main__':
    update_templates()

