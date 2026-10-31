import re

with open("templates/calculators.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update toolbar buttons in sync banner
old_btn = """                    <button type="button" id="btn-sync-live" class="tools-btn-secondary" title="Re-fetch and synchronize latest sensor readings across all calculators">
                        <svg class="ui-icon" aria-hidden="true">
                            <use href="#icon-history"></use>
                        </svg>
                        <span>Sync Live Data</span>
                    </button>"""

new_btns = """                    <div class="sync-banner-actions">
                        <button type="button" id="btn-sync-live" class="tools-btn-secondary" title="Re-fetch and synchronize latest sensor readings across all calculators">
                            <svg class="ui-icon" aria-hidden="true">
                                <use href="#icon-history"></use>
                            </svg>
                            <span>Sync Live Data</span>
                        </button>

                        <button type="button" id="btn-open-save-modal" class="tools-btn-save" title="Save current pond calculation snapshot into MySQL database">
                            <svg class="ui-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                                <polyline points="17 21 17 13 7 13 7 21"></polyline>
                                <polyline points="7 3 7 8 15 8"></polyline>
                            </svg>
                            <span>Save Snapshot</span>
                        </button>

                        <button type="button" id="btn-open-export-modal" class="tools-btn-export" title="Export calculation records to Excel or CSV with custom data selection">
                            <svg class="ui-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M12 3v12"></path>
                                <polyline points="7 10 12 15 17 10"></polyline>
                                <path d="M5 17v4h14v-4"></path>
                            </svg>
                            <span>Export Data</span>
                        </button>
                    </div>"""

# Normalize CRLF for replacement
norm_content = content.replace("\r\n", "\n")
norm_old = old_btn.replace("\r\n", "\n")
norm_new = new_btns.replace("\r\n", "\n")

if norm_old in norm_content:
    norm_content = norm_content.replace(norm_old, norm_new)
    print("Replaced sync buttons")
else:
    print("ERROR: old_btn not found in content")

# 2. Add modals before script tag
modals_html = """
<!-- SAVE CALCULATION SNAPSHOT MODAL -->
<div id="tools-save-modal" class="modal-dialog-backdrop" hidden>
    <div class="modal-dialog-container tools-save-dialog" role="dialog" aria-modal="true" aria-labelledby="save-calc-modal-title">

        <div class="modal-dialog-header">
            <div class="modal-header-text">
                <div class="panel-heading-icon tools-icon-save modal-icon">
                    <svg class="ui-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                        <polyline points="17 21 17 13 7 13 7 21"></polyline>
                        <polyline points="7 3 7 8 15 8"></polyline>
                    </svg>
                </div>
                <div>
                    <h3 id="save-calc-modal-title">Save Calculation Snapshot</h3>
                    <p>Persist all active pond computational parameters into your MySQL database records.</p>
                </div>
            </div>
            <button type="button" id="close-save-modal" class="modal-close-btn" aria-label="Close dialog">
                &times;
            </button>
        </div>

        <div class="modal-dialog-body tools-save-modal-body">
            <div class="tools-modal-field">
                <label for="save-calc-notes" class="tools-modal-label">
                    <span>Pond Identifier / Run Notes:</span>
                    <span class="tools-modal-hint">(Optional reference note, e.g., Pond 1 - DOC 45 Sampling)</span>
                </label>
                <input type="text" id="save-calc-notes" class="tools-modal-input" placeholder="e.g. Pond 1 - DOC 45 Sampling" maxlength="200">
            </div>

            <div class="tools-save-summary-card">
                <span class="save-summary-title">SNAPSHOT OVERVIEW TO BE RECORDED:</span>
                <div class="save-summary-grid">
                    <div class="save-summary-item">
                        <span class="summary-label">Standing Biomass:</span>
                        <span id="save-preview-biomass" class="summary-val">-- kg</span>
                    </div>
                    <div class="save-summary-item">
                        <span class="summary-label">Daily Adjusted Feed:</span>
                        <span id="save-preview-feed" class="summary-val">-- kg/day</span>
                    </div>
                    <div class="save-summary-item">
                        <span class="summary-label">Survival Rate (Eq. 1):</span>
                        <span id="save-preview-sr" class="summary-val">-- %</span>
                    </div>
                    <div class="save-summary-item">
                        <span class="summary-label">Final ABW (Eq. 2):</span>
                        <span id="save-preview-fabw" class="summary-val">-- g</span>
                    </div>
                    <div class="save-summary-item">
                        <span class="summary-label">ADWG (Eq. 3):</span>
                        <span id="save-preview-adwg" class="summary-val">-- g/day</span>
                    </div>
                    <div class="save-summary-item">
                        <span class="summary-label">SGR (Eq. 4):</span>
                        <span id="save-preview-sgr" class="summary-val">-- %/day</span>
                    </div>
                    <div class="save-summary-item">
                        <span class="summary-label">Feed Conversion (Eq. 7):</span>
                        <span id="save-preview-fcr" class="summary-val">--</span>
                    </div>
                    <div class="save-summary-item">
                        <span class="summary-label">Fulton's K Factor (Eq. 8):</span>
                        <span id="save-preview-k" class="summary-val">--</span>
                    </div>
                    <div class="save-summary-item">
                        <span class="summary-label">Liming Buffer:</span>
                        <span id="save-preview-lime" class="summary-val">-- kg</span>
                    </div>
                    <div class="save-summary-item">
                        <span class="summary-label">Carbon Dosing:</span>
                        <span id="save-preview-carbon" class="summary-val">-- kg</span>
                    </div>
                    <div class="save-summary-item">
                        <span class="summary-label">Aerator Power:</span>
                        <span id="save-preview-aeration" class="summary-val">-- HP</span>
                    </div>
                    <div class="save-summary-item">
                        <span class="summary-label">Unionized NH₃:</span>
                        <span id="save-preview-nh3" class="summary-val">-- ppm</span>
                    </div>
                </div>
            </div>

            <div id="save-calc-status-message" class="save-status-msg" hidden></div>
        </div>

        <div class="modal-dialog-footer">
            <button type="button" id="cancel-save-modal-btn" class="tools-btn-secondary">
                Cancel
            </button>
            <button type="button" id="confirm-save-modal-btn" class="tools-btn-save-confirm">
                <svg class="ui-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <span>Confirm &amp; Save to Database</span>
            </button>
        </div>

    </div>
</div>


<!-- EXPORT AQUACULTURE CALCULATIONS MODAL -->
<div id="tools-export-modal" class="modal-dialog-backdrop" hidden>
    <div class="modal-dialog-container tools-export-dialog" role="dialog" aria-modal="true" aria-labelledby="tools-export-title">

        <div class="modal-dialog-header">
            <div class="modal-header-text">
                <div class="panel-heading-icon export-modal-icon">
                    <svg class="ui-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 3v12"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <path d="M5 17v4h14v-4"></path>
                    </svg>
                </div>
                <div>
                    <h3 id="tools-export-title">Export Aquaculture Calculations</h3>
                    <p>Customize specific data categories, select records scope, and choose file format.</p>
                </div>
            </div>
            <button type="button" id="close-tools-export-modal" class="modal-close-btn" aria-label="Close export dialog">
                &times;
            </button>
        </div>

        <div class="modal-dialog-body export-modal-body">

            <!-- 1. SELECT DATA CATEGORIES -->
            <div class="export-modal-section">
                <div class="export-section-header">
                    <label class="export-section-label">
                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-calculator"></use></svg>
                        <span>1. Choose Calculation Data to Export</span>
                    </label>
                    <div class="export-quick-selects">
                        <button type="button" id="export-cat-select-all" class="export-pill-btn">Select All (7)</button>
                        <button type="button" id="export-cat-clear-all" class="export-pill-btn">Clear All</button>
                    </div>
                </div>

                <div class="tools-export-categories-grid">
                    <!-- Category 1: Biomass -->
                    <label class="category-checkbox-card" id="card-cat-biomass">
                        <input type="checkbox" name="export-category" value="biomass" checked>
                        <div class="cat-card-body">
                            <div class="cat-card-header">
                                <span class="cat-card-title">Estimated Standing Biomass</span>
                                <span class="cat-badge">Biomass</span>
                            </div>
                            <p class="cat-card-desc">Pond area, depth, density, survival rate, ABW, active count, biomass (kg &amp; tons).</p>
                        </div>
                    </label>

                    <!-- Category 2: Temp Feed -->
                    <label class="category-checkbox-card" id="card-cat-temp-feed">
                        <input type="checkbox" name="export-category" value="temp_feed" checked>
                        <div class="cat-card-body">
                            <div class="cat-card-header">
                                <span class="cat-card-title">Temperature Feeding Adjustment</span>
                                <span class="cat-badge">Feeding</span>
                            </div>
                            <p class="cat-card-desc">Water temp, base feed %, temp multiplier, adjusted feed kg/day, meal division.</p>
                        </div>
                    </label>

                    <!-- Category 3: Growth Equations -->
                    <label class="category-checkbox-card" id="card-cat-growth">
                        <input type="checkbox" name="export-category" value="growth" checked>
                        <div class="cat-card-body">
                            <div class="cat-card-header">
                                <span class="cat-card-title">Eight Equations (Eqs. 1–8)</span>
                                <span class="cat-badge">Growth &amp; FCR</span>
                            </div>
                            <p class="cat-card-desc">SR%, mortality, FABW, count/kg, ADWG, SGR, Initial/Final Biomass, FCR, Fulton's K factor.</p>
                        </div>
                    </label>

                    <!-- Category 4: Liming -->
                    <label class="category-checkbox-card" id="card-cat-lime">
                        <input type="checkbox" name="export-category" value="lime" checked>
                        <div class="cat-card-body">
                            <div class="cat-card-header">
                                <span class="cat-card-title">pH Liming Dosage</span>
                                <span class="cat-badge">Water Quality</span>
                            </div>
                            <p class="cat-card-desc">Pond volume, initial and target pH, neutralizing agent, dosage (kg &amp; ppm).</p>
                        </div>
                    </label>

                    <!-- Category 5: Carbon -->
                    <label class="category-checkbox-card" id="card-cat-carbon">
                        <input type="checkbox" name="export-category" value="carbon" checked>
                        <div class="cat-card-body">
                            <div class="cat-card-header">
                                <span class="cat-card-title">Organic Carbon Dosing</span>
                                <span class="cat-badge">Biofloc C:N</span>
                            </div>
                            <p class="cat-card-desc">Feed application, crude protein %, target C:N ratio, carbon agent, requirement (kg/day).</p>
                        </div>
                    </label>

                    <!-- Category 6: Aeration -->
                    <label class="category-checkbox-card" id="card-cat-aeration">
                        <input type="checkbox" name="export-category" value="aeration" checked>
                        <div class="cat-card-body">
                            <div class="cat-card-header">
                                <span class="cat-card-title">Aerator Power Sizing</span>
                                <span class="cat-badge">DO Demand</span>
                            </div>
                            <p class="cat-card-desc">Biomass, temperature, salinity, target DO, required motor power (HP), paddlewheel units.</p>
                        </div>
                    </label>

                    <!-- Category 7: Ammonia -->
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
                </div>
            </div>

            <!-- 2. DATASET SCOPE & DATE FILTER -->
            <div class="export-modal-section">
                <label class="export-section-label">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-history"></use></svg>
                    <span>2. Select Dataset Scope</span>
                </label>

                <div class="export-scope-toggle-group">
                    <label class="export-radio-card" id="tools-scope-card-saved">
                        <input type="radio" name="tools-export-scope" id="tools-scope-saved" value="saved" checked>
                        <div class="radio-card-content">
                            <span class="radio-card-title">Saved Database Records</span>
                            <span class="radio-card-desc">Export historical snapshots recorded in your database table.</span>
                        </div>
                    </label>

                    <label class="export-radio-card" id="tools-scope-card-current">
                        <input type="radio" name="tools-export-scope" id="tools-scope-current" value="current">
                        <div class="radio-card-content">
                            <span class="radio-card-title">Current Screen Snapshot</span>
                            <span class="radio-card-desc">Export the active calculations currently displayed on this page.</span>
                        </div>
                    </label>
                </div>

                <!-- Date Range for Saved Records -->
                <div class="tools-export-date-box" id="tools-export-date-box">
                    <label class="export-input-sublabel">Filter by Record Date:</label>
                    <div class="tools-date-filter-row">
                        <select id="tools-export-date-range" class="tools-export-select">
                            <option value="all">All Saved Records (Full History)</option>
                            <option value="today">Today's Calculations Only</option>
                            <option value="7d">Last 7 Days</option>
                            <option value="30d">Last 30 Days</option>
                            <option value="custom">Specific Calendar Date...</option>
                        </select>
                        <input type="date" id="tools-export-custom-date" class="export-date-input" style="display:none;" aria-label="Specific calculation date">
                    </div>
                </div>
            </div>

            <!-- 3. FILE FORMAT SELECTION -->
            <div class="export-modal-section">
                <label class="export-section-label">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                    <span>3. Choose File Format</span>
                </label>
                <div class="export-format-toggle-group">
                    <label class="export-format-pill" id="tools-format-card-xlsx">
                        <input type="radio" name="tools-export-format" value="xlsx" checked>
                        <div class="format-pill-content">
                            <span class="format-badge-icon xlsx-badge">XLSX</span>
                            <div class="format-pill-info">
                                <span class="format-title">Microsoft Excel (.xlsx)</span>
                                <span class="format-desc">Structured workbook with formatted columns</span>
                            </div>
                        </div>
                    </label>

                    <label class="export-format-pill" id="tools-format-card-csv">
                        <input type="radio" name="tools-export-format" value="csv">
                        <div class="format-pill-content">
                            <span class="format-badge-icon csv-badge">CSV</span>
                            <div class="format-pill-info">
                                <span class="format-title">Comma-Separated Values (.csv)</span>
                                <span class="format-desc">Universal raw data format for analysis</span>
                            </div>
                        </div>
                    </label>
                </div>
            </div>

            <!-- 4. LIVE PREVIEW BANNER -->
            <div class="export-preview-card" id="tools-export-preview-card">
                <div class="preview-card-icon">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-activity"></use></svg>
                </div>
                <div class="preview-card-info">
                    <div class="preview-card-header">
                        <span class="preview-card-label">EXPORT CONFIGURATION</span>
                        <span id="tools-export-preview-badge" class="preview-badge preview-badge-ready">Ready to Download</span>
                    </div>
                    <p id="tools-export-preview-text" class="preview-card-desc">
                        Exporting all 7 calculation modules &bull; Saved records &bull; Excel (.xlsx)
                    </p>
                </div>
            </div>

        </div>

        <div class="modal-dialog-footer export-modal-footer">
            <button type="button" id="cancel-tools-export-btn" class="export-btn-secondary">
                Cancel
            </button>
            <button type="button" id="confirm-tools-export-btn" class="export-btn-primary">
                <svg class="ui-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 3v12"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <path d="M5 17v4h14v-4"></path>
                </svg>
                <span id="confirm-tools-export-text">Download Excel (.xlsx)</span>
            </button>
        </div>

    </div>
</div>
"""

script_tag = '<script src="{{ url_for(\'static\', filename=\'js/calculators.js\') }}"></script>'
if script_tag in norm_content:
    norm_content = norm_content.replace(script_tag, modals_html + "\n" + script_tag)
    print("Inserted modals before script tag")
else:
    print("ERROR: script tag not found")

with open("templates/calculators.html", "w", encoding="utf-8") as f:
    f.write(norm_content)

print("Saved templates/calculators.html successfully")

