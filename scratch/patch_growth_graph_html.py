import re

with open("templates/calculators.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add button in growth-param-actions (top of Section 2)
target1 = """                        <div class="growth-param-actions">
                            <button type="button" id="btn-sync-from-biomass" class="tools-chip-btn" title="Sync live population and ABW values from Biomass Section above">
                                Sync Biomass Tool
                            </button>
                        </div>"""

replace1 = """                        <div class="growth-param-actions">
                            <button type="button" id="btn-sync-from-biomass" class="tools-chip-btn" title="Sync live population and ABW values from Biomass Section above">
                                Sync Biomass Tool
                            </button>
                            <button type="button" id="btn-open-growth-chart-top" class="tools-chip-btn tools-chip-chart" title="View Shrimp Growth & Zootechnical Performance Graph">
                                <svg class="ui-icon" aria-hidden="true" style="width:13px;height:13px;margin-right:4px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <line x1="18" y1="20" x2="18" y2="10"></line>
                                    <line x1="12" y1="20" x2="12" y2="4"></line>
                                    <line x1="6" y1="20" x2="6" y2="14"></line>
                                </svg>
                                <span>Performance Graph</span>
                            </button>
                        </div>"""

# 2. Add button in growth-metrics-header
target2 = """                    <div class="growth-metrics-header">
                        <div>
                            <h3 class="tools-subheading">Computed Performance Metrics (Eqs. 1–8)</h3>
                            <span class="growth-metrics-sub">Full zootechnical growth profile, biomass conversion, feeding efficiency, and morphometric condition factor</span>
                        </div>
                    </div>"""

replace2 = """                    <div class="growth-metrics-header">
                        <div>
                            <h3 class="tools-subheading">Computed Performance Metrics (Eqs. 1–8)</h3>
                            <span class="growth-metrics-sub">Full zootechnical growth profile, biomass conversion, feeding efficiency, and morphometric condition factor</span>
                        </div>
                        <div class="growth-header-actions">
                            <button type="button" id="btn-open-growth-chart" class="tools-chart-modal-btn" title="View Shrimp Growth & Zootechnical Performance Trend Graph">
                                <svg class="ui-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <line x1="18" y1="20" x2="18" y2="10"></line>
                                    <line x1="12" y1="20" x2="12" y2="4"></line>
                                    <line x1="6" y1="20" x2="6" y2="14"></line>
                                </svg>
                                <span>Performance Trend Graph</span>
                            </button>
                        </div>
                    </div>"""

# 3. Add Modal dialog #growth-trend-graph-modal before #growth-equation-modal
target3 = '<!-- GROWTH EQUATION DETAILS POPUP DIALOG -->'

modal_graph_html = """<!-- SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE POPUP GRAPH MODAL (Eqs. 1-8 Excl. Eq. 5) -->
<div id="growth-trend-graph-modal" class="modal-dialog-backdrop" hidden>
    <div class="modal-dialog-container growth-graph-dialog" role="dialog" aria-modal="true" aria-labelledby="growth-graph-title">

        <div class="modal-dialog-header">
            <div class="modal-header-text">
                <div class="panel-heading-icon trend-panel-icon modal-icon">
                    <svg class="ui-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="20" x2="18" y2="10"></line>
                        <line x1="12" y1="20" x2="12" y2="4"></line>
                        <line x1="6" y1="20" x2="6" y2="14"></line>
                    </svg>
                </div>
                <div>
                    <span class="historical-section-eyebrow">ZOOTECHNICAL VISUAL TREND &bull; PENAEUS VANNAMEI</span>
                    <h3 id="growth-graph-title">Shrimp Growth &amp; Zootechnical Performance Trend</h3>
                    <p>Continuous trajectory and zootechnical evaluation across culture days for active production equations.</p>
                </div>
            </div>
            <button type="button" id="close-growth-graph-modal" class="modal-close-btn" aria-label="Close dialog">
                &times;
            </button>
        </div>

        <div class="modal-dialog-body growth-graph-modal-body">

            <!-- Chart Controls Row -->
            <div class="growth-graph-controls-row">
                <!-- View Mode Selector -->
                <div class="growth-graph-mode-toggle">
                    <button type="button" class="graph-mode-pill active" id="btn-graph-mode-trajectory" data-mode="trajectory">
                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-activity"></use></svg>
                        <span>Culture Cycle Trajectory (DOC 1–<span id="graph-doc-pill">90</span>)</span>
                    </button>
                    <button type="button" class="graph-mode-pill" id="btn-graph-mode-history" data-mode="history">
                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-history"></use></svg>
                        <span>Saved Database Batches</span>
                    </button>
                </div>

                <div class="growth-graph-badge-wrap">
                    <span id="growth-graph-count-badge" class="historical-count-badge">7 Zootechnical Metrics</span>
                </div>
            </div>

            <!-- Metric Filter Chips (Multi-Toggle) -->
            <div class="growth-metric-filter-bar">
                <span class="metric-filter-label">Display Metrics:</span>
                <div class="growth-metric-chips" id="growth-metric-chips-group">
                    <button type="button" class="metric-chip active" data-metric="sr" title="Eq. 1: Survival Rate (%)">
                        <i class="chip-color-dot dot-sr"></i>
                        <span>Eq. 1: SR (%)</span>
                    </button>
                    <button type="button" class="metric-chip active" data-metric="fabw" title="Eq. 2: Final Average Body Weight (g)">
                        <i class="chip-color-dot dot-fabw"></i>
                        <span>Eq. 2: FABW (g)</span>
                    </button>
                    <button type="button" class="metric-chip active" data-metric="adwg" title="Eq. 3: Average Daily Weight Gain (g/day)">
                        <i class="chip-color-dot dot-adwg"></i>
                        <span>Eq. 3: ADWG (g/d)</span>
                    </button>
                    <button type="button" class="metric-chip active" data-metric="sgr" title="Eq. 4: Specific Growth Rate (%/day)">
                        <i class="chip-color-dot dot-sgr"></i>
                        <span>Eq. 4: SGR (%/d)</span>
                    </button>
                    <button type="button" class="metric-chip active" data-metric="fb" title="Eq. 6: Final Biomass (kg)">
                        <i class="chip-color-dot dot-fb"></i>
                        <span>Eq. 6: Final Biomass (kg)</span>
                    </button>
                    <button type="button" class="metric-chip active" data-metric="fcr" title="Eq. 7: Feed Conversion Ratio">
                        <i class="chip-color-dot dot-fcr"></i>
                        <span>Eq. 7: FCR</span>
                    </button>
                    <button type="button" class="metric-chip active" data-metric="k" title="Eq. 8: Fulton's Condition Factor">
                        <i class="chip-color-dot dot-k"></i>
                        <span>Eq. 8: Fulton's K</span>
                    </button>
                </div>
                <button type="button" id="btn-toggle-all-growth-metrics" class="growth-toggle-all-btn">Reset All</button>
            </div>

            <!-- Canvas Chart Wrap (Uniform with water quality trend) -->
            <div class="historical-chart-wrap growth-chart-wrap">
                <canvas id="growth-trend-chart" role="img" aria-label="Shrimp Growth & Zootechnical Performance Graph">
                    Your browser does not support the canvas element.
                </canvas>
                <div id="growth-chart-tooltip" class="historical-chart-tooltip growth-chart-tooltip" hidden></div>
                <p id="growth-chart-empty" hidden>
                    No calculation readings available for the selected view.
                </p>
            </div>

            <!-- Legend (Uniform with water quality trend) -->
            <div id="growth-chart-legend" class="chart-legend monitoring-chart-legend growth-chart-legend" aria-label="Growth performance chart legend">
                <!-- Dynamically rendered / populated -->
            </div>

            <!-- Mini Summary Metric Cards Strip (Excluding Eq. 5) -->
            <div class="growth-graph-summary-strip">
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 1: Survival</span>
                    <strong id="mini-stat-sr" class="mini-val">-- %</strong>
                    <span id="mini-badge-sr" class="mini-badge badge-optimal">Optimal</span>
                </div>
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 2: FABW</span>
                    <strong id="mini-stat-fabw" class="mini-val">-- g</strong>
                    <span id="mini-sub-fabw" class="mini-sub">-- count/kg</span>
                </div>
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 3: ADWG</span>
                    <strong id="mini-stat-adwg" class="mini-val">-- g/d</strong>
                    <span id="mini-badge-adwg" class="mini-badge badge-optimal">Fast</span>
                </div>
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 4: SGR</span>
                    <strong id="mini-stat-sgr" class="mini-val">-- %/d</strong>
                    <span id="mini-sub-sgr" class="mini-sub">Specific Rate</span>
                </div>
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 6: Final Biomass</span>
                    <strong id="mini-stat-fb" class="mini-val">-- kg</strong>
                    <span id="mini-sub-fb" class="mini-sub">Yield</span>
                </div>
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 7: FCR</span>
                    <strong id="mini-stat-fcr" class="mini-val">--</strong>
                    <span id="mini-badge-fcr" class="mini-badge badge-optimal">Optimal</span>
                </div>
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 8: Fulton's K</span>
                    <strong id="mini-stat-k" class="mini-val">--</strong>
                    <span id="mini-badge-k" class="mini-badge badge-optimal">Normal</span>
                </div>
            </div>

        </div>

        <div class="modal-dialog-footer growth-graph-modal-footer">
            <button type="button" id="close-growth-graph-action-btn" class="tools-btn-secondary">
                Close Graph
            </button>
            <button type="button" id="growth-graph-open-export" class="tools-btn-export">
                <svg class="ui-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 3v12"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <path d="M5 17v4h14v-4"></path>
                </svg>
                <span>Export Performance Data</span>
            </button>
        </div>

    </div>
</div>

"""

# Normalize for replacing
norm_content = content.replace("\r\n", "\n")
norm_t1 = target1.replace("\r\n", "\n")
norm_r1 = replace1.replace("\r\n", "\n")
norm_t2 = target2.replace("\r\n", "\n")
norm_r2 = replace2.replace("\r\n", "\n")

if norm_t1 in norm_content:
    norm_content = norm_content.replace(norm_t1, norm_r1)
    print("Added top performance graph button")
else:
    print("ERROR: target1 not found")

if norm_t2 in norm_content:
    norm_content = norm_content.replace(norm_t2, norm_r2)
    print("Added main performance graph button in header")
else:
    print("ERROR: target2 not found")

if target3 in norm_content:
    norm_content = norm_content.replace(target3, modal_graph_html + target3)
    print("Added growth-trend-graph-modal")
else:
    print("ERROR: target3 not found")

with open("templates/calculators.html", "w", encoding="utf-8") as f:
    f.write(norm_content)

print("Saved templates/calculators.html successfully")

