with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

def normalize(text):
    return text.replace("\r\n", "\n")

html_norm = normalize(html)

# 1. Insert Module Selector Bar between Telemetry Section and Section 1
selector_bar_html = """        <!-- COMPUTATION MODULE SELECTION BAR -->
        <section class="dashboard-section tools-module-nav-section" aria-label="Calculator Module Selection">
            <div class="tools-module-nav-bar">
                <div class="module-nav-header">
                    <span class="module-nav-eyebrow">CHOOSE WHAT TO COMPUTE</span>
                    <h3 class="module-nav-title">Computation Focus</h3>
                </div>

                <div class="module-nav-controls">
                    <!-- Dropdown Trigger Button with active label -->
                    <div class="module-dropdown-wrap" id="tools-module-dropdown-wrap">
                        <button type="button" id="btn-choose-computation" class="tools-btn-choose" aria-haspopup="true" aria-expanded="false" title="Click to choose which calculator module to show">
                            <svg class="ui-icon" aria-hidden="true">
                                <use href="#icon-calculator"></use>
                            </svg>
                            <span class="btn-choose-label">Choose What to Compute:</span>
                            <strong id="active-computation-label" class="active-computation-name">Feeding Management</strong>
                            <svg class="ui-icon chevron-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="6 9 12 15 18 9"></polyline>
                            </svg>
                        </button>

                        <div id="tools-module-dropdown-menu" class="tools-module-dropdown-menu" hidden>
                            <button type="button" class="module-dropdown-item active" data-module="feeding">
                                <div class="item-icon-box tools-icon-biomass">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-shrimp"></use></svg>
                                </div>
                                <div class="item-meta">
                                    <strong>Feeding Management</strong>
                                    <span>Pond population, standing biomass &amp; feed sizing</span>
                                </div>
                                <span class="active-check">✓</span>
                            </button>

                            <button type="button" class="module-dropdown-item" data-module="growth">
                                <div class="item-icon-box tools-icon-biomass">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                </div>
                                <div class="item-meta">
                                    <strong>Growth Performance</strong>
                                    <span>Survival rate, FCR, ADWG, SGR &amp; Fulton's K</span>
                                </div>
                                <span class="active-check">✓</span>
                            </button>

                            <button type="button" class="module-dropdown-item" data-module="remediation">
                                <div class="item-icon-box tools-icon-remediation">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                                </div>
                                <div class="item-meta">
                                    <strong>Water Remediation</strong>
                                    <span>Liming buffer, biofloc carbon &amp; aerator HP</span>
                                </div>
                                <span class="active-check">✓</span>
                            </button>

                            <button type="button" class="module-dropdown-item" data-module="ammonia">
                                <div class="item-icon-box ammonia-heading-icon">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                                </div>
                                <div class="item-meta">
                                    <strong>Unionized Ammonia Toxicity</strong>
                                    <span>Toxic NH₃ fraction &amp; Van Wyk reference matrix</span>
                                </div>
                                <span class="active-check">✓</span>
                            </button>

                            <button type="button" class="module-dropdown-item" data-module="co2">
                                <div class="item-icon-box co2-heading-icon">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-activity"></use></svg>
                                </div>
                                <div class="item-meta">
                                    <strong>Carbon Dioxide</strong>
                                    <span>Tucker (1984) free CO₂ &amp; carbonate equilibrium</span>
                                </div>
                                <span class="active-check">✓</span>
                            </button>

                            <div class="module-dropdown-divider"></div>

                            <button type="button" class="module-dropdown-item" data-module="all">
                                <div class="item-icon-box all-tools-icon">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-calculator"></use></svg>
                                </div>
                                <div class="item-meta">
                                    <strong>Show All Modules</strong>
                                    <span>Display all 5 computational tools together</span>
                                </div>
                                <span class="active-check">✓</span>
                            </button>
                        </div>
                    </div>

                    <!-- Quick Segmented Pill Tabs for 1-click switching -->
                    <div class="module-nav-pills" id="tools-module-pills" role="tablist" aria-label="Calculation Modules">
                        <button type="button" class="module-pill active" data-module="feeding" role="tab" aria-selected="true">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-shrimp"></use></svg>
                            <span>Feeding Management</span>
                        </button>
                        <button type="button" class="module-pill" data-module="growth" role="tab" aria-selected="false">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                            <span>Growth Performance</span>
                        </button>
                        <button type="button" class="module-pill" data-module="remediation" role="tab" aria-selected="false">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                            <span>Water Remediation</span>
                        </button>
                        <button type="button" class="module-pill" data-module="ammonia" role="tab" aria-selected="false">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                            <span>Unionized Ammonia</span>
                        </button>
                        <button type="button" class="module-pill" data-module="co2" role="tab" aria-selected="false">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-activity"></use></svg>
                            <span>Carbon Dioxide</span>
                        </button>
                        <button type="button" class="module-pill pill-all" data-module="all" role="tab" aria-selected="false">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-calculator"></use></svg>
                            <span>Show All</span>
                        </button>
                    </div>
                </div>
            </div>
        </section>"""

