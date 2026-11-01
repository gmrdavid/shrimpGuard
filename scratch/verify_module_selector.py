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
assert 'id="tools-module-pills"' not in html, "Exposed pills container should be removed"
assert 'class="module-pill"' not in html, "Exposed module pill buttons should be removed"

expected_modules = ["feeding", "growth", "remediation", "ammonia", "co2", "all"]
for m in expected_modules:
    dropdown_match = re.search(rf'class="module-dropdown-item[^"]*"\s+data-module="{m}"', html)
    assert dropdown_match, f"Dropdown option for module '{m}' not found"

print("[OK] All 6 dropdown items confirmed in HTML and exposed pill buttons confirmed removed.")

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
    ".calc-module-active",
]
for rule in css_rules:
    assert rule in css, f"CSS rule '{rule}' missing in style.css"

# Verify button color is green in style.css
assert "#16a34a" in css, "Green color #16a34a missing in style.css"
assert "#15803d" in css, "Green shade #15803d missing in style.css"

print("[OK] All CSS classes, green styles, and button aesthetics verified in style.css.")

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
print("\n>>> ALL TESTS PASSED! Dropdown-only button with green aesthetic is active. <<<")
