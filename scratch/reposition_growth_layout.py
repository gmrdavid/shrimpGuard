# -*- coding: utf-8 -*-
"""
Script to place Computed Performance Metrics below Pond Stocking & Harvest Parameters in Section 2.
"""

new_section2_stacked_html = '''        <!-- 2. SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE CALCULATOR (Eqs. 1–8) -->
        <section class="dashboard-section" id="tools-growth-section" aria-labelledby="growth-calculators-title">

            <div class="section-heading-row">
                <div>
                    <span class="section-eyebrow">ZOOTECHNICAL &bull; PENAEUS VANNAMEI PRODUCTION EQUATIONS</span>
                    <h2 id="growth-calculators-title">Shrimp Growth &amp; Zootechnical Performance Calculator (Eqs. 1–8)</h2>
                    <p>Standard scientific aquaculture equations computing survival rate, average body weight, daily gain, specific growth rate, pond biomass, feed conversion ratio, and Fulton's condition factor.</p>
                </div>
                <div class="monitoring-species-pill">
                    <span class="species-dot"></span>
                    <span>8 Scientific Equations</span>
                </div>
            </div>

            <article class="panel dashboard-panel tools-calc-panel">

                <div class="tools-panel-header">
                    <div class="panel-heading-icon tools-icon-biomass">
                        <svg class="ui-icon" aria-hidden="true">
                            <use href="#icon-shrimp"></use>
                        </svg>
                    </div>
                    <div>
                        <h2>All-in-One Growth &amp; Production Performance Engine</h2>
                        <p>Simultaneously computes Survival Rate, FABW, ADWG, SGR, Biomasses, FCR, and Fulton's K from pond stocking and harvest data.</p>
                    </div>
                </div>

                <!-- TOP SECTION: POND STOCKING & HARVEST PARAMETERS -->
                <div class="growth-parameters-wrapper">
                    <div class="tools-subheading-row">
                        <h3 class="tools-subheading">Pond Stocking &amp; Harvest Parameters</h3>
                        <div class="growth-param-actions">
                            <button type="button" id="btn-sync-from-biomass" class="tools-chip-btn" title="Sync live population and ABW values from Biomass Section above">
                                Sync Biomass Tool
                            </button>
                        </div>
                    </div>

                    <!-- Presets Row -->
                    <div class="ammonia-presets-row" style="margin-bottom: 16px;">
                        <span class="ammonia-presets-label">Pond Presets:</span>
                        <div class="ammonia-preset-chips" id="growth-master-presets">
                            <button type="button" class="preset-chip active btn-preset-growth" data-preset="commercial">Commercial 90d</button>
                            <button type="button" class="preset-chip btn-preset-growth" data-preset="intensive">Intensive 75d</button>
                            <button type="button" class="preset-chip btn-preset-growth" data-preset="nursery">Nursery 30d</button>
                        </div>
                    </div>

                    <!-- Responsive Grid of 7 Input Fields -->
                    <div class="growth-form-grid">

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
                        <label class="tools-field-label" for="gm-total-length">
                            <span class="field-label-text">Average Total Length (TL)</span>
                            <span class="dashboard-field-wrap">
                                <input type="number" id="gm-total-length" min="1.0" max="30.0" step="0.1" value="12.9" placeholder="e.g. 12.9">
                                <span class="input-unit">cm</span>
                            </span>
                        </label>

                    </div>

                    <!-- Callout Tip -->
                    <div class="tools-callout-tip" style="margin-top: 14px;">
                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                        <p>
                            <strong>Scientific Model Equations (Eqs. 1–8):</strong> Conforms to validated zootechnical research for <em>Penaeus vannamei</em> shrimp culture. Performance metrics automatically recompute in real-time as parameters change. Click <strong>"Formula &amp; Steps"</strong> on any card to view detailed formulation and recommendations.
                        </p>
                    </div>
                </div>

                <!-- BOTTOM SECTION: COMPUTED PERFORMANCE METRICS (8 CARDS IN RESPONSIVE GRID) -->
                <div class="growth-metrics-wrapper">
                    <div class="growth-metrics-header">
                        <div>
                            <h3 class="tools-subheading">Computed Performance Metrics (Eqs. 1–8)</h3>
                            <span class="growth-metrics-sub">Full zootechnical growth profile, biomass conversion, feeding efficiency, and morphometric condition factor</span>
                        </div>
                    </div>

                    <div class="growth-metrics-grid">

                        <!-- Card 1: Survival Rate -->
                        <div class="tools-res-card">
                            <div class="res-card-header">
                                <span class="res-card-label">EQ. 1 &bull; SURVIVAL RATE (SR)</span>
                                <span id="gm-res-sr-badge" class="wqi-metric-badge badge-optimal">Optimal</span>
                            </div>
                            <div class="res-value-row">
                                <strong id="gm-res-sr-val" class="res-big-value">85.00</strong>
                                <span class="res-unit">%</span>
                            </div>
                            <p class="res-card-detail">Mortality: <strong id="gm-res-mortality-count">15,000</strong> (<span id="gm-res-mortality-pct">15.00%</span>)</p>
                            <div class="res-card-action-row">
                                <button type="button" class="growth-calc-details-btn" data-eq="1" aria-label="View calculation details for Equation 1">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                    <span>Formula &amp; Steps</span>
                                </button>
                            </div>
                        </div>

                        <!-- Card 2: Final Average Body Weight -->
                        <div class="tools-res-card">
                            <div class="res-card-header">
                                <span class="res-card-label">EQ. 2 &bull; FINAL AVG BODY WEIGHT (FABW)</span>
                                <span id="gm-res-fabw-badge" class="wqi-metric-badge badge-optimal">Size 50</span>
                            </div>
                            <div class="res-value-row">
                                <strong id="gm-res-fabw-val" class="res-big-value">20.00</strong>
                                <span class="res-unit">g / shrimp</span>
                            </div>
                            <p class="res-card-detail">Market Count: <strong id="gm-res-count-per-kg">50.0</strong> pcs / kg</p>
                            <div class="res-card-action-row">
                                <button type="button" class="growth-calc-details-btn" data-eq="2" aria-label="View calculation details for Equation 2">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                    <span>Formula &amp; Steps</span>
                                </button>
                            </div>
                        </div>

                        <!-- Card 3: Average Daily Weight Gain (SEPARATE) -->
                        <div class="tools-res-card">
                            <div class="res-card-header">
                                <span class="res-card-label">EQ. 3 &bull; AVG DAILY WEIGHT GAIN (ADWG)</span>
                                <span id="gm-res-adwg-badge" class="wqi-metric-badge badge-optimal">Optimal Growth</span>
                            </div>
                            <div class="res-value-row">
                                <strong id="gm-res-adwg-val" class="res-big-value">0.2221</strong>
                                <span class="res-unit">g / day</span>
                            </div>
                            <p class="res-card-detail">Weekly Gain: <strong id="gm-res-weekly-gain">1.555</strong> g / week</p>
                            <div class="res-card-action-row">
                                <button type="button" class="growth-calc-details-btn" data-eq="3" aria-label="View calculation details for Equation 3">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                    <span>Formula &amp; Steps</span>
                                </button>
                            </div>
                        </div>

                        <!-- Card 4: Specific Growth Rate (SEPARATE) -->
                        <div class="tools-res-card">
                            <div class="res-card-header">
                                <span class="res-card-label">EQ. 4 &bull; SPECIFIC GROWTH RATE (SGR)</span>
                                <span class="wqi-metric-badge badge-optimal">Logarithmic Velocity</span>
                            </div>
                            <div class="res-value-row">
                                <strong id="gm-res-sgr-val" class="res-big-value">8.445</strong>
                                <span class="res-unit">% / day</span>
                            </div>
                            <p class="res-card-detail">Weight Multiplier: <strong id="gm-res-weight-mult">2,000&times;</strong></p>
                            <div class="res-card-action-row">
                                <button type="button" class="growth-calc-details-btn" data-eq="4" aria-label="View calculation details for Equation 4">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                    <span>Formula &amp; Steps</span>
                                </button>
                            </div>
                        </div>

                        <!-- Card 5: Initial Biomass (SEPARATE) -->
                        <div class="tools-res-card">
                            <div class="res-card-header">
                                <span class="res-card-label">EQ. 5 &bull; INITIAL BIOMASS (IB)</span>
                                <span class="res-secondary-val">Stocking Mass</span>
                            </div>
                            <div class="res-value-row">
                                <strong id="gm-res-ib-kg" class="res-big-value">1.00</strong>
                                <span class="res-unit">kg</span>
                            </div>
                            <p class="res-card-detail">Released: <strong id="gm-res-ib-grams">1,000</strong> g biological mass</p>
                            <div class="res-card-action-row">
                                <button type="button" class="growth-calc-details-btn" data-eq="5" aria-label="View calculation details for Equation 5">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                    <span>Formula &amp; Steps</span>
                                </button>
                            </div>
                        </div>

                        <!-- Card 6: Final Biomass (SEPARATE) -->
                        <div class="tools-res-card">
                            <div class="res-card-header">
                                <span class="res-card-label">EQ. 6 &bull; FINAL BIOMASS (FB)</span>
                                <span class="res-secondary-val">Standing Crop</span>
                            </div>
                            <div class="res-value-row">
                                <strong id="gm-res-fb-kg" class="res-big-value">1,700.00</strong>
                                <span class="res-unit">kg</span>
                            </div>
                            <p class="res-card-detail">Net Live Gain: <strong id="gm-res-net-biomass">1,699.00</strong> kg</p>
                            <div class="res-card-action-row">
                                <button type="button" class="growth-calc-details-btn" data-eq="6" aria-label="View calculation details for Equation 6">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                    <span>Formula &amp; Steps</span>
                                </button>
                            </div>
                        </div>

                        <!-- Card 7: Feed Conversion Ratio (Highlight Card) -->
                        <div class="tools-res-card highlight-card">
                            <div class="res-card-header">
                                <span class="res-card-label">EQ. 7 &bull; FEED CONVERSION RATIO (FCR)</span>
                                <span id="gm-res-fcr-badge" class="wqi-metric-badge badge-optimal">Optimal</span>
                            </div>
                            <div class="res-value-row">
                                <strong id="gm-res-fcr-val" class="res-big-value res-accent-value">1.251</strong>
                                <span class="res-unit">FCR</span>
                            </div>
                            <p class="res-card-detail">Feed Efficiency: <strong id="gm-res-feed-efficiency">79.95%</strong> (Feed: <span id="gm-res-tfg-summary">2,125.0 kg</span>)</p>
                            <div class="res-card-action-row">
                                <button type="button" class="growth-calc-details-btn" data-eq="7" aria-label="View calculation details for Equation 7">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                    <span>Formula &amp; Steps</span>
                                </button>
                            </div>
                        </div>

                        <!-- Card 8: Fulton's Condition Factor -->
                        <div class="tools-res-card">
                            <div class="res-card-header">
                                <span class="res-card-label">EQ. 8 &bull; FULTON'S CONDITION FACTOR (K)</span>
                                <span id="gm-res-k-badge" class="wqi-metric-badge badge-optimal">Optimal</span>
                            </div>
                            <div class="res-value-row">
                                <strong id="gm-res-k-val" class="res-big-value">0.9317</strong>
                                <span class="res-unit">K factor</span>
                            </div>
                            <p class="res-card-detail">Profile: <strong id="gm-res-k-profile">Healthy, robust girth</strong></p>
                            <div class="res-card-action-row">
                                <button type="button" class="growth-calc-details-btn" data-eq="8" aria-label="View calculation details for Equation 8">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                    <span>Formula &amp; Steps</span>
                                </button>
                            </div>
                        </div>

                    </div>
                </div>

            </article>

        </section>
'''

def update_layout():
    with open('templates/calculators.html', 'r', encoding='utf-8') as f:
        content = f.read()

    s2_start = '<!-- 2. SHRIMP GROWTH & ZOOTECHNICAL'
    s3_start = '<!-- 3. WATER TREATMENT & DOSING CALCULATORS -->'

    idx_s2 = content.find(s2_start)
    idx_s3 = content.find(s3_start)

    if idx_s2 == -1 or idx_s3 == -1:
        print(f"Error finding section markers: s2={idx_s2}, s3={idx_s3}")
        return False

    content = content[:idx_s2] + new_section2_stacked_html + '\n\n\n        ' + content[idx_s3:]

    with open('templates/calculators.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Successfully updated templates/calculators.html with stacked layout!")
    return True

if __name__ == '__main__':
    update_layout()