target_before_s1 = """        </section>


        <!-- 1. BIOMASS & FEEDING ESTIMATOR -->
        <section class="dashboard-section" aria-labelledby="biomass-calculator-title">"""

replacement_before_s1 = f"""        </section>


{selector_bar_html}


        <!-- 1. BIOMASS & FEEDING ESTIMATOR -->
        <section class="dashboard-section" id="tools-feeding-section" data-calc-module="feeding" aria-labelledby="biomass-calculator-title">"""

assert normalize(target_before_s1) in html_norm, "target_before_s1 not found"
html_norm = html_norm.replace(normalize(target_before_s1), normalize(replacement_before_s1), 1)

# 2. Tag Section 2 (Growth)
target_s2 = """<!-- 2. SHRIMP GROWTH & PERFORMANCE MASTER EQUATIONS (EQS. 1-8) -->
        <section class="dashboard-section" id="tools-growth-section" aria-labelledby="tools-growth-title">"""
replacement_s2 = """<!-- 2. SHRIMP GROWTH & PERFORMANCE MASTER EQUATIONS (EQS. 1-8) -->
        <section class="dashboard-section" id="tools-growth-section" data-calc-module="growth" aria-labelledby="tools-growth-title">"""
assert normalize(target_s2) in html_norm, "target_s2 not found"
html_norm = html_norm.replace(normalize(target_s2), normalize(replacement_s2), 1)

# 3. Tag Section 3 (Remediation)
target_s3 = """<!-- 3. WATER TREATMENT & DOSING CALCULATORS -->
        <section class="dashboard-section" id="tools-remediation-section" aria-labelledby="treatment-calculators-title">"""
replacement_s3 = """<!-- 3. WATER TREATMENT & DOSING CALCULATORS -->
        <section class="dashboard-section" id="tools-remediation-section" data-calc-module="remediation" aria-labelledby="treatment-calculators-title">"""
assert normalize(target_s3) in html_norm, "target_s3 not found"
html_norm = html_norm.replace(normalize(target_s3), normalize(replacement_s3), 1)

# 4. Tag Section 4 (Ammonia)
target_s4 = """<!-- 4. UNIONIZED AMMONIA (NH3) CALCULATOR & VAN WYK MATRIX -->
        <section class="dashboard-section" id="tools-ammonia-section" aria-labelledby="tools-ammonia-title">"""
replacement_s4 = """<!-- 4. UNIONIZED AMMONIA (NH3) CALCULATOR & VAN WYK MATRIX -->
        <section class="dashboard-section" id="tools-ammonia-section" data-calc-module="ammonia" aria-labelledby="tools-ammonia-title">"""
assert normalize(target_s4) in html_norm, "target_s4 not found"
html_norm = html_norm.replace(normalize(target_s4), normalize(replacement_s4), 1)

# 5. Tag Section 5 (CO2)
target_s5 = """<!-- 5. FREE CARBON DIOXIDE (CO2) ESTIMATION & TUCKER MATRIX -->
        <section class="dashboard-section" id="tools-co2-section" aria-labelledby="tools-co2-heading">"""
replacement_s5 = """<!-- 5. FREE CARBON DIOXIDE (CO2) ESTIMATION & TUCKER MATRIX -->
        <section class="dashboard-section" id="tools-co2-section" data-calc-module="co2" aria-labelledby="tools-co2-heading">"""
assert normalize(target_s5) in html_norm, "target_s5 not found"
html_norm = html_norm.replace(normalize(target_s5), normalize(replacement_s5), 1)

# 6. Tag Section 6 (Standards)
target_s6 = """<!-- 6. PENAEUS VANNAMEI SPECIES WATER QUALITY STANDARDS & PROTOCOLS -->
        <section class="dashboard-section" aria-labelledby="standards-heading">"""
replacement_s6 = """<!-- 6. PENAEUS VANNAMEI SPECIES WATER QUALITY STANDARDS & PROTOCOLS -->
        <section class="dashboard-section" id="tools-standards-section" data-calc-module="standards" aria-labelledby="standards-heading">"""
assert normalize(target_s6) in html_norm, "target_s6 not found"
html_norm = html_norm.replace(normalize(target_s6), normalize(replacement_s6), 1)

with open("templates/calculators.html", "w", encoding="utf-8") as f:
    f.write(html_norm)

print("Updated templates/calculators.html with module selector bar and section IDs!")

