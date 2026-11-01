with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

with open("static/css/style.css", "r", encoding="utf-8") as f:
    css = f.read()

with open("static/js/calculators.js", "r", encoding="utf-8") as f:
    js = f.read()

print("--- Verifying HTML Elements ---")
assert 'id="btn-analyze-with-ai"' in html, "btn-analyze-with-ai missing in HTML"
assert 'id="ai-decision-modal"' in html, "ai-decision-modal missing in HTML"
assert 'id="ai-modal-badge"' in html, "ai-modal-badge missing in HTML"
assert 'id="ai-modal-focus-name"' in html, "ai-modal-focus-name missing in HTML"
assert 'id="ai-modal-temp-val"' in html, "ai-modal-temp-val missing in HTML"
assert 'id="ai-modal-key-metric"' in html, "ai-modal-key-metric missing in HTML"
assert 'id="ai-modal-eval-text"' in html, "ai-modal-eval-text missing in HTML"
assert 'id="ai-modal-actions-list"' in html, "ai-modal-actions-list missing in HTML"
assert 'id="btn-reanalyze-ai"' in html, "btn-reanalyze-ai missing in HTML"
assert 'id="close-ai-modal"' in html, "close-ai-modal missing in HTML"
assert 'id="close-ai-modal-action"' in html, "close-ai-modal-action missing in HTML"

# Ensure NO inline tools-ai-card elements remain in templates/calculators.html
assert 'class="tools-ai-card"' not in html, "Inline tools-ai-card should not exist in calculators.html"

print("[OK] HTML button and popup modal confirmed in calculators.html.")

print("\n--- Verifying CSS Rules ---")
css_rules = [
    ".tools-btn-ai-analyze",
    ".ai-decision-dialog",
    ".ai-modal-context-bar",
    ".ai-modal-eval-card",
    ".ai-modal-actions-card",
    ".btn-ai-reanalyze",
    ".ai-modal-footer",
]
for rule in css_rules:
    assert rule in css, f"CSS rule '{rule}' missing in style.css"

print("[OK] CSS rules confirmed in style.css.")

print("\n--- Verifying JavaScript Hooks ---")
js_hooks = [
    "aiDecisionModal",
    "openAiDecisionModal",
    "closeAiDecisionModal",
    "executeAiDecisionAnalysis",
    "initAiModalListeners",
    "btnAnalyzeWithAi",
    "btnReanalyzeAi",
]
for hook in js_hooks:
    assert hook in js, f"JS hook '{hook}' missing in calculators.js"

print("[OK] JS functions and modal event handlers confirmed in calculators.js.")
print("\n>>> ALL TESTS PASSED! Clean Analyze with AI button and popup modal dialog are active. <<<")

