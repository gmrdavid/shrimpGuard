with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

assert "btn-open-growth-chart" in html
assert "btn-open-growth-chart-top" in html
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

print("All template assertions passed! Eqs. 1-4, 6-8 are present and Eq. 5 Initial Biomass is 100% excluded.")
