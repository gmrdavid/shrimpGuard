# -*- coding: utf-8 -*-
"""
Script to update templates/calculators.html with Section 2:
Shrimp Growth & Zootechnical Performance Calculators (Eqs. 1-8).
"""
import sys

section2_html = '''
        <!-- 2. SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE CALCULATORS (Eqs. 1–8) -->
        <section class="dashboard-section growth-section" id="tools-growth-section" aria-labelledby="growth-calculators-title">

            <div class="section-heading-row">
                <div>
                    <span class="section-eyebrow">ZOOTECHNICAL EQUATIONS &bull; PENAEUS VANNAMEI PERFORMANCE</span>
                    <h2 id="growth-calculators-title">Shrimp Growth &amp; Zootechnical Performance Calculators (Eqs. 1–8)</h2>
                    <p>Standard scientific aquaculture growth performance, biomass conversion, and Fulton's condition factor equations based on commercial vannamei research models.</p>
                </div>
                <div class="growth-header-pills">
                    <span class="section-count">8 scientific equations</span>
                </div>
            </div>

            <!-- Tab Navigation Bar for Master Engine vs Individual Calculators -->
            <div class="growth-tabs-bar" role="tablist" aria-label="Growth Equations Tabs">
                <button type="button" class="growth-tab-item active" role="tab" id="tab-btn-master" aria-selected="true" aria-controls="pane-growth-master" data-pane="master">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-calculator"></use></svg>
                    <span>All-in-One Master Engine</span>
                    <span class="growth-tab-tag">Eqs. 1–8</span>
                </button>
                <button type="button" class="growth-tab-item" role="tab" id="tab-btn-eq1" aria-selected="false" aria-controls="pane-growth-eq1" data-pane="eq1">
                    <span>Eq. 1: Survival (SR)</span>
                </button>
                <button type="button" class="growth-tab-item" role="tab" id="tab-btn-eq2" aria-selected="false" aria-controls="pane-growth-eq2" data-pane="eq2">
                    <span>Eq. 2: Body Weight (FABW)</span>
                </button>
                <button type="button" class="growth-tab-item" role="tab" id="tab-btn-eq34" aria-selected="false" aria-controls="pane-growth-eq34" data-pane="eq34">
                    <span>Eqs. 3–4: ADWG &amp; SGR</span>
                </button>
                <button type="button" class="growth-tab-item" role="tab" id="tab-btn-eq56" aria-selected="false" aria-controls="pane-growth-eq56" data-pane="eq56">
                    <span>Eqs. 5–6: Biomass (IB &amp; FB)</span>
                </button>
                <button type="button" class="growth-tab-item" role="tab" id="tab-btn-eq7" aria-selected="false" aria-controls="pane-growth-eq7" data-pane="eq7">
                    <span>Eq. 7: Feed Conversion (FCR)</span>
                </button>
                <button type="button" class="growth-tab-item" role="tab" id="tab-btn-eq8" aria-selected="false" aria-controls="pane-growth-eq8" data-pane="eq8">
                    <span>Eq. 8: Fulton's Condition (K)</span>
                </button>
            </div>

            <!-- PANE 1: MASTER UNIFIED ENGINE (Eqs. 1–8) -->
            <div id="pane-growth-master" class="growth-tab-pane active" role="tabpanel" aria-labelledby="tab-btn-master">
                <article class="panel dashboard-panel growth-master-panel">
                    <div class="growth-pane-header">
                        <div class="growth-pane-title-group">
                            <span class="growth-card-badge">UNIFIED ZOOTECHNICAL MODEL</span>
                            <h3>All-in-One Growth &amp; Production Performance Engine</h3>
                            <p>Compute all 8 equations simultaneously from pond stocking records, harvest data, feed totals, and morphometric measurements.</p>
                        </div>
                        <div class="growth-preset-group">
                            <span class="growth-preset-label">LOAD PRESETS:</span>
                            <button type="button" class="btn-preset-growth active" data-preset="commercial" title="Load typical 90-day commercial harvest dataset">Commercial 90d</button>
                            <button type="button" class="btn-preset-growth" data-preset="intensive" title="Load high-density 75-day intensive harvest dataset">Intensive 75d</button>
                            <button type="button" class="btn-preset-growth" data-preset="nursery" title="Load 30-day early nursery dataset">Nursery 30d</button>
                            <button type="button" id="btn-sync-from-biomass" class="btn-preset-sync" title="Sync live population and ABW values from Biomass Section above">
                                <svg class="ui-icon" aria-hidden="true"><use href="#icon-history"></use></svg>
                                <span>Sync Biomass Tool</span>
                            </button>
                        </div>
                    </div>

                    <div class="growth-master-layout">
                        <!-- Inputs Column -->
                        <div class="growth-master-inputs">
                            <h4 class="growth-input-col-title">Primary Pond Parameters</h4>

                            <div class="growth-field-grid">
                                <div class="tools-field-group">
                                    <label class="tools-field-label" for="gm-initial-stocking">
                                        <span class="field-label-text">Initial Stocking (IS)</span>
                                        <span class="field-hint">Post-larvae stocked (pcs)</span>
                                    </label>
                                    <div class="tools-input-wrap">
                                        <input type="number" id="gm-initial-stocking" min="1000" max="5000000" step="1000" value="100000">
                                        <span class="input-unit">shrimp</span>
                                    </div>
                                </div>

                                <div class="tools-field-group">
                                    <label class="tools-field-label" for="gm-live-harvest-count">
                                        <span class="field-label-text">Live Harvest Count (LHC)</span>
                                        <span class="field-hint">Live shrimp harvested (pcs)</span>
                                    </label>
                                    <div class="tools-input-wrap">
                                        <input type="number" id="gm-live-harvest-count" min="100" max="5000000" step="500" value="85000">
                                        <span class="input-unit">shrimp</span>
                                    </div>
                                </div>

                                <div class="tools-field-group">
                                    <label class="tools-field-label" for="gm-days-of-culture">
                                        <span class="field-label-text">Days of Culture (DOC)</span>
                                        <span class="field-hint">Culture duration (days)</span>
                                    </label>
                                    <div class="tools-input-wrap">
                                        <input type="number" id="gm-days-of-culture" min="1" max="365" step="1" value="90">
                                        <span class="input-unit">days</span>
                                    </div>
                                </div>

                                <div class="tools-field-group">
                                    <label class="tools-field-label" for="gm-initial-weight">
                                        <span class="field-label-text">Initial Body Weight (IBW)</span>
                                        <span class="field-hint">Weight at stocking (g)</span>
                                    </label>
                                    <div class="tools-input-wrap">
                                        <input type="number" id="gm-initial-weight" min="0.001" max="10" step="0.005" value="0.010">
                                        <span class="input-unit">grams</span>
                                    </div>
                                </div>

                                <div class="tools-field-group">
                                    <label class="tools-field-label" for="gm-bulk-weight">
                                        <span class="field-label-text">Harvest Bulk Weight (BW)</span>
                                        <span class="field-hint">Total harvested mass</span>
                                    </label>
                                    <div class="tools-input-wrap">
                                        <input type="number" id="gm-bulk-weight" min="10" max="500000" step="10" value="1700">
                                        <select id="gm-bw-unit" class="input-unit-select" aria-label="Bulk weight unit">
                                            <option value="kg" selected>kg</option>
                                            <option value="g">grams</option>
                                        </select>
                                    </div>
                                </div>

                                <div class="tools-field-group">
                                    <label class="tools-field-label" for="gm-total-feed">
                                        <span class="field-label-text">Total Feed Given (TFG)</span>
                                        <span class="field-hint">Cumulative feed input</span>
                                    </label>
                                    <div class="tools-input-wrap">
                                        <input type="number" id="gm-total-feed" min="10" max="500000" step="25" value="2125">
                                        <select id="gm-feed-unit" class="input-unit-select" aria-label="Feed weight unit">
                                            <option value="kg" selected>kg</option>
                                            <option value="g">grams</option>
                                        </select>
                                    </div>
                                </div>

                                <div class="tools-field-group">
                                    <label class="tools-field-label" for="gm-total-length">
                                        <span class="field-label-text">Total Length (TL)</span>
                                        <span class="field-hint">Rostrum tip to telson end (cm)</span>
                                    </label>
                                    <div class="tools-input-wrap">
                                        <input type="number" id="gm-total-length" min="1.0" max="30.0" step="0.1" value="12.9">
                                        <span class="input-unit">cm</span>
                                    </div>
                                </div>
                            </div>

                            <button type="button" id="gm-btn-calculate" class="growth-btn-compute">
                                <svg class="ui-icon" aria-hidden="true"><use href="#icon-calculator"></use></svg>
                                <span>Recompute All Equations (1–8)</span>
                            </button>
                        </div>

                        <!-- Results Dashboard Grid -->
                        <div class="growth-master-results">
                            <h4 class="growth-input-col-title">Computed Performance Metrics</h4>

                            <div class="growth-cards-grid">
                                <!-- Card 1: Survival Rate -->
                                <div class="growth-result-card" data-eq="1">
                                    <div class="growth-res-top">
                                        <span class="growth-eq-badge">Eq. 1</span>
                                        <span class="growth-res-label">SURVIVAL RATE (SR)</span>
                                        <span id="gm-res-sr-badge" class="wqi-metric-badge badge-optimal">Optimal</span>
                                    </div>
                                    <div class="growth-res-main">
                                        <span id="gm-res-sr-val" class="growth-res-number">85.00</span>
                                        <span class="growth-res-unit">%</span>
                                    </div>
                                    <div class="growth-res-sub">
                                        <span>Mortality: <strong id="gm-res-mortality-count">15,000</strong> shrimp (<span id="gm-res-mortality-pct">15.00%</span>)</span>
                                    </div>
                                    <div class="growth-res-formula">
                                        <code>SR = (LHC / IS) &times; 100</code>
                                        <div id="gm-sub-sr" class="growth-formula-sub">(85,000 / 100,000) &times; 100 = 85.00%</div>
                                    </div>
                                </div>

                                <!-- Card 2: Final Average Body Weight -->
                                <div class="growth-result-card" data-eq="2">
                                    <div class="growth-res-top">
                                        <span class="growth-eq-badge">Eq. 2</span>
                                        <span class="growth-res-label">FINAL AVG BODY WEIGHT (FABW)</span>
                                        <span class="growth-sub-badge">Commercial Size</span>
                                    </div>
                                    <div class="growth-res-main">
                                        <span id="gm-res-fabw-val" class="growth-res-number">20.00</span>
                                        <span class="growth-res-unit">g / shrimp</span>
                                    </div>
                                    <div class="growth-res-sub">
                                        <span>Harvest Count: <strong id="gm-res-count-per-kg">50.0</strong> pcs / kg</span>
                                    </div>
                                    <div class="growth-res-formula">
                                        <code>FABW = BW / LHC</code>
                                        <div id="gm-sub-fabw" class="growth-formula-sub">1,700,000 g / 85,000 = 20.00 g</div>
                                    </div>
                                </div>

                                <!-- Card 3: Average Daily Weight Gain -->
                                <div class="growth-result-card" data-eq="3">
                                    <div class="growth-res-top">
                                        <span class="growth-eq-badge">Eq. 3</span>
                                        <span class="growth-res-label">AVG DAILY WEIGHT GAIN (ADWG)</span>
                                        <span id="gm-res-adwg-badge" class="wqi-metric-badge badge-optimal">Optimal Growth</span>
                                    </div>
                                    <div class="growth-res-main">
                                        <span id="gm-res-adwg-val" class="growth-res-number">0.2221</span>
                                        <span class="growth-res-unit">g / day</span>
                                    </div>
                                    <div class="growth-res-sub">
                                        <span>Weekly Gain: <strong id="gm-res-weekly-gain">1.555</strong> g / week</span>
                                    </div>
                                    <div class="growth-res-formula">
                                        <code>ADWG = (FABW - IBW) / DOC</code>
                                        <div id="gm-sub-adwg" class="growth-formula-sub">(20.00 - 0.010) / 90 = 0.2221 g/day</div>
                                    </div>
                                </div>

                                <!-- Card 4: Specific Growth Rate -->
                                <div class="growth-result-card" data-eq="4">
                                    <div class="growth-res-top">
                                        <span class="growth-eq-badge">Eq. 4</span>
                                        <span class="growth-res-label">SPECIFIC GROWTH RATE (SGR)</span>
                                        <span class="growth-sub-badge">Exponential Rate</span>
                                    </div>
                                    <div class="growth-res-main">
                                        <span id="gm-res-sgr-val" class="growth-res-number">8.445</span>
                                        <span class="growth-res-unit">% / day</span>
                                    </div>
                                    <div class="growth-res-sub">
                                        <span>Total Weight Multiplication: <strong id="gm-res-weight-mult">2,000&times;</strong></span>
                                    </div>
                                    <div class="growth-res-formula">
                                        <code>SGR = ((ln FABW - ln IBW) / DOC) &times; 100</code>
                                        <div id="gm-sub-sgr" class="growth-formula-sub">((ln 20.00 - ln 0.010) / 90) &times; 100 = 8.445%</div>
                                    </div>
                                </div>

                                <!-- Card 5 & 6: Biomass Conversion -->
                                <div class="growth-result-card" data-eq="5-6">
                                    <div class="growth-res-top">
                                        <span class="growth-eq-badge">Eqs. 5 &amp; 6</span>
                                        <span class="growth-res-label">POND BIOMASS (IB &amp; FB)</span>
                                        <span class="growth-sub-badge">Standing Mass</span>
                                    </div>
                                    <div class="growth-biomass-split">
                                        <div>
                                            <span class="biomass-sub-label">INITIAL (IB):</span>
                                            <strong id="gm-res-ib-kg">1.00</strong> kg
                                        </div>
                                        <div class="biomass-arrow">&rarr;</div>
                                        <div>
                                            <span class="biomass-sub-label">FINAL (FB):</span>
                                            <strong id="gm-res-fb-kg">1,700.00</strong> kg
                                        </div>
                                    </div>
                                    <div class="growth-res-sub">
                                        <span>Net Biomass Yield Gain: <strong id="gm-res-net-biomass">1,699.00</strong> kg</span>
                                    </div>
                                    <div class="growth-res-formula">
                                        <code>IB = IS &times; IBW &nbsp;|&nbsp; FB = LHC &times; FABW</code>
                                        <div id="gm-sub-biomass" class="growth-formula-sub">Gain: 1,700.00 kg - 1.00 kg = 1,699.00 kg</div>
                                    </div>
                                </div>

                                <!-- Card 7: Feed Conversion Ratio -->
                                <div class="growth-result-card" data-eq="7">
                                    <div class="growth-res-top">
                                        <span class="growth-eq-badge">Eq. 7</span>
                                        <span class="growth-res-label">FEED CONVERSION RATIO (FCR)</span>
                                        <span id="gm-res-fcr-badge" class="wqi-metric-badge badge-optimal">Optimal</span>
                                    </div>
                                    <div class="growth-res-main">
                                        <span id="gm-res-fcr-val" class="growth-res-number">1.251</span>
                                        <span class="growth-res-unit">ratio</span>
                                    </div>
                                    <div class="growth-res-sub">
                                        <span>Feed Efficiency: <strong id="gm-res-feed-efficiency">79.95%</strong> (Gain / Feed)</span>
                                    </div>
                                    <div class="growth-res-formula">
                                        <code>FCR = TFG / (FB - IB)</code>
                                        <div id="gm-sub-fcr" class="growth-formula-sub">2,125.0 kg / 1,699.00 kg = 1.251</div>
                                    </div>
                                </div>

                                <!-- Card 8: Fulton's Condition Factor -->
                                <div class="growth-result-card" data-eq="8">
                                    <div class="growth-res-top">
                                        <span class="growth-eq-badge">Eq. 8</span>
                                        <span class="growth-res-label">FULTON'S CONDITION FACTOR (K)</span>
                                        <span id="gm-res-k-badge" class="wqi-metric-badge badge-optimal">Optimal Condition</span>
                                    </div>
                                    <div class="growth-res-main">
                                        <span id="gm-res-k-val" class="growth-res-number">0.9317</span>
                                        <span class="growth-res-unit">K factor</span>
                                    </div>
                                    <div class="growth-res-sub">
                                        <span>Body Profile: <strong id="gm-res-k-profile">Healthy, well-proportioned robust girth</strong></span>
                                    </div>
                                    <div class="growth-res-formula">
                                        <code>K = (FABW / TL&sup3;) &times; 100</code>
                                        <div id="gm-sub-k" class="growth-formula-sub">(20.00 / 12.9&sup3;) &times; 100 = 0.9317</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Equations Reference Footnote -->
                    <div class="growth-reference-strip">
                        <div class="growth-ref-icon">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-alert"></use></svg>
                        </div>
                        <div class="growth-ref-text">
                            <strong>Scientific Aquaculture Protocol:</strong> These 8 zootechnical equations conform to peer-reviewed growth performance modeling for <em>Penaeus vannamei</em> culture. Variables: <em>SR</em> = Survival rate (%), <em>LHC</em> = Live harvest count, <em>IS</em> = Initial stocking, <em>FABW</em> = Final average body weight (g), <em>BW</em> = Bulk weight (g), <em>ADWG</em> = Average daily weight gain (g/day), <em>IBW</em> = Initial body weight (g), <em>DOC</em> = Day of culture (day), <em>SGR</em> = Specific growth rate (%/day), <em>IB</em> = Initial biomass (g), <em>FB</em> = Final biomass (g), <em>FCR</em> = Feed conversion ratio, <em>TFG</em> = Total feed given (g), <em>K</em> = Fulton's body condition factor, <em>TL</em> = Total length (cm).
                        </div>
                    </div>
                </article>
            </div>

            <!-- PANE 2: Eq. 1 SURVIVAL RATE (SR) -->
            <div id="pane-growth-eq1" class="growth-tab-pane" role="tabpanel" aria-labelledby="tab-btn-eq1" hidden>
                <article class="panel dashboard-panel individual-growth-panel">
                    <div class="tools-panel-header">
                        <div class="panel-heading-icon tools-icon-biomass">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-monitor"></use></svg>
                        </div>
                        <div>
                            <h2>Equation 1: Survival Rate (SR) Calculator</h2>
                            <p>Computes the percentage of stocked post-larvae that survive until final harvest.</p>
                        </div>
                    </div>

                    <div class="indiv-calc-grid">
                        <div class="indiv-calc-inputs">
                            <div class="math-eq-banner">
                                <span class="math-eq-tag">FORMULA</span>
                                <code>SR = (LHC / IS) &times; 100</code>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-is">
                                    <span class="field-label-text">Initial Stocking (IS)</span>
                                    <span class="field-hint">Total number of post-larvae stocked into the pond</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-is" min="1000" max="10000000" step="1000" value="100000">
                                    <span class="input-unit">shrimp</span>
                                </div>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-lhc">
                                    <span class="field-label-text">Live Harvest Count (LHC)</span>
                                    <span class="field-hint">Actual count or sampled estimation of live harvested shrimp</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-lhc" min="100" max="10000000" step="500" value="85000">
                                    <span class="input-unit">shrimp</span>
                                </div>
                            </div>

                            <button type="button" id="btn-calc-eq1" class="growth-btn-compute">
                                <span>Compute Survival Rate</span>
                            </button>
                        </div>

                        <div class="indiv-calc-results">
                            <div class="indiv-res-box">
                                <span class="res-card-label">COMPUTED SURVIVAL RATE (SR)</span>
                                <div class="indiv-big-stat">
                                    <strong id="indiv-sr-result">85.00</strong>
                                    <span class="stat-unit">%</span>
                                    <span id="indiv-sr-badge" class="wqi-metric-badge badge-optimal">Optimal</span>
                                </div>
                                <div class="indiv-breakdown">
                                    <div class="indiv-stat-row">
                                        <span>Estimated Mortality Count:</span>
                                        <strong id="indiv-sr-mortality-count">15,000 shrimp</strong>
                                    </div>
                                    <div class="indiv-stat-row">
                                        <span>Cumulative Mortality:</span>
                                        <strong id="indiv-sr-mortality-pct">15.00%</strong>
                                    </div>
                                </div>
                            </div>

                            <div class="step-math-box">
                                <span class="step-math-title">Step-by-Step Calculation</span>
                                <div class="step-row">
                                    <span>Formula Substitution:</span>
                                    <code id="indiv-sr-step-math">SR = (85,000 / 100,000) &times; 100 = 85.00%</code>
                                </div>
                                <p id="indiv-sr-rating" class="treatment-instruction">
                                    Optimal survival rate exceeding typical commercial benchmark (&ge;80%). Favorable water quality and healthy nursery transition.
                                </p>
                            </div>
                        </div>
                    </div>
                </article>
            </div>

            <!-- PANE 3: Eq. 2 FINAL AVERAGE BODY WEIGHT (FABW) -->
            <div id="pane-growth-eq2" class="growth-tab-pane" role="tabpanel" aria-labelledby="tab-btn-eq2" hidden>
                <article class="panel dashboard-panel individual-growth-panel">
                    <div class="tools-panel-header">
                        <div class="panel-heading-icon tools-icon-biomass">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-calculator"></use></svg>
                        </div>
                        <div>
                            <h2>Equation 2: Final Average Body Weight (FABW) Calculator</h2>
                            <p>Determines average individual shrimp weight from total harvested bulk weight and population count.</p>
                        </div>
                    </div>

                    <div class="indiv-calc-grid">
                        <div class="indiv-calc-inputs">
                            <div class="math-eq-banner">
                                <span class="math-eq-tag">FORMULA</span>
                                <code>FABW = BW / LHC</code>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-bw">
                                    <span class="field-label-text">Bulk Weight (BW)</span>
                                    <span class="field-hint">Total harvested mass of all shrimp</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-bw" min="1" max="1000000" step="10" value="1700">
                                    <select id="indiv-bw-unit" class="input-unit-select" aria-label="Bulk weight unit">
                                        <option value="kg" selected>kg</option>
                                        <option value="g">grams</option>
                                    </select>
                                </div>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-fabw-lhc">
                                    <span class="field-label-text">Live Harvest Count (LHC)</span>
                                    <span class="field-hint">Total live shrimp harvested</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-fabw-lhc" min="100" max="10000000" step="500" value="85000">
                                    <span class="input-unit">shrimp</span>
                                </div>
                            </div>

                            <button type="button" id="btn-calc-eq2" class="growth-btn-compute">
                                <span>Compute Average Body Weight</span>
                            </button>
                        </div>

                        <div class="indiv-calc-results">
                            <div class="indiv-res-box">
                                <span class="res-card-label">FINAL AVERAGE BODY WEIGHT (FABW)</span>
                                <div class="indiv-big-stat">
                                    <strong id="indiv-fabw-result">20.00</strong>
                                    <span class="stat-unit">grams</span>
                                    <span class="wqi-metric-badge badge-optimal">Standard Harvest</span>
                                </div>
                                <div class="indiv-breakdown">
                                    <div class="indiv-stat-row">
                                        <span>Commercial Shrimp Count:</span>
                                        <strong id="indiv-fabw-count-per-kg">50.0 pcs / kg</strong>
                                    </div>
                                    <div class="indiv-stat-row">
                                        <span>Total Bulk Biomass:</span>
                                        <strong id="indiv-fabw-bulk-kg">1,700.00 kg (1,700,000 g)</strong>
                                    </div>
                                </div>
                            </div>

                            <div class="step-math-box">
                                <span class="step-math-title">Step-by-Step Calculation</span>
                                <div class="step-row">
                                    <span>Formula Substitution:</span>
                                    <code id="indiv-fabw-step-math">FABW = 1,700,000 g / 85,000 shrimp = 20.00 g</code>
                                </div>
                                <p class="treatment-instruction">
                                    20.00 g corresponds to size 50 shrimp count (50 pieces per kilogram), typical for high-value commercial vannamei sales.
                                </p>
                            </div>
                        </div>
                    </div>
                </article>
            </div>

            <!-- PANE 4: Eqs. 3 & 4 ADWG and SGR -->
            <div id="pane-growth-eq34" class="growth-tab-pane" role="tabpanel" aria-labelledby="tab-btn-eq34" hidden>
                <article class="panel dashboard-panel individual-growth-panel">
                    <div class="tools-panel-header">
                        <div class="panel-heading-icon tools-icon-biomass">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                        </div>
                        <div>
                            <h2>Equations 3 &amp; 4: Daily Weight Gain (ADWG) &amp; Specific Growth Rate (SGR)</h2>
                            <p>Evaluates linear growth velocity (g/day) and logarithmic biological compounding (%/day).</p>
                        </div>
                    </div>

                    <div class="indiv-calc-grid">
                        <div class="indiv-calc-inputs">
                            <div class="math-eq-banner">
                                <span class="math-eq-tag">FORMULAS</span>
                                <code>ADWG = (FABW - IBW) / DOC &nbsp;|&nbsp; SGR = [(ln FABW - ln IBW) / DOC] &times; 100</code>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-grow-ibw">
                                    <span class="field-label-text">Initial Body Weight (IBW)</span>
                                    <span class="field-hint">Weight at nursery release / stocking (grams)</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-grow-ibw" min="0.001" max="10" step="0.005" value="0.010">
                                    <span class="input-unit">grams</span>
                                </div>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-grow-fabw">
                                    <span class="field-label-text">Final Average Body Weight (FABW)</span>
                                    <span class="field-hint">Harvest or current sampled body weight (grams)</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-grow-fabw" min="0.1" max="60" step="0.1" value="20.00">
                                    <span class="input-unit">grams</span>
                                </div>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-grow-doc">
                                    <span class="field-label-text">Days of Culture (DOC)</span>
                                    <span class="field-hint">Elapsed culture time in days</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-grow-doc" min="1" max="365" step="1" value="90">
                                    <span class="input-unit">days</span>
                                </div>
                            </div>

                            <button type="button" id="btn-calc-eq34" class="growth-btn-compute">
                                <span>Compute Growth Rates</span>
                            </button>
                        </div>

                        <div class="indiv-calc-results">
                            <div class="growth-dual-grid">
                                <div class="indiv-res-box">
                                    <span class="res-card-label">AVERAGE DAILY GAIN (ADWG)</span>
                                    <div class="indiv-big-stat">
                                        <strong id="indiv-adwg-result">0.2221</strong>
                                        <span class="stat-unit">g / day</span>
                                    </div>
                                    <span id="indiv-adwg-badge" class="wqi-metric-badge badge-optimal">Optimal Growth</span>
                                    <div class="indiv-stat-row" style="margin-top: 10px;">
                                        <span>Weekly Weight Gain:</span>
                                        <strong id="indiv-adwg-weekly">1.555 g / week</strong>
                                    </div>
                                </div>

                                <div class="indiv-res-box">
                                    <span class="res-card-label">SPECIFIC GROWTH RATE (SGR)</span>
                                    <div class="indiv-big-stat">
                                        <strong id="indiv-sgr-result">8.445</strong>
                                        <span class="stat-unit">% / day</span>
                                    </div>
                                    <span class="growth-sub-badge">Logarithmic Velocity</span>
                                    <div class="indiv-stat-row" style="margin-top: 10px;">
                                        <span>Relative Biomass Multiplication:</span>
                                        <strong id="indiv-sgr-mult">2,000&times;</strong>
                                    </div>
                                </div>
                            </div>

                            <div class="step-math-box">
                                <span class="step-math-title">Step-by-Step Substitution</span>
                                <div class="step-row">
                                    <span>Eq. 3 (ADWG):</span>
                                    <code id="indiv-adwg-step-math">(20.00 - 0.010) / 90 = 0.2221 g/day</code>
                                </div>
                                <div class="step-row">
                                    <span>Eq. 4 (SGR):</span>
                                    <code id="indiv-sgr-step-math">[(ln 20.00 - ln 0.010) / 90] &times; 100 = 8.445%/day</code>
                                </div>
                            </div>
                        </div>
                    </div>
                </article>
            </div>

            <!-- PANE 5: Eqs. 5 & 6 BIOMASS (IB & FB) -->
            <div id="pane-growth-eq56" class="growth-tab-pane" role="tabpanel" aria-labelledby="tab-btn-eq56" hidden>
                <article class="panel dashboard-panel individual-growth-panel">
                    <div class="tools-panel-header">
                        <div class="panel-heading-icon tools-icon-biomass">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-dashboard"></use></svg>
                        </div>
                        <div>
                            <h2>Equations 5 &amp; 6: Initial &amp; Final Biomass (IB &amp; FB) Calculator</h2>
                            <p>Computes total standing biological biomass at stocking and harvest, plus net pond biomass gain.</p>
                        </div>
                    </div>

                    <div class="indiv-calc-grid">
                        <div class="indiv-calc-inputs">
                            <div class="math-eq-banner">
                                <span class="math-eq-tag">FORMULAS</span>
                                <code>IB = IS &times; IBW &nbsp;|&nbsp; FB = LHC &times; FABW</code>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-bio-is">
                                    <span class="field-label-text">Initial Stocking (IS)</span>
                                    <span class="field-hint">Post-larvae stocked (pcs)</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-bio-is" min="1000" max="10000000" step="1000" value="100000">
                                    <span class="input-unit">shrimp</span>
                                </div>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-bio-ibw">
                                    <span class="field-label-text">Initial Body Weight (IBW)</span>
                                    <span class="field-hint">Stocking weight per shrimp (g)</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-bio-ibw" min="0.001" max="10" step="0.005" value="0.010">
                                    <span class="input-unit">grams</span>
                                </div>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-bio-lhc">
                                    <span class="field-label-text">Live Harvest Count (LHC)</span>
                                    <span class="field-hint">Shrimp harvested (pcs)</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-bio-lhc" min="100" max="10000000" step="500" value="85000">
                                    <span class="input-unit">shrimp</span>
                                </div>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-bio-fabw">
                                    <span class="field-label-text">Final Avg Body Weight (FABW)</span>
                                    <span class="field-hint">Harvest weight per shrimp (g)</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-bio-fabw" min="0.1" max="60" step="0.1" value="20.00">
                                    <span class="input-unit">grams</span>
                                </div>
                            </div>

                            <button type="button" id="btn-calc-eq56" class="growth-btn-compute">
                                <span>Compute Biomass</span>
                            </button>
                        </div>

                        <div class="indiv-calc-results">
                            <div class="indiv-res-box">
                                <span class="res-card-label">STANDING BIOMASS SUMMARY</span>
                                <div class="biomass-compare-grid">
                                    <div class="biomass-block">
                                        <span class="biomass-block-label">INITIAL BIOMASS (IB)</span>
                                        <strong id="indiv-bio-ib-val" class="biomass-stat-val">1.00 kg</strong>
                                        <span id="indiv-bio-ib-sub" class="biomass-stat-sub">(1,000 g)</span>
                                    </div>
                                    <div class="biomass-block">
                                        <span class="biomass-block-label">FINAL BIOMASS (FB)</span>
                                        <strong id="indiv-bio-fb-val" class="biomass-stat-val">1,700.00 kg</strong>
                                        <span id="indiv-bio-fb-sub" class="biomass-stat-sub">(1,700,000 g)</span>
                                    </div>
                                </div>
                                <div class="net-yield-banner">
                                    <span>NET BIOMASS YIELD GAIN (FB - IB):</span>
                                    <strong id="indiv-bio-gain-val">1,699.00 kg (1.70 metric tons)</strong>
                                </div>
                            </div>

                            <div class="step-math-box">
                                <span class="step-math-title">Step-by-Step Substitution</span>
                                <div class="step-row">
                                    <span>Eq. 5 (IB):</span>
                                    <code id="indiv-bio-ib-step">100,000 &times; 0.010 g = 1,000 g (1.00 kg)</code>
                                </div>
                                <div class="step-row">
                                    <span>Eq. 6 (FB):</span>
                                    <code id="indiv-bio-fb-step">85,000 &times; 20.00 g = 1,700,000 g (1,700.00 kg)</code>
                                </div>
                            </div>
                        </div>
                    </div>
                </article>
            </div>

            <!-- PANE 6: Eq. 7 FEED CONVERSION RATIO (FCR) -->
            <div id="pane-growth-eq7" class="growth-tab-pane" role="tabpanel" aria-labelledby="tab-btn-eq7" hidden>
                <article class="panel dashboard-panel individual-growth-panel">
                    <div class="tools-panel-header">
                        <div class="panel-heading-icon tools-icon-carbon">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-calculator"></use></svg>
                        </div>
                        <div>
                            <h2>Equation 7: Feed Conversion Ratio (FCR) Calculator</h2>
                            <p>Assesses the feed utilization efficiency: kilograms of feed required to produce 1 kg of shrimp biomass gain.</p>
                        </div>
                    </div>

                    <div class="indiv-calc-grid">
                        <div class="indiv-calc-inputs">
                            <div class="math-eq-banner">
                                <span class="math-eq-tag">FORMULA</span>
                                <code>FCR = TFG / (FB - IB)</code>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-fcr-tfg">
                                    <span class="field-label-text">Total Feed Given (TFG)</span>
                                    <span class="field-hint">Total cumulative commercial feed dispensed</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-fcr-tfg" min="1" max="1000000" step="25" value="2125">
                                    <select id="indiv-fcr-tfg-unit" class="input-unit-select" aria-label="Feed weight unit">
                                        <option value="kg" selected>kg</option>
                                        <option value="g">grams</option>
                                    </select>
                                </div>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-fcr-fb">
                                    <span class="field-label-text">Final Biomass (FB)</span>
                                    <span class="field-hint">Harvest biomass in kg</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-fcr-fb" min="1" max="1000000" step="25" value="1700">
                                    <span class="input-unit">kg</span>
                                </div>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-fcr-ib">
                                    <span class="field-label-text">Initial Biomass (IB)</span>
                                    <span class="field-hint">Stocking biomass in kg</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-fcr-ib" min="0.01" max="50000" step="0.5" value="1.00">
                                    <span class="input-unit">kg</span>
                                </div>
                            </div>

                            <button type="button" id="btn-calc-eq7" class="growth-btn-compute">
                                <span>Compute Feed Conversion Ratio</span>
                            </button>
                        </div>

                        <div class="indiv-calc-results">
                            <div class="indiv-res-box">
                                <span class="res-card-label">COMPUTED FEED CONVERSION RATIO</span>
                                <div class="indiv-big-stat">
                                    <strong id="indiv-fcr-result">1.251</strong>
                                    <span class="stat-unit">FCR</span>
                                    <span id="indiv-fcr-badge" class="wqi-metric-badge badge-optimal">Optimal</span>
                                </div>
                                <div class="indiv-breakdown">
                                    <div class="indiv-stat-row">
                                        <span>Feed Assimilation Efficiency:</span>
                                        <strong id="indiv-fcr-efficiency">79.95%</strong>
                                    </div>
                                    <div class="indiv-stat-row">
                                        <span>Net Weight Gain Produced:</span>
                                        <strong id="indiv-fcr-gain-desc">1,699.00 kg</strong>
                                    </div>
                                </div>
                            </div>

                            <div class="step-math-box">
                                <span class="step-math-title">Step-by-Step Substitution</span>
                                <div class="step-row">
                                    <span>Formula Substitution:</span>
                                    <code id="indiv-fcr-step-math">FCR = 2,125.0 kg / (1,700.0 - 1.0) kg = 1.251</code>
                                </div>
                                <p id="indiv-fcr-rating" class="treatment-instruction">
                                    Target commercial FCR for Penaeus vannamei is 1.20&ndash;1.50. This result indicates minimal feed wastage and high nutrient assimilation.
                                </p>
                            </div>
                        </div>
                    </div>
                </article>
            </div>

            <!-- PANE 7: Eq. 8 FULTON'S CONDITION FACTOR (K) -->
            <div id="pane-growth-eq8" class="growth-tab-pane" role="tabpanel" aria-labelledby="tab-btn-eq8" hidden>
                <article class="panel dashboard-panel individual-growth-panel">
                    <div class="tools-panel-header">
                        <div class="panel-heading-icon tools-icon-biomass">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-settings"></use></svg>
                        </div>
                        <div>
                            <h2>Equation 8: Fulton's Condition Factor (K) Calculator</h2>
                            <p>Evaluates shrimp plumpness, muscular health, and robust morphometric body condition from weight and length.</p>
                        </div>
                    </div>

                    <div class="indiv-calc-grid">
                        <div class="indiv-calc-inputs">
                            <div class="math-eq-banner">
                                <span class="math-eq-tag">FORMULA</span>
                                <code>K = (FABW / TL&sup3;) &times; 100</code>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-k-fabw">
                                    <span class="field-label-text">Final Average Body Weight (FABW)</span>
                                    <span class="field-hint">Average body weight per shrimp (grams)</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-k-fabw" min="0.1" max="100" step="0.1" value="20.00">
                                    <span class="input-unit">grams</span>
                                </div>
                            </div>

                            <div class="tools-field-group">
                                <label class="tools-field-label" for="indiv-k-tl">
                                    <span class="field-label-text">Total Length (TL)</span>
                                    <span class="field-hint">Linear length from tip of rostrum to tip of telson (cm)</span>
                                </label>
                                <div class="tools-input-wrap">
                                    <input type="number" id="indiv-k-tl" min="1.0" max="35.0" step="0.1" value="12.9">
                                    <span class="input-unit">cm</span>
                                </div>
                            </div>

                            <button type="button" id="btn-calc-eq8" class="growth-btn-compute">
                                <span>Compute Fulton's Condition Factor</span>
                            </button>
                        </div>

                        <div class="indiv-calc-results">
                            <div class="indiv-res-box">
                                <span class="res-card-label">FULTON'S CONDITION FACTOR (K)</span>
                                <div class="indiv-big-stat">
                                    <strong id="indiv-k-result">0.9317</strong>
                                    <span class="stat-unit">K</span>
                                    <span id="indiv-k-badge" class="wqi-metric-badge badge-optimal">Optimal Condition</span>
                                </div>
                                <div class="indiv-breakdown">
                                    <div class="indiv-stat-row">
                                        <span>Target Vannamei Range:</span>
                                        <strong>0.80 &ndash; 1.15 K</strong>
                                    </div>
                                    <div class="indiv-stat-row">
                                        <span>Body Condition Assessment:</span>
                                        <strong id="indiv-k-summary">Robust &amp; Well-proportioned</strong>
                                    </div>
                                </div>
                            </div>

                            <div class="step-math-box">
                                <span class="step-math-title">Step-by-Step Substitution</span>
                                <div class="step-row">
                                    <span>Formula Substitution:</span>
                                    <code id="indiv-k-step-math">K = (20.00 / 12.9&sup3;) &times; 100 = (20.00 / 2,146.689) &times; 100 = 0.9317</code>
                                </div>
                                <p id="indiv-k-rating" class="treatment-instruction">
                                    A Fulton's condition factor between 0.80 and 1.15 is the ideal biological index for healthy commercial Penaeus vannamei, denoting dense muscle tissue, full tail meat filling, and healthy exoskeleton development.
                                </p>
                            </div>
                        </div>
                    </div>
                </article>
            </div>

        </section>
'''

