# -*- coding: utf-8 -*-
"""
Script to apply user requests:
1. Remove all separate calculators of Eq. 1 - Eq. 8, keep ONLY All-in-One.
2. In All-in-One performance metrics, do not merge Eq 3 and 4; separate them into distinct cards.
3. Remove displayed formulas from metric cards; add a popup dialog for each equation showing:
   - Scientific formula & variable definitions
   - Step-by-step substitution with current pond values
   - Zootechnical recommendation & benchmark advice for Penaeus vannamei.
"""

# New Section 2 HTML (Only All-in-One Engine with 8 separate clean metric cards)
new_section2_html = '''        <!-- 2. SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE CALCULATOR (Eqs. 1–8) -->
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

                <div class="tools-grid-split">

                    <!-- INPUTS COLUMN -->
                    <div class="tools-input-column">
                        <div class="tools-subheading-row">
                            <h3 class="tools-subheading">Pond Stocking &amp; Harvest Parameters</h3>
                            <button type="button" id="btn-sync-from-biomass" class="tools-chip-btn" title="Sync live population and ABW values from Biomass Section above">
                                Sync Biomass Tool
                            </button>
                        </div>

                        <!-- Presets Row -->
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

                        <!-- Tip callout matching Section 1 exactly -->
                        <div class="tools-callout-tip">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                            <p>
                                <strong>Scientific Model Equations (Eqs. 1–8):</strong> Conforms to validated zootechnical research for <em>Penaeus vannamei</em> shrimp culture. Click on any metric's <strong>"Formula &amp; Steps"</strong> button to view its mathematical formulation, step-by-step substitution, and zootechnical recommendations.
                            </p>
                        </div>

                    </div>

                    <!-- OUTPUTS COLUMN (8 SEPARATE METRIC CARDS) -->
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
                                <p class="res-card-detail">Stocked: 100,000 shrimp &bull; Harvested: 85,000 live shrimp</p>
                                <div class="res-card-action-row">
                                    <button type="button" class="growth-calc-details-btn" data-eq="1" aria-label="View calculation details for Equation 1">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                        <span>Formula &amp; Steps</span>
                                    </button>
                                </div>
                            </div>

                            <!-- Eq. 2: Final Average Body Weight -->
                            <div class="tools-res-card">
                                <div class="res-card-header">
                                    <span class="res-card-label">EQ. 2 &bull; FINAL AVG BODY WEIGHT (FABW)</span>
                                    <span id="gm-res-fabw-badge" class="wqi-metric-badge badge-optimal">Size 50</span>
                                </div>
                                <div class="res-value-row">
                                    <strong id="gm-res-fabw-val" class="res-big-value">20.00</strong>
                                    <span class="res-unit">g / shrimp</span>
                                    <span class="res-secondary-val">(<strong id="gm-res-count-per-kg">50.0</strong> pcs/kg)</span>
                                </div>
                                <p class="res-card-detail">Bulk harvested: <span id="gm-res-bulk-summary">1,700.00 kg</span></p>
                                <div class="res-card-action-row">
                                    <button type="button" class="growth-calc-details-btn" data-eq="2" aria-label="View calculation details for Equation 2">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                        <span>Formula &amp; Steps</span>
                                    </button>
                                </div>
                            </div>

                            <!-- Eq. 3: Average Daily Weight Gain (SEPARATE) -->
                            <div class="tools-res-card">
                                <div class="res-card-header">
                                    <span class="res-card-label">EQ. 3 &bull; AVG DAILY WEIGHT GAIN (ADWG)</span>
                                    <span id="gm-res-adwg-badge" class="wqi-metric-badge badge-optimal">Optimal Growth</span>
                                </div>
                                <div class="res-value-row">
                                    <strong id="gm-res-adwg-val" class="res-big-value">0.2221</strong>
                                    <span class="res-unit">g / day</span>
                                    <span class="res-secondary-val">(<strong id="gm-res-weekly-gain">1.555</strong> g / week)</span>
                                </div>
                                <p class="res-card-detail">Linear daily gain for 90 days culture duration</p>
                                <div class="res-card-action-row">
                                    <button type="button" class="growth-calc-details-btn" data-eq="3" aria-label="View calculation details for Equation 3">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                        <span>Formula &amp; Steps</span>
                                    </button>
                                </div>
                            </div>

                            <!-- Eq. 4: Specific Growth Rate (SEPARATE) -->
                            <div class="tools-res-card">
                                <div class="res-card-header">
                                    <span class="res-card-label">EQ. 4 &bull; SPECIFIC GROWTH RATE (SGR)</span>
                                    <span class="wqi-metric-badge badge-optimal">Logarithmic Velocity</span>
                                </div>
                                <div class="res-value-row">
                                    <strong id="gm-res-sgr-val" class="res-big-value">8.445</strong>
                                    <span class="res-unit">% / day</span>
                                    <span class="res-secondary-val">(Weight Multiplication: <strong id="gm-res-weight-mult">2,000&times;</strong>)</span>
                                </div>
                                <p class="res-card-detail">Exponential weight compounding per culture day</p>
                                <div class="res-card-action-row">
                                    <button type="button" class="growth-calc-details-btn" data-eq="4" aria-label="View calculation details for Equation 4">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                        <span>Formula &amp; Steps</span>
                                    </button>
                                </div>
                            </div>

                            <!-- Eq. 5: Initial Biomass (SEPARATE) -->
                            <div class="tools-res-card">
                                <div class="res-card-header">
                                    <span class="res-card-label">EQ. 5 &bull; INITIAL BIOMASS (IB)</span>
                                    <span class="res-secondary-val">Stocking Mass</span>
                                </div>
                                <div class="res-value-row">
                                    <strong id="gm-res-ib-kg" class="res-big-value">1.00</strong>
                                    <span class="res-unit">kg</span>
                                    <span class="res-secondary-val">(<span id="gm-res-ib-grams">1,000</span> g at stocking)</span>
                                </div>
                                <p class="res-card-detail">Starting biomass of post-larvae released</p>
                                <div class="res-card-action-row">
                                    <button type="button" class="growth-calc-details-btn" data-eq="5" aria-label="View calculation details for Equation 5">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                        <span>Formula &amp; Steps</span>
                                    </button>
                                </div>
                            </div>

                            <!-- Eq. 6: Final Biomass (SEPARATE) -->
                            <div class="tools-res-card">
                                <div class="res-card-header">
                                    <span class="res-card-label">EQ. 6 &bull; FINAL BIOMASS (FB)</span>
                                    <span class="res-secondary-val">Harvest Mass</span>
                                </div>
                                <div class="res-value-row">
                                    <strong id="gm-res-fb-kg" class="res-big-value">1,700.00</strong>
                                    <span class="res-unit">kg</span>
                                    <span class="res-secondary-val">(Net Yield Gain: <strong id="gm-res-net-biomass">1,699.00</strong> kg)</span>
                                </div>
                                <p class="res-card-detail">Total biological standing crop harvested (1.70 metric tons)</p>
                                <div class="res-card-action-row">
                                    <button type="button" class="growth-calc-details-btn" data-eq="6" aria-label="View calculation details for Equation 6">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                        <span>Formula &amp; Steps</span>
                                    </button>
                                </div>
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
                                    <span>Total Feed Given: <span id="gm-res-tfg-summary">2,125.0 kg</span></span>
                                    <span>Net Biomass Gain: <span id="gm-res-gain-summary">1,699.0 kg</span></span>
                                </div>
                                <div class="res-card-action-row">
                                    <button type="button" class="growth-calc-details-btn" data-eq="7" aria-label="View calculation details for Equation 7">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                        <span>Formula &amp; Steps</span>
                                    </button>
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
                                <p class="res-card-detail">Profile: <strong id="gm-res-k-profile">Healthy, well-proportioned robust girth</strong></p>
                                <div class="res-card-action-row">
                                    <button type="button" class="growth-calc-details-btn" data-eq="8" aria-label="View calculation details for Equation 8">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                        <span>Formula &amp; Steps</span>
                                    </button>
                                </div>
                            </div>

                        </div>

                    </div>

                </div>

            </article>

        </section>
'''

