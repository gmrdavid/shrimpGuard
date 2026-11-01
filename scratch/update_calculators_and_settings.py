with open("templates/calculators.html", "r", encoding="utf-8") as f:
    calc_html = f.read()

def normalize(text):
    return text.replace("\r\n", "\n")

calc_norm = normalize(calc_html)

# 1. Update Water Remediation structure in templates/calculators.html
old_remediation_section = """<!-- 3. WATER TREATMENT & DOSING CALCULATORS -->
        <section class="dashboard-section" aria-labelledby="treatment-calculators-title">

            <div class="section-heading-row">
                <div>
                    <h2 id="treatment-calculators-title">WATER REMEDIATION</h2>
                </div>
                <span class="section-count">3 remediation tools</span>
            </div>

            <div class="tools-treatment-grid">

                <!-- TOOL A: AGRICULTURAL LIME (CaCO3 / DOLOMITE) -->
                <article class="panel dashboard-panel treatment-card">"""

new_remediation_section = """<!-- 3. WATER TREATMENT & DOSING CALCULATORS -->
        <section class="dashboard-section" id="tools-remediation-section" aria-labelledby="treatment-calculators-title">

            <article class="panel dashboard-panel tools-calc-panel remediation-main-panel">

                <div class="panel-heading">
                    <div class="panel-heading-icon tools-icon-remediation">
                        <svg class="ui-icon" aria-hidden="true">
                            <use href="#icon-droplet"></use>
                        </svg>
                    </div>
                    <div>
                        <h2 id="treatment-calculators-title">Water Remediation</h2>
                        <p>Chemical and biological dosing protocols for alkalinity buffering, heterotrophic TAN assimilation, and continuous DO aeration.</p>
                    </div>
                </div>

                <div class="tools-treatment-grid">

                    <!-- TOOL A: AGRICULTURAL LIME (CaCO3 / DOLOMITE) -->
                    <div class="treatment-card">"""

assert normalize(old_remediation_section) in calc_norm, "old_remediation_section not found"
calc_norm = calc_norm.replace(normalize(old_remediation_section), normalize(new_remediation_section), 1)

# Tool A end to Tool B start
old_card_a_b = """                    </div>

                </article>


                <!-- TOOL B: BIOFLOC ORGANIC CARBON (MOLASSES) DOSING -->
                <article class="panel dashboard-panel treatment-card">"""

new_card_a_b = """                    </div>

                    </div>


                    <!-- TOOL B: BIOFLOC ORGANIC CARBON (MOLASSES) DOSING -->
                    <div class="treatment-card">"""

assert normalize(old_card_a_b) in calc_norm, "old_card_a_b not found"
calc_norm = calc_norm.replace(normalize(old_card_a_b), normalize(new_card_a_b), 1)

# Tool B end to Tool C start
old_card_b_c = """                    </div>

                </article>


                <!-- TOOL C: AERATOR HORSEPOWER & CAPACITY ESTIMATOR -->
                <article class="panel dashboard-panel treatment-card">"""

new_card_b_c = """                    </div>

                    </div>


                    <!-- TOOL C: AERATOR HORSEPOWER & CAPACITY ESTIMATOR -->
                    <div class="treatment-card">"""

assert normalize(old_card_b_c) in calc_norm, "old_card_b_c not found"
calc_norm = calc_norm.replace(normalize(old_card_b_c), normalize(new_card_b_c), 1)

# Tool C end and section end
old_remediation_end = """                        </div>
                    </div>

                </article>

            </div>

        </section>"""

new_remediation_end = """                        </div>
                    </div>

                    </div>

                </div>

            </article>

        </section>"""

assert normalize(old_remediation_end) in calc_norm, "old_remediation_end not found"
calc_norm = calc_norm.replace(normalize(old_remediation_end), normalize(new_remediation_end), 1)

with open("templates/calculators.html", "w", encoding="utf-8") as f:
    f.write(calc_norm)

print("Updated templates/calculators.html successfully!")


# 2. Update static/js/calculators.js for Van Wyk Intersection Indicator
with open("static/js/calculators.js", "r", encoding="utf-8") as f:
    calc_js = f.read()

js_norm = normalize(calc_js)

