with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Assert legend and summary strip are removed
assert "growth-chart-legend" not in html, "Found growth-chart-legend in template, should be removed!"
assert "growth-graph-summary-strip" not in html, "Found growth-graph-summary-strip in template, should be removed!"
assert "mini-stat-sr" not in html, "Found mini-stat-sr in template, should be removed!"
assert "mini-stat-fabw" not in html, "Found mini-stat-fabw in template, should be removed!"
assert "mini-badge-sr" not in html, "Found mini-badge-sr in template, should be removed!"

print("Assertion 1 Passed: Both growth-chart-legend and mini-stat summary cards below graph are removed.")

# 2. Assert warning and critical badges are present
assert html.count("tools-badge-opt") >= 7, "Expected at least 7 tools-badge-opt"
assert html.count("tools-badge-warn") == 7, f"Expected 7 tools-badge-warn, found {html.count('tools-badge-warn')}"
assert html.count("tools-badge-crit") == 7, f"Expected 7 tools-badge-crit, found {html.count('tools-badge-crit')}"
print("Assertion 2 Passed: All 7 parameters in Action Matrix have optimal, warning, and critical badge styling.")

# 3. Assert CSS contains styles
with open("static/css/style.css", "r", encoding="utf-8") as f:
    css = f.read()

assert ".calculators-page .tools-badge-warn" in css, "Missing .tools-badge-warn in style.css"
assert ".calculators-page .tools-badge-crit" in css, "Missing .tools-badge-crit in style.css"
print("Assertion 3 Passed: style.css contains proper styles for warning and critical badges.")
