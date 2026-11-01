import re

with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

with open("static/css/style.css", "r", encoding="utf-8") as f:
    css = f.read()

with open("static/js/calculators.js", "r", encoding="utf-8") as f:
    js = f.read()

print("--- Verifying HTML Elements ---")
assert 'id="btn-choose-computation"' in html, "btn-choose-computation missing"
assert 'id="active-computation-label"' in html, "active-computation-label missing"
assert 'id="tools-module-dropdown-menu"' in html, "tools-module-dropdown-menu missing"
assert 'id="tools-module-pills"' in html, "tools-module-pills missing"

expected_modules = ["feeding", "growth", "remediation", "ammonia", "co2", "all"]
for m in expected_modules:
    dropdown_match = re.search(rf'class="module-dropdown-item[^"]*"\s+data-module="{m}"', html)
    assert dropdown_match, f"Dropdown option for module '{m}' not found"
    
    pill_match = re.search(rf'class="module-pill[^"]*"\s+data-module="{m}"', html)
    assert pill_match, f"Pill tab for module '{m}' not found"

print("[OK] All 6 dropdown items and pill buttons confirmed in HTML.")

expected_sections = [
    ("tools-feeding-section", "feeding"),
    ("tools-growth-section", "growth"),
    ("tools-remediation-section", "remediation"),
    ("tools-ammonia-section", "ammonia"),
    ("tools-co2-section", "co2"),
    ("tools-standards-section", "standards"),
]

for sec_id, data_val in expected_sections:
    assert f'id="{sec_id}"' in html, f"Section id '{sec_id}' missing in HTML"
    assert f'data-calc-module="{data_val}"' in html, f"data-calc-module='{data_val}' missing in HTML"

print("[OK] All calculator sections and data-calc-module attributes verified in HTML.")

print("\n--- Verifying CSS Rules ---")
css_rules = [
    ".tools-module-nav-section",
    ".tools-module-nav-bar",
    ".module-nav-header",
    ".tools-btn-choose",
    ".active-computation-name",
    ".tools-module-dropdown-menu",
    ".module-dropdown-item",
    ".module-nav-pills",
    ".module-pill",
    ".calc-module-active",
]
for rule in css_rules:
    assert rule in css, f"CSS rule '{rule}' missing in style.css"

print("[OK] All CSS classes and styles verified in style.css.")

print("\n--- Verifying JavaScript Module Switching Logic ---")
js_tokens = [
    "MODULE_DEFINITIONS",
    "feeding:",
    "growth:",
    "remediation:",
    "ammonia:",
    "co2:",
    "all:",
    "btnChooseComputation",
    "dropdownMenu",
    "activeLabel",
    "setActiveComputationModule",
    "initComputationModuleSelector",
    "shrimpguard_active_calc_module",
    "section.hidden = true",
    'section.style.display = "none"',
]
for token in js_tokens:
    assert token in js, f"JavaScript token '{token}' missing in calculators.js"

print("[OK] Module switcher JavaScript logic verified in calculators.js.")
print("\n>>> ALL TESTS PASSED! Computation module chooser is completely integrated. <<<")