old_highlight_vanwyk = """    function highlightVanWykMatrix(temp, ph) {
        // Find closest grid column
        let closestTemp = VAN_WYK_TEMPS[0];
        let minDiffT = Math.abs(temp - closestTemp);
        VAN_WYK_TEMPS.forEach(t => {
            const diff = Math.abs(temp - t);
            if (diff < minDiffT) {
                minDiffT = diff;
                closestTemp = t;
            }
        });

        // Find closest grid row
        let closestPh = VAN_WYK_PHS[0];
        let minDiffP = Math.abs(ph - closestPh);
        VAN_WYK_PHS.forEach(p => {
            const diff = Math.abs(ph - p);
            if (diff < minDiffP) {
                minDiffP = diff;
                closestPh = p;
            }
        });

        const matrix = document.getElementById("tools-van-wyk-matrix");
        if (!matrix) return;

        // Reset highlights
        matrix.querySelectorAll("td, th").forEach(cell => {
            cell.classList.remove("cell-highlight-col", "cell-highlight-row", "cell-highlight-intersect");
        });

        // Highlight header col
        const thCol = matrix.querySelector(`th[data-temp="${closestTemp}"]`);
        if (thCol) thCol.classList.add("cell-highlight-col");

        // Highlight row
        const trRow = matrix.querySelector(`tr[data-ph="${closestPh.toFixed(1)}"]`);
        if (trRow) {
            trRow.querySelectorAll("td").forEach(td => td.classList.add("cell-highlight-row"));
            const targetCell = trRow.querySelector(`td[data-temp="${closestTemp}"]`);
            if (targetCell) {
                targetCell.classList.remove("cell-highlight-row", "cell-highlight-col");
                targetCell.classList.add("cell-highlight-intersect");
            }
        }
    }"""

new_highlight_vanwyk = """    function highlightVanWykMatrix(temp, ph) {
        // Find closest grid column
        let closestTemp = VAN_WYK_TEMPS[0];
        let minDiffT = Math.abs(temp - closestTemp);
        VAN_WYK_TEMPS.forEach(t => {
            const diff = Math.abs(temp - t);
            if (diff < minDiffT) {
                minDiffT = diff;
                closestTemp = t;
            }
        });

        // Find closest grid row
        let closestPh = VAN_WYK_PHS[0];
        let minDiffP = Math.abs(ph - closestPh);
        VAN_WYK_PHS.forEach(p => {
            const diff = Math.abs(ph - p);
            if (diff < minDiffP) {
                minDiffP = diff;
                closestPh = p;
            }
        });

        const matrix = document.getElementById("tools-van-wyk-matrix");
        if (!matrix) return;

        // Reset highlights
        matrix.querySelectorAll("td, th").forEach(cell => {
            cell.classList.remove("cell-highlight-col", "cell-highlight-row", "cell-highlight-intersect", "active-col-cell", "active-col-header", "active-intersect-cell");
        });
        matrix.querySelectorAll("tr").forEach(tr => tr.classList.remove("active-row"));

        // Highlight header col
        const thCol = matrix.querySelector(`th[data-temp="${closestTemp}"]`);
        if (thCol) {
            thCol.classList.add("cell-highlight-col", "active-col-header");
        }

        // Highlight col cells in body
        matrix.querySelectorAll(`tbody td[data-temp="${closestTemp}"]`).forEach(td => {
            td.classList.add("cell-highlight-col", "active-col-cell");
        });

        // Highlight row
        const trRow = matrix.querySelector(`tr[data-ph="${closestPh.toFixed(1)}"]`);
        if (trRow) {
            trRow.classList.add("active-row");
            trRow.querySelectorAll("td").forEach(td => td.classList.add("cell-highlight-row"));
            const targetCell = trRow.querySelector(`td[data-temp="${closestTemp}"]`);
            if (targetCell) {
                targetCell.classList.remove("cell-highlight-row", "cell-highlight-col", "active-col-cell");
                targetCell.classList.add("cell-highlight-intersect", "active-intersect-cell");
            }
        }
    }"""

assert normalize(old_highlight_vanwyk) in js_norm, "old_highlight_vanwyk not found"
js_norm = js_norm.replace(normalize(old_highlight_vanwyk), normalize(new_highlight_vanwyk), 1)

with open("static/js/calculators.js", "w", encoding="utf-8") as f:
    f.write(js_norm)

print("Updated static/js/calculators.js successfully!")


# 3. Update templates/settings.html: Profile Information icon
with open("templates/settings.html", "r", encoding="utf-8") as f:
    settings_html = f.read()

settings_norm = normalize(settings_html)