# New Modal Popup Dialog HTML
growth_modal_html = '''
<!-- GROWTH EQUATION DETAILS POPUP DIALOG -->
<div id="growth-equation-modal" class="modal-dialog-backdrop" hidden>
    <div class="modal-dialog-container growth-modal-container" role="dialog" aria-modal="true" aria-labelledby="growth-modal-title">

        <div class="modal-dialog-header">
            <div class="modal-header-text">
                <div class="panel-heading-icon tools-icon-biomass modal-icon">
                    <svg class="ui-icon" aria-hidden="true">
                        <use href="#icon-calculator"></use>
                    </svg>
                </div>
                <div>
                    <h3 id="growth-modal-title">Equation Details</h3>
                    <p id="growth-modal-subtitle">Mathematical formulation, parameter substitution, and zootechnical guidance</p>
                </div>
            </div>
            <button type="button" id="close-growth-modal" class="modal-close-btn" aria-label="Close dialog">
                &times;
            </button>
        </div>

        <div class="modal-dialog-body growth-modal-body">
            <!-- 1. Scientific Formula -->
            <div class="growth-modal-section">
                <span class="growth-modal-section-title">SCIENTIFIC FORMULA &amp; NOTATION</span>
                <div class="growth-modal-formula-box">
                    <code id="growth-modal-formula">SR = (LHC / IS) &times; 100</code>
                </div>
                <div id="growth-modal-variables" class="growth-modal-vars-list">
                    <!-- Dynamic variable breakdown -->
                </div>
            </div>

            <!-- 2. Step-by-Step Substitution -->
            <div class="growth-modal-section">
                <span class="growth-modal-section-title">STEP-BY-STEP POND SUBSTITUTION</span>
                <div class="growth-modal-substitution-box">
                    <div id="growth-modal-substitution" class="growth-modal-substitution-text">
                        <!-- e.g. (85,000 shrimp / 100,000 shrimp) * 100 = 85.00% -->
                    </div>
                </div>
            </div>

            <!-- 3. Recommendation & Benchmarks -->
            <div class="growth-modal-section">
                <div class="growth-modal-eval-header">
                    <span class="growth-modal-section-title">ZOOTECHNICAL EVALUATION &amp; RECOMMENDATION</span>
                    <span id="growth-modal-badge" class="wqi-metric-badge badge-optimal">Optimal</span>
                </div>
                <div class="growth-modal-eval-card">
                    <p id="growth-modal-recommendation" class="growth-modal-eval-text">
                        <!-- Dynamic assessment -->
                    </p>
                    <div id="growth-modal-action-tip" class="growth-modal-tip-box">
                        <!-- Actionable advice -->
                    </div>
                </div>
            </div>
        </div>

        <div class="modal-dialog-footer">
            <button type="button" id="growth-modal-close-action" class="ammonia-btn-primary">
                Close Calculation
            </button>
        </div>

    </div>
</div>
'''

