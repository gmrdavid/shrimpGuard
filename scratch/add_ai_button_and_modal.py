with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

def normalize(s):
    return s.replace("\r\n", "\n")

html_norm = normalize(html)

# 1. Add "Analyze with AI" button next to dropdown trigger
target_nav_controls = """                    <!-- Dropdown Trigger Button with active label -->
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

                        <div id="tools-module-dropdown-menu" class="tools-module-dropdown-menu" hidden>"""

replacement_nav_controls = """                    <!-- Dropdown Trigger Button with active label -->
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

                        <div id="tools-module-dropdown-menu" class="tools-module-dropdown-menu" hidden>"""

# Add the button right after the module-dropdown-wrap closing </div>
target_after_dropdown = """                            <button type="button" class="module-dropdown-item" data-module="all">
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


                </div>"""

btn_ai_markup = """                            <button type="button" class="module-dropdown-item" data-module="all">
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

                    <!-- ANALYZE WITH AI BUTTON -->
                    <button type="button" id="btn-analyze-with-ai" class="tools-btn-ai-analyze" title="Run Gemini AI Decision Support on the active computation module">
                        <svg class="ui-icon" aria-hidden="true">
                            <use href="#icon-sparkles"></use>
                        </svg>
                        <span>Analyze with AI</span>
                    </button>

                </div>"""

assert normalize(target_after_dropdown) in html_norm, "target_after_dropdown not found"
html_norm = html_norm.replace(normalize(target_after_dropdown), normalize(btn_ai_markup), 1)

# 2. Add AI Decision Support Modal right before <script src=".../calculators.js">
modal_markup = """<!-- AI DECISION SUPPORT POPUP DIALOG -->
<div id="ai-decision-modal" class="modal-dialog-backdrop" hidden>
    <div class="modal-dialog-container ai-decision-dialog" role="dialog" aria-modal="true" aria-labelledby="ai-modal-title">

        <div class="modal-dialog-header">
            <div class="modal-header-text">
                <div class="panel-heading-icon tools-icon-biomass modal-icon ai-modal-icon">
                    <svg class="ui-icon" aria-hidden="true">
                        <use href="#icon-sparkles"></use>
                    </svg>
                </div>
                <div>
                    <span class="modal-eyebrow">GOOGLE GEMINI AI DECISION SUPPORT</span>
                    <h3 id="ai-modal-title">Penaeus vannamei Biological Diagnosis</h3>
                    <p id="ai-modal-subtitle">Real-time physiological evaluation &amp; operational directives</p>
                </div>
            </div>
            <div class="modal-header-actions-group">
                <span id="ai-modal-badge" class="ai-status-pill badge-optimal">Optimal</span>
                <button type="button" id="close-ai-modal" class="modal-close-btn" aria-label="Close dialog">
                    &times;
                </button>
            </div>
        </div>

        <div class="modal-dialog-body ai-modal-body">
            <!-- Context Summary Pill Bar -->
            <div class="ai-modal-context-bar" id="ai-modal-context-bar">
                <div class="context-item">
                    <span class="context-label">COMPUTATION FOCUS</span>
                    <strong id="ai-modal-focus-name">Feeding Management</strong>
                </div>
                <div class="context-item">
                    <span class="context-label">WATER TEMPERATURE</span>
                    <strong id="ai-modal-temp-val">29.5 °C</strong>
                </div>
                <div class="context-item">
                    <span class="context-label">KEY PARAMETERS</span>
                    <strong id="ai-modal-key-metric">24.5 kg/day (765 kg Biomass)</strong>
                </div>
            </div>

            <!-- Biological Diagnosis Card -->
            <div class="ai-modal-section">
                <div class="ai-modal-section-title-row">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-activity"></use></svg>
                    <span class="ai-modal-section-title">BIOLOGICAL DIAGNOSIS &amp; PHYSIOLOGICAL EVALUATION</span>
                </div>
                <div class="ai-modal-eval-card">
                    <p id="ai-modal-eval-text" class="ai-modal-eval-content">
                        <!-- Dynamic content from Gemini API -->
                    </p>
                </div>
            </div>

            <!-- Actionable Directives Card -->
            <div class="ai-modal-section">
                <div class="ai-modal-section-title-row">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                    <span class="ai-modal-section-title">ACTIONABLE OPERATIONAL DIRECTIVES</span>
                </div>
                <div class="ai-modal-actions-card">
                    <ul id="ai-modal-actions-list" class="ai-modal-actions-list">
                        <!-- Action items list -->
                    </ul>
                </div>
            </div>
        </div>

        <div class="modal-dialog-footer ai-modal-footer">
            <span id="ai-modal-source-stamp" class="ai-source-stamp">
                Powered by Google Gemini AI • Penaeus vannamei Engine
            </span>
            <div class="ai-modal-footer-btns">
                <button type="button" id="btn-reanalyze-ai" class="btn-ai-reanalyze">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-sparkles"></use></svg>
                    <span>Re-analyze</span>
                </button>
                <button type="button" id="close-ai-modal-action" class="modal-dialog-btn btn-secondary">
                    Close
                </button>
            </div>
        </div>

    </div>
</div>

<script src="{{ url_for('static', filename='js/calculators.js') }}"></script>"""

target_script = """<script src="{{ url_for('static', filename='js/calculators.js') }}"></script>"""
assert normalize(target_script) in html_norm, "target_script not found"
html_norm = html_norm.replace(normalize(target_script), normalize(modal_markup), 1)

with open("templates/calculators.html", "w", encoding="utf-8") as f:
    f.write(html_norm)

print("Added Analyze with AI button and AI Decision Support popup modal successfully!")