def update_calculators():
    with open('templates/calculators.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Target marker where Section 2 used to start:
    target_marker = '<!-- 2. WATER TREATMENT & DOSING CALCULATORS -->'
    if target_marker not in content:
        print(f"Error: Could not find target marker: {target_marker}")
        return False

    # Insert Section 2 before target marker
    updated = content.replace(target_marker, section2_html.strip() + '\n\n\n        <!-- 3. WATER TREATMENT & DOSING CALCULATORS -->')

    # Update subsequent section numbering comments
    updated = updated.replace('<!-- 3. UNIONIZED AMMONIA (NH3) CALCULATOR & VAN WYK MATRIX -->', '<!-- 4. UNIONIZED AMMONIA (NH3) CALCULATOR & VAN WYK MATRIX -->')
    updated = updated.replace('<!-- 4. PENAEUS VANNAMEI SPECIES WATER QUALITY STANDARDS & PROTOCOLS -->', '<!-- 5. PENAEUS VANNAMEI SPECIES WATER QUALITY STANDARDS & PROTOCOLS -->')

    with open('templates/calculators.html', 'w', encoding='utf-8') as f:
        f.write(updated)

    print("Successfully updated templates/calculators.html with Section 2!")
    return True

if __name__ == '__main__':
    update_calculators()