def update_calculators_html():
    with open('templates/calculators.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find Section 2 start and Section 3 start
    s2_start = '<!-- 2. SHRIMP GROWTH & ZOOTECHNICAL'
    s3_start = '<!-- 3. WATER TREATMENT & DOSING CALCULATORS -->'

    idx_s2 = content.find(s2_start)
    idx_s3 = content.find(s3_start)

    if idx_s2 == -1 or idx_s3 == -1:
        print(f"Error finding section markers: s2={idx_s2}, s3={idx_s3}")
        return False

    # Replace Section 2 with new_section2_html
    content = content[:idx_s2] + new_section2_html + '\n\n\n        ' + content[idx_s3:]

    # Remove existing #growth-equation-modal if present
    if '<div id="growth-equation-modal"' in content:
        import re
        content = re.sub(r'<!-- GROWTH EQUATION DETAILS POPUP DIALOG -->[\s\S]+?</div>\s*</div>\s*</div>', '', content)

    # Insert growth_modal_html right before <!-- VAN WYK REFERENCE MATRIX POPUP DIALOG -->
    van_wyk_marker = '<!-- VAN WYK REFERENCE MATRIX POPUP DIALOG -->'
    if van_wyk_marker in content:
        content = content.replace(van_wyk_marker, growth_modal_html.strip() + '\n\n\n' + van_wyk_marker)
    else:
        # Before <script
        content = content.replace('<script src="{{ url_for(\'static\', filename=\'js/calculators.js\')', growth_modal_html.strip() + '\n\n<script src="{{ url_for(\'static\', filename=\'js/calculators.js\')')

    with open('templates/calculators.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Updated templates/calculators.html with clean All-in-One and popup dialog modal!")
    return True

if __name__ == '__main__':
    update_calculators_html()

