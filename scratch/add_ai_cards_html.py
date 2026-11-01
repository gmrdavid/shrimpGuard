with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

def normalize(s):
    return s.replace("\r\n", "\n")

html_norm = normalize(html)

def make_ai_card(module_name, title_name, default_eval, default_actions):
    actions_li = "\n".join(f"                                        <li>{a}</li>" for a in default_actions)
    return f"""                        <!-- AI DECISION SUPPORT CARD ({module_name.upper()}) -->
                        <div class="tools-ai-card" id="ai-card-{module_name}" data-ai-module="{module_name}">
                            <div class="ai-card-header">
                                <div class="ai-card-title-group">
                                    <div class="ai-sparkle-box">
                                        <svg class="ui-icon ai-sparkle-icon" aria-hidden="true"><use href="#icon-sparkles"></use></svg>
                                    </div>
                                    <div>
                                        <span class="ai-card-eyebrow">AI DECISION SUPPORT</span>
                                        <h4 class="ai-card-title">{title_name}</h4>
                                    </div>
                                </div>
                                <div class="ai-header-actions">
                                    <span id="ai-badge-{module_name}" class="ai-status-pill badge-optimal">Optimal</span>
                                    <button type="button" class="btn-generate-ai-insight" data-module="{module_name}" title="Analyze with Google Gemini AI">
                                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-sparkles"></use></svg>
                                        <span>Analyze with AI</span>
                                    </button>
                                </div>
                            </div>
                            <div class="ai-card-body">
                                <p id="ai-eval-{module_name}" class="ai-eval-text">
                                    {default_eval}
                                </p>
                                <div class="ai-actions-wrap">
                                    <span class="ai-actions-title">RECOMMENDED FIELD ACTIONS:</span>
                                    <ul id="ai-actions-{module_name}" class="ai-actions-list">
{actions_li}
                                    </ul>
                                </div>
                            </div>
                            <div class="ai-card-footer">
                                <span id="ai-source-{module_name}" class="ai-source-stamp">Powered by Google Gemini AI • Penaeus vannamei Engine</span>
                            </div>
                        </div>"""

# 1. Feeding AI Card
feeding_card = make_ai_card(
    "feeding",
    "Gemini Feeding Diagnosis",
    "At optimal culture temperatures (28.0–32.0 °C), Penaeus vannamei gastric evacuation proceeds efficiently within 2 hours. Standing biomass is safely balanced against daily protein ration.",
    [
        "Inspect feeding check trays 1.5–2 hours post-feed; if >10% feed remains, reduce subsequent meal by 20%.",
        "Maintain dissolved oxygen >5.0 mg/L with paddlewheel aeration along peripheral feeding lanes.",
        "Adjust daily feeding percentage following weekly cast-net ABW sampling."
    ]
)

target_feeding = """                        <!-- Feeding Tray Monitoring Tip -->
                        <div class="tools-callout-tip">
                            <svg class="ui-icon" aria-hidden="true">
                                <use href="#icon-lightbulb"></use>
                            </svg>
                            <p id="feed-tray-tip">
                                <strong>Feeding Tray Protocol:</strong> Place 4 feed check trays per 1,000 m² pond area. Check trays 1.5–2 hours after feeding. If &gt;10% feed remains, reduce next feeding by 20% to prevent ammonia spikes.
                            </p>
                        </div>"""

replacement_feeding = f"""{target_feeding}

{feeding_card}"""

assert normalize(target_feeding) in html_norm, "target_feeding not found"
html_norm = html_norm.replace(normalize(target_feeding), normalize(replacement_feeding), 1)

# 2. Growth AI Card
growth_card = make_ai_card(
    "growth",
    "Gemini Zootechnical Evaluation",
    "Zootechnical performance metrics (SR: 85.0%, ADWG: 0.222 g/day, FCR: 1.25, K: 0.85) conform to top-tier commercial intensive culture standards for Penaeus vannamei.",
    [
        "Audit daily feeding rates against weekly ABW growth curve to keep FCR within the 1.1–1.4 target range.",
        "Verify carapace hardness and gut fullness during weekly sampling to detect early molting cycles.",
        "Schedule partial biomass thinning if pond density approaches maximum dissolved oxygen carrying capacity."
    ]
)

target_growth = """                        <!-- Card 8: Fulton's Condition Factor -->
                        <div class="tools-res-card">
                            <div class="res-card-header">
                                <span class="res-card-label">FULTON'S CONDITION FACTOR</span>
                                <span id="gm-res-k-badge" class="wqi-metric-badge badge-optimal">Optimal</span>
                            </div>
                            <div class="res-value-row">
                                <strong id="gm-res-k-val" class="res-big-value">0.9317</strong>
                                <span class="res-unit">K factor</span>
                            </div>
                            
                            <div class="res-card-action-row">
                                <button type="button" class="growth-calc-details-btn" data-eq="8" aria-label="View calculation details for Equation 8">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                                    <span>Formula &amp; Steps</span>
                                </button>
                            </div>
                        </div>

                    </div>
                </div>"""