old_profile_icon = """                <div class="panel-heading">
                    <div class="panel-heading-icon profile-heading-icon">
                        <svg class="ui-icon" aria-hidden="true">
                            <use href="#icon-dashboard"></use>
                        </svg>
                    </div>"""

new_profile_icon = """                <div class="panel-heading">
                    <div class="panel-heading-icon profile-heading-icon">
                        <svg class="ui-icon" aria-hidden="true">
                            <use href="#icon-user"></use>
                        </svg>
                    </div>"""

assert normalize(old_profile_icon) in settings_norm, "old_profile_icon not found"
settings_norm = settings_norm.replace(normalize(old_profile_icon), normalize(new_profile_icon), 1)

with open("templates/settings.html", "w", encoding="utf-8") as f:
    f.write(settings_norm)

print("Updated templates/settings.html successfully!")


# 4. Update static/css/style.css:
# - Bigger telemetry readings & smaller buttons
# - Remediation panel icon & treatment card styling
# - Settings grid & panel gap / spacing fixes
with open("static/css/style.css", "r", encoding="utf-8") as f:
    css = f.read()

css_norm = normalize(css)

# A. Bigger telemetry badge and values
old_telemetry_css = """.calculators-page .telemetry-badge {
    display: flex;
    flex-direction: column;
    padding: 8px 14px;
    background: #ffffff;
    border: 1px solid #dcfce7;
    border-radius: 10px;
    min-width: 105px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.calculators-page .telemetry-label {
    font-size: 9.5px;
    font-weight: 750;
    letter-spacing: 0.5px;
    color: #4b5563;
    text-transform: uppercase;
}

.calculators-page .telemetry-value {
    font-size: 16px;
    font-weight: 800;
    color: #111827;
}"""

new_telemetry_css = """.calculators-page .telemetry-badge {
    display: flex;
    flex-direction: column;
    padding: 10px 18px;
    background: #ffffff;
    border: 1px solid #dcfce7;
    border-radius: 12px;
    min-width: 125px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.calculators-page .telemetry-label {
    font-size: 10px;
    font-weight: 750;
    letter-spacing: 0.6px;
    color: #4b5563;
    text-transform: uppercase;
    margin-bottom: 2px;
}

.calculators-page .telemetry-value {
    font-size: 22px;
    font-weight: 850;
    color: #111827;
    line-height: 1.25;
}"""

assert normalize(old_telemetry_css) in css_norm, "old_telemetry_css not found"
css_norm = css_norm.replace(normalize(old_telemetry_css), normalize(new_telemetry_css), 1)

# B. Smaller sync live button
old_sync_btn = """.calculators-page .tools-btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 9px 15px;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 9px;
    color: #1e293b;
    font-size: 12.5px;
    font-weight: 650;
    cursor: pointer;
    transition: all 180ms ease;
}

.calculators-page .tools-btn-secondary:hover {
    background: #f8fafc;
    border-color: #94a3b8;
}

.calculators-page .tools-btn-secondary .ui-icon {
    width: 16px;
    height: 16px;
}"""

new_sync_btn = """.calculators-page .tools-btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 6px 11px;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    color: #1e293b;
    font-size: 11px;
    font-weight: 650;
    cursor: pointer;
    transition: all 180ms ease;
}

.calculators-page .tools-btn-secondary:hover {
    background: #f8fafc;
    border-color: #94a3b8;
}

.calculators-page .tools-btn-secondary .ui-icon {
    width: 13px;
    height: 13px;
}"""

assert normalize(old_sync_btn) in css_norm, "old_sync_btn not found"
css_norm = css_norm.replace(normalize(old_sync_btn), normalize(new_sync_btn), 1)

# C. Smaller save snapshot and export buttons
old_save_export_btns = """.calculators-page .tools-btn-save {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 8px 14px;
    background: #0284c7;
    border: 1px solid #0284c7;
    border-radius: 9px;
    color: #ffffff;
    font-size: 12.5px;
    font-weight: 650;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(2, 132, 199, 0.22);
    transition: all 160ms ease;
}

.calculators-page .tools-btn-save:hover {
    background: #0369a1;
    border-color: #0369a1;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(2, 132, 199, 0.3);
}

.calculators-page .tools-btn-save .ui-icon {
    width: 15px;
    height: 15px;
}

.calculators-page .tools-btn-export {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 8px 14px;
    background: #0f766e;
    border: 1px solid #0f766e;
    border-radius: 9px;
    color: #ffffff;
    font-size: 12.5px;
    font-weight: 650;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(15, 118, 110, 0.22);
    transition: all 160ms ease;
}

.calculators-page .tools-btn-export:hover {
    background: #115e59;
    border-color: #115e59;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(15, 118, 110, 0.3);
}

.calculators-page .tools-btn-export .ui-icon {
    width: 15px;
    height: 15px;
}"""

