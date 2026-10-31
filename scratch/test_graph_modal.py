with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

# Verify single performance graph button exists and duplicate is removed
assert "btn-open-growth-chart" in html, "Kept button #btn-open-growth-chart missing!"
assert "btn-open-growth-chart-top" not in html, "Duplicate button #btn-open-growth-chart-top still exists!"

# Verify growth modal exists and Eq 5 is strictly excluded
assert "growth-trend-graph-modal" in html
assert "growth-trend-chart" in html

start_idx = html.find('id="growth-trend-graph-modal"')
end_idx = html.find('<!-- GROWTH EQUATION DETAILS POPUP DIALOG -->', start_idx)
modal_text = html[start_idx:end_idx]

for eq in ["Eq. 1", "Eq. 2", "Eq. 3", "Eq. 4", "Eq. 6", "Eq. 7", "Eq. 8"]:
    assert eq in modal_text, f"Missing {eq} in graph modal!"

assert "Initial Biomass" not in modal_text, "Found Initial Biomass in graph modal!"
assert "Eq. 5" not in modal_text, "Found Eq. 5 in graph modal!"
assert "dot-ib" not in modal_text, "Found dot-ib in graph modal!"

# Verify that under Computed Performance Metrics, detail labels like Mortality, Market Count, etc. are removed
grid_start = html.find('class="growth-metrics-grid"')
grid_end = html.find('<!-- MODAL DIALOGS FOR AQUACULTURE CALCULATORS -->', grid_start)
grid_text = html[grid_start:grid_end]

removed_labels = [
    "Mortality:",
    "Market Count:",
    "Weekly Gain:",
    "Weight Multiplier:",
    "Released:",
    "Net Live Gain:",
    "Feed Efficiency:",
    "Profile:"
]

for label in removed_labels:
    assert label not in grid_text, f"Detail label '{label}' should be removed from cards under Computed Performance Metrics!"

print("All tests in test_graph_modal.py passed successfully!")