replacement_growth = f"""{target_growth}

{growth_card}"""

assert normalize(target_growth) in html_norm, "target_growth not found"
html_norm = html_norm.replace(normalize(target_growth), normalize(replacement_growth), 1)

# 3. Remediation AI Card
remediation_card = make_ai_card(
    "remediation",
    "Gemini Remediation Protocol",
    "Water treatment parameters calculate safe buffer reserves and microbial C:N ratio to sequester toxic nitrogen metabolites while maintaining nocturnal oxygen integrity.",
    [
        "Slurry agricultural limestone in pond water and broadcast across paddlewheel aerator wash in the early morning.",
        "Ferment carbon source with probiotic consortium (Bacillus subtilis) for 4 hours before application.",
        "Run paddlewheel aerators continuously throughout nocturnal peak respiration hours (22:00–07:00)."
    ]
)

target_remediation = """                        <div class="treatment-result-box">
                            <span class="res-card-label">RECOMMENDED AERATOR POWER</span>
                            <div class="res-value-row">
                                <strong id="aero-power-hp" class="res-big-value">2.0</strong>
                                <span class="res-unit">HP</span>
                                <span class="res-secondary-val">(<span id="aero-units">1 × 2-HP</span> unit)</span>
                            </div>
                            <p id="aero-instruction" class="treatment-instruction">
                                Minimum 1 HP per 400 kg biomass for vannamei. Run continuously from 22:00 to 07:00 when algae respiration consumes DO.
                            </p>
                        </div>
                    </div>

                    </div>

                </div>"""

replacement_remediation = f"""{target_remediation}

{remediation_card}"""

assert normalize(target_remediation) in html_norm, "target_remediation not found"
html_norm = html_norm.replace(normalize(target_remediation), normalize(replacement_remediation), 1)

# 4. Ammonia AI Card
ammonia_card = make_ai_card(
    "ammonia",
    "Gemini NH₃ Toxicological Diagnosis",
    "Unionized ammonia (NH3) concentration remains below the commercial stress threshold (<0.030 ppm). Gill epithelial osmoregulation and branchial excretion operate unimpaired.",
    [
        "Monitor diurnal pH swings closely; higher afternoon pH significantly amplifies toxic NH3 fraction.",
        "Supplement biofloc carbon source (15:1 C:N ratio) to stimulate heterotrophic uptake of surplus TAN.",
        "Maintain total alkalinity >120 ppm to support continuous autotrophic nitrifying biofilter efficiency."
    ]
)

target_ammonia = """                        <!-- SENSITIVITY CALLOUT -->
                        <div class="ammonia-sensitivity-callout">
                            <svg class="ui-icon" aria-hidden="true">
                                <use href="#icon-lightbulb"></use>
                            </svg>
                            <p id="tools-ammonia-sensitivity">
                                <strong>Sensitivity Insight:</strong> At 28 °C, an increase in pH of only +0.2 (to 7.8) yields <strong>0.0344 ppm</strong>, which exceeds the acceptable limit (&lt;0.03 ppm) and requires immediate aeration &amp; mitigation.
                            </p>
                        </div>"""

replacement_ammonia = f"""{target_ammonia}

{ammonia_card}"""

assert normalize(target_ammonia) in html_norm, "target_ammonia not found"
html_norm = html_norm.replace(normalize(target_ammonia), normalize(replacement_ammonia), 1)

# 5. CO2 AI Card
co2_card = make_ai_card(
    "co2",
    "Gemini Carbonate & CO₂ Diagnosis",
    "Free carbon dioxide concentration is well within the physiological tolerance limit (<10.0 mg/L). Hemocyanin oxygen affinity and branchial gas exchange remain optimal.",
    [
        "Operate mechanical aerators during pre-dawn hours to strip nocturnal CO2 respiration peaks.",
        "Maintain total alkalinity between 120–160 mg/L as CaCO3 to stabilize the carbonate equilibrium.",
        "Inspect phytoplankton bloom density to prevent excessive algal nocturnal carbon dioxide surges."
    ]
)

target_co2 = """                        <!-- SENSITIVITY CALLOUT -->
                        <div class="ammonia-sensitivity-callout">
                            <svg class="ui-icon" aria-hidden="true">
                                <use href="#icon-lightbulb"></use>
                            </svg>
                            <p id="tools-co2-sensitivity">
                                <strong>Diurnal Dynamics Insight:</strong> Free CO₂ reaches peak concentrations just before dawn due to uninterrupted shrimp and plankton respiration during the night, while pH dips to its diurnal trough. Daytime photosynthesis rapidly strips CO₂ and elevates pH.
                            </p>
                        </div>"""

replacement_co2 = f"""{target_co2}

{co2_card}"""

assert normalize(target_co2) in html_norm, "target_co2 not found"
html_norm = html_norm.replace(normalize(target_co2), normalize(replacement_co2), 1)

with open("templates/calculators.html", "w", encoding="utf-8") as f:
    f.write(html_norm)

print("Added AI decision support cards to all 5 calculators in templates/calculators.html successfully!")