new_save_export_btns = """.calculators-page .tools-btn-save {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 6px 11px;
    background: #0284c7;
    border: 1px solid #0284c7;
    border-radius: 7px;
    color: #ffffff;
    font-size: 11px;
    font-weight: 650;
    cursor: pointer;
    box-shadow: 0 1px 3px rgba(2, 132, 199, 0.2);
    transition: all 160ms ease;
}

.calculators-page .tools-btn-save:hover {
    background: #0369a1;
    border-color: #0369a1;
    transform: translateY(-1px);
    box-shadow: 0 3px 6px rgba(2, 132, 199, 0.25);
}

.calculators-page .tools-btn-save .ui-icon {
    width: 13px;
    height: 13px;
}

.calculators-page .tools-btn-export {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 6px 11px;
    background: #0f766e;
    border: 1px solid #0f766e;
    border-radius: 7px;
    color: #ffffff;
    font-size: 11px;
    font-weight: 650;
    cursor: pointer;
    box-shadow: 0 1px 3px rgba(15, 118, 110, 0.2);
    transition: all 160ms ease;
}

.calculators-page .tools-btn-export:hover {
    background: #115e59;
    border-color: #115e59;
    transform: translateY(-1px);
    box-shadow: 0 3px 6px rgba(15, 118, 110, 0.25);
}

.calculators-page .tools-btn-export .ui-icon {
    width: 13px;
    height: 13px;
}"""

assert normalize(old_save_export_btns) in css_norm, "old_save_export_btns not found"
css_norm = css_norm.replace(normalize(old_save_export_btns), normalize(new_save_export_btns), 1)

# D. Water Remediation icon and treatment cards
old_treatment_card_css = """.calculators-page .treatment-card {
    padding: 20px;
    display: flex;
    flex-direction: column;
}"""

new_treatment_card_css = """.calculators-page .tools-icon-remediation {
    background: #e0f2fe;
    color: #0369a1;
    border: 1px solid #bae6fd;
}

.calculators-page .treatment-card {
    background: #ffffff;
    border: 1px solid #dce9e1;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
}"""

assert normalize(old_treatment_card_css) in css_norm, "old_treatment_card_css not found"
css_norm = css_norm.replace(normalize(old_treatment_card_css), normalize(new_treatment_card_css), 1)

# E. Settings Grid Spacing and Alignment
old_settings_grid_css = """.settings-page .settings-grid {
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: 24px !important;
    align-items: stretch !important;
}"""

new_settings_grid_css = """.settings-page .settings-grid {
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: 16px !important;
    align-items: start !important;
}

.settings-page .settings-panel .panel-heading {
    margin-bottom: 0 !important;
}

.settings-page .settings-panel-divider {
    height: 1px;
    margin: 12px 0 16px;
    background: #eef2ef;
}"""

assert normalize(old_settings_grid_css) in css_norm, "old_settings_grid_css not found"
css_norm = css_norm.replace(normalize(old_settings_grid_css), normalize(new_settings_grid_css), 1)

# F. Settings intro panel and section spacing tightening
old_settings_intro_css = """.settings-page .settings-intro-panel {
    margin-bottom: 24px;
    padding: 23px 24px 17px;
    border: 1px solid #e0ebe3;
    border-radius: var(--settings-radius);
    background: #fff;
    box-shadow: 0 5px 20px rgba(28, 69, 45, 0.025);
}"""

new_settings_intro_css = """.settings-page .settings-intro-panel {
    margin-bottom: 14px;
    padding: 16px 20px 14px;
    border: 1px solid #e0ebe3;
    border-radius: var(--settings-radius);
    background: #fff;
    box-shadow: 0 5px 20px rgba(28, 69, 45, 0.025);
}"""

if normalize(old_settings_intro_css) in css_norm:
    css_norm = css_norm.replace(normalize(old_settings_intro_css), normalize(new_settings_intro_css), 1)

with open("static/css/style.css", "w", encoding="utf-8") as f:
    f.write(css_norm)

print("Updated static/css/style.css successfully!")

